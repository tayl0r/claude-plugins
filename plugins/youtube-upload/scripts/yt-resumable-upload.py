#!/usr/bin/env python3
"""YouTube resumable upload with persistent session recovery.

Saves upload session URI to a state file so interrupted uploads
can resume from where they left off instead of restarting.
"""

import argparse
import json
import hashlib
import os
import sys
import time

import requests as req
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CONFIG_DIR = os.path.expanduser("~/.config/youtubeuploader")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
STATE_DIR = os.path.join(CONFIG_DIR, "resume_states")


def get_credentials():
    """Get or refresh OAuth credentials."""
    creds = None
    token_path = os.path.join(CONFIG_DIR, "yt_upload_token.json")
    secrets_path = os.path.join(CONFIG_DIR, "client_secrets.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=8082)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def state_file_for(filepath):
    """Get resume state file path for a given video file."""
    os.makedirs(STATE_DIR, exist_ok=True)
    file_hash = hashlib.md5(os.path.abspath(filepath).encode()).hexdigest()[:12]
    return os.path.join(STATE_DIR, f"{file_hash}.json")


def save_state(state_path, resumable_uri, file_path, title, privacy):
    """Save upload state for resume."""
    with open(state_path, "w") as f:
        json.dump({
            "resumable_uri": resumable_uri,
            "file_path": os.path.abspath(file_path),
            "title": title,
            "privacy": privacy,
            "timestamp": time.time(),
        }, f)


def load_state(state_path):
    """Load saved upload state."""
    if not os.path.exists(state_path):
        return None
    with open(state_path) as f:
        state = json.load(f)
    # Expire states older than 24h (Google expires resumable URIs after ~24h)
    if time.time() - state.get("timestamp", 0) > 86400:
        os.remove(state_path)
        return None
    return state


def format_size(bytes_val):
    """Format bytes to human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def format_time(seconds):
    """Format seconds to human readable."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h:.0f}h {m:.0f}m"


def auth_header(creds):
    """Get Authorization header, refreshing if needed."""
    if not creds.valid:
        creds.refresh(Request())
    return {"Authorization": f"Bearer {creds.token}"}


def upload_with_resume(file_path, title, privacy, chunk_size_mb=16):
    """Upload a video with resumable upload support."""
    file_path = os.path.abspath(file_path)
    file_size = os.path.getsize(file_path)
    state_path = state_file_for(file_path)
    chunk_size = chunk_size_mb * 1024 * 1024

    print(f"File: {os.path.basename(file_path)} ({format_size(file_size)})")

    creds = get_credentials()
    bytes_uploaded = 0

    # Check for existing resume state
    state = load_state(state_path)

    if state and state["file_path"] == file_path:
        print("Resuming previous upload...")
        resumable_uri = state["resumable_uri"]

        # Query current upload progress
        resp = req.put(
            resumable_uri,
            headers={**auth_header(creds), "Content-Range": f"bytes */{file_size}"},
        )

        if resp.status_code in (200, 201):
            print("Upload was already completed!")
            os.remove(state_path)
            return
        elif resp.status_code == 308:
            range_header = resp.headers.get("Range", "")
            if range_header:
                bytes_uploaded = int(range_header.split("-")[1]) + 1
                print(f"Resuming from {format_size(bytes_uploaded)} ({bytes_uploaded * 100 / file_size:.1f}%)")
            else:
                bytes_uploaded = 0
                print("Starting from beginning (no bytes confirmed)")
        else:
            print(f"Resume URI expired or invalid (status {resp.status_code}), starting new upload")
            state = None

    if not state:
        # Initiate resumable upload
        body = {
            "snippet": {"title": title, "description": ""},
            "status": {"privacyStatus": privacy},
        }

        resp = req.post(
            "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            headers={
                **auth_header(creds),
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/*",
                "X-Upload-Content-Length": str(file_size),
            },
            json=body,
        )

        if resp.status_code not in (200, 201):
            print(f"Failed to initiate upload: {resp.status_code}")
            print(resp.text)
            sys.exit(1)

        resumable_uri = resp.headers["Location"]
        save_state(state_path, resumable_uri, file_path, title, privacy)
        bytes_uploaded = 0
        print("Upload started")

    # Upload chunks with progress
    start_time = time.time()
    initial_bytes = bytes_uploaded

    with open(file_path, "rb") as f:
        f.seek(bytes_uploaded)
        while bytes_uploaded < file_size:
            chunk_end = min(bytes_uploaded + chunk_size, file_size) - 1
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break

            headers = {
                **auth_header(creds),
                "Content-Range": f"bytes {bytes_uploaded}-{chunk_end}/{file_size}",
                "Content-Type": "video/*",
            }

            deadline = start_time + 86400  # 24h from start
            attempt = 0
            while time.time() < deadline:
                try:
                    resp = req.put(
                        resumable_uri,
                        headers=headers,
                        data=chunk_data,
                        timeout=300,
                    )

                    if resp.status_code in (200, 201):
                        bytes_uploaded = file_size
                        print(f"\nUpload complete!")
                        result = resp.json()
                        video_id = result.get("id", "unknown")
                        print(f"Video ID: {video_id}")
                        print(f"URL: https://youtu.be/{video_id}")
                        os.remove(state_path)
                        return
                    elif resp.status_code == 308:
                        range_header = resp.headers.get("Range", "")
                        if range_header:
                            bytes_uploaded = int(range_header.split("-")[1]) + 1
                        else:
                            bytes_uploaded = chunk_end + 1
                        break
                    elif resp.status_code == 401:
                        creds.refresh(Request())
                        headers.update(auth_header(creds))
                        continue
                    else:
                        wait = min(2 ** attempt, 60)
                        print(f"\nUnexpected status {resp.status_code}: {resp.text}")
                        print(f"Retrying in {wait}s...")
                        time.sleep(wait)
                        attempt += 1
                        continue

                except Exception as e:
                    wait = min(2 ** attempt, 60)
                    print(f"\nConnection error: {e}")
                    print(f"Retrying in {wait}s...")
                    time.sleep(wait)
                    attempt += 1
                    # Re-seek in case we need to resend this chunk
                    f.seek(bytes_uploaded)
                    chunk_data = f.read(chunk_size)
            else:
                print(f"\n24h deadline reached. Run the command again to start a new session.")
                save_state(state_path, resumable_uri, file_path, title, privacy)
                sys.exit(1)

            # Progress display
            elapsed = time.time() - start_time
            bytes_since_start = bytes_uploaded - initial_bytes
            pct = bytes_uploaded * 100 / file_size
            speed = bytes_since_start / elapsed if elapsed > 0 else 0
            remaining = (file_size - bytes_uploaded) / speed if speed > 0 else 0
            print(
                f"\r  {format_size(bytes_uploaded)}/{format_size(file_size)} "
                f"({pct:.1f}%) | {format_size(speed)}/s | ETA: {format_time(remaining)}",
                end="", flush=True,
            )

            # Save state periodically
            save_state(state_path, resumable_uri, file_path, title, privacy)


def main():
    parser = argparse.ArgumentParser(description="Resumable YouTube uploader")
    parser.add_argument("file", help="Video file to upload")
    parser.add_argument("title", help="Video title")
    parser.add_argument("--privacy", default="unlisted", help="Privacy (default: unlisted)")
    parser.add_argument("--chunk-size", type=int, default=16, help="Chunk size in MB (default: 16)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    upload_with_resume(args.file, args.title, args.privacy, args.chunk_size)


if __name__ == "__main__":
    main()
