---
name: youtube-upload
description: Set up and use resumable YouTube uploads from the command line. Use when the user wants to upload videos to YouTube, set up YouTube CLI uploading, or troubleshoot upload issues.
---

# YouTube Resumable Upload

A CLI tool for uploading videos to YouTube with true resume support — survives connection drops, sleep, and process crashes. Shows upload speed and ETA.

## Setup

### Prerequisites

- Python 3.10+
- A Google Cloud project with YouTube Data API v3 enabled
- OAuth client credentials (Desktop app type)

### Installation

```bash
# Create dedicated venv
python3 -m venv ~/.config/youtubeuploader/venv

# Install dependencies
~/.config/youtubeuploader/venv/bin/pip install \
    google-api-python-client google-auth-oauthlib google-auth-httplib2 requests

# Copy the upload script
cp scripts/yt-resumable-upload.py ~/.config/youtubeuploader/yt-resumable-upload.py
```

### Google Cloud Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or use existing)
3. Enable **YouTube Data API v3** under APIs & Services → Library
4. Go to **OAuth consent screen**:
   - Add scopes: `youtube.upload`, `youtube`, `youtubepartner`
   - Add your email as a test user
5. Create **OAuth client ID** (Desktop app) under Credentials
6. Download the JSON and save as `~/.config/youtubeuploader/client_secrets.json`

### First Auth

```bash
caffeinate -i ~/.config/youtubeuploader/venv/bin/python \
    ~/.config/youtubeuploader/yt-resumable-upload.py \
    /path/to/any/video.mp4 "test" --privacy private
```

Complete the OAuth flow in the browser. The token is saved to `~/.config/youtubeuploader/yt_upload_token.json`.

### Justfile Recipe (optional)

Add to your `~/.justfile`:

```just
# YouTube upload with resumable uploads and sleep prevention
yt-upload file title privacy="unlisted":
    caffeinate -i ~/.config/youtubeuploader/venv/bin/python \
        ~/.config/youtubeuploader/yt-resumable-upload.py \
        "{{file}}" "{{title}}" --privacy "{{privacy}}"
```

## Usage

```bash
just yt-upload ./video.mp4 "My Video Title"
```

Or directly:

```bash
caffeinate -i ~/.config/youtubeuploader/venv/bin/python \
    ~/.config/youtubeuploader/yt-resumable-upload.py \
    ./video.mp4 "My Video Title" --privacy unlisted
```

### Options

- `--privacy` — `private`, `unlisted`, or `public` (default: `unlisted`)
- `--chunk-size` — Chunk size in MB (default: 16)

## How Resume Works

- Upload state is saved to `~/.config/youtubeuploader/resume_states/` after each chunk
- If the connection drops, it retries with exponential backoff (up to 60s between attempts)
- If the process dies, run the same command again — it queries Google for bytes received and picks up from there
- Retries continuously for up to 24 hours (Google's resumable session limit)
- `caffeinate -i` prevents macOS idle sleep during upload

## Troubleshooting

- **401 errors**: Token expired — delete `~/.config/youtubeuploader/yt_upload_token.json` and re-auth
- **"Access blocked" during OAuth**: Add your email as a test user in OAuth consent screen, and ensure all 3 scopes are added
- **OAuth redirect fails**: The script uses port 8082 for the callback — make sure nothing else is on that port
