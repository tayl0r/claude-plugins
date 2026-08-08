# Ollama models for Claude Code agent tiers

Research date: 2026-08-07. This doc maps the current Ollama model landscape onto the
two agent tiers this repo pins in plugin agent definitions, plus the main Claude Code
loop. Everything is sourced against Ollama's library/API docs, the model creators'
release material, and Ollama GitHub issues. Facts are marked **verified** (read on a
primary source) or **inferred** (my synthesis from the verified facts). Where sources
conflict or are thin, that is stated plainly.

Context: the user runs Claude Code against Ollama's Anthropic-compatible endpoint
(`ANTHROPIC_BASE_URL`), so no Anthropic inference models are usable. The repo's agents
currently pin `claude-sonnet-4-6` (Tier 1) and `claude-opus-4-8` (Tier 2) in frontmatter;
neither name resolves on Ollama unless aliased (see "Hooking this into the repo").

---

## TL;DR

| Tier | Current pin | Recommended (hosted / Ollama cloud) | Recommended (local, 32–64 GB Mac) |
|---|---|---|---|
| Driver (main loop) | n/a | `deepseek-v4-pro:cloud` (best all-round) or `kimi-k2.7-code:cloud` | `qwen3.6:35b` or `qwen3-coder:30b` |
| Tier 1 (sonnet-tier) — workhorse: PR review, seed reviewers, react-performance | `claude-sonnet-4-6` | `deepseek-v4-flash:cloud` (cheap, 1M ctx, strong tool use) | `qwen3-coder:30b` (first) / `qwen3.6:27b` (second) |
| Tier 2 (opus-tier) — resolver: rubric weighing + adversarial self-check | `claude-opus-4-8` | `deepseek-v4-pro:cloud` (strongest reasoning on Ollama) | `qwen3.6:35b` (only if thinking is actually enabled; see caveats) |

Key judgment calls, summarized:

- **The best model on Ollama is DeepSeek-V4-Pro** (1.6T MoE / 49B active, 1M context) —
  but on Ollama it is **cloud-only** (`deepseek-v4-pro:cloud`). The open weights exist
  (Hugging Face, MIT) but need ~400 GB+ VRAM, i.e. datacenter hardware. Treat it as the
  hosted/API choice for the resolver tier and the driver.
- **The best locally-runnable workhorse is `qwen3-coder:30b`** (19 GB, 256K ctx): a
  dedicated agentic-coding model with first-class Ollama tool support since v0.12.0
  (custom XML renderer/parser) — it is the model Ollama's own Anthropic-compat doc
  recommends for Claude Code. No vision, no thinking mode (usually a plus for tool loops).
- **`qwen3.6:27b`/`:35b`** are the strongest thinking-capable local models (released
  April 2026), but their tool-calling had a string of Ollama bugs (thinking blocks
  swallowing tool calls) that need a recent Ollama (≥ 0.31.2) plus a model re-pull.
- **Avoid for this use case:** `gpt-oss` (strong but single-tool-call-per-turn and a
  history of malformed tool calls on Ollama), and anything 75–87 GB dense
  (`mistral-medium-3.5`, `nemotron-3-super`, `devstral-2`, `qwen3.5:122b`) — they don't
  fit a 64 GB Mac and add nothing over the 30–35B class for agentic work on this budget.

---

## How this maps onto the repo

The plugin agents pin dated Anthropic ids in frontmatter
(`plugins/{dev-flow,dev-flow-worktree,react-performance,better-code-review}/agents/*.md`).
Running against Ollama, the `model` string from frontmatter is sent to `/v1/messages`
as-is, and Ollama looks it up by that name. Two ways to make the tiers resolve:

1. **Aliases (zero repo change, recommended):** create Ollama model aliases matching the
   pinned names, so the installed plugins keep working unchanged:

   ```sh
   ollama pull qwen3-coder:30b
   ollama cp qwen3-coder:30b claude-sonnet-4-6      # Tier 1
   ollama cp deepseek-v4-pro:cloud claude-opus-4-8  # Tier 2 (hosted)
   # or for a fully-local Tier 2:
   ollama cp qwen3.6:35b claude-opus-4-8
   ```
   Aliasing a model name is a documented Ollama feature (`ollama cp`, [docs](https://docs.ollama.com/api/openai-compatibility) "Model management" section — verified).
2. **Edit the frontmatter ids** to the real Ollama model names. Cleaner long-term but
   couples the repo to specific models and bumps plugin versions (per CLAUDE.md rules) —
   a follow-up decision, not part of this research.

Driver-loop env vars (from Ollama's Anthropic-compat doc, verified, and the
[BobbyEncoded walkthrough](https://www.bobbyencoded.com/blog/2026/05/20/run-claude-code-with-local-ollama)):

```sh
export ANTHROPIC_AUTH_TOKEN=ollama            # required but ignored
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_MODEL=qwen3-coder:30b        # or deepseek-v4-pro:cloud
export ANTHROPIC_DEFAULT_HAIKU_MODEL=qwen3-coder:30b   # background tasks
```

---

## Anthropic-compatible endpoint (`/v1/messages`) — what actually works

Verified from [Ollama's Anthropic compatibility docs](https://docs.ollama.com/api/anthropic-compatibility):

**Supported:** messages, streaming, system prompts, multi-turn, vision (base64 images),
tools + tool results, thinking/extended thinking, `stop_sequences`, `temperature`,
`top_p`, `top_k`.

**Unsupported / partial — each has a real consequence for Claude Code:**

- **`tool_choice` — unsupported.** You cannot force or disable a specific tool. Claude
  Code generally doesn't rely on forcing, but the option is simply ignored.
- **Prompt caching (`cache_control`) — unsupported.** Long sessions re-process full
  history every turn; expect slower turns on big contexts.
- **`/v1/messages/count_tokens` — unsupported.** Claude Code's telemetry probes this
  endpoint; on Ollama ≥ 0.15.2 this has caused unresponsive servers / 500s
  ([issue #13949](https://github.com/ollama/ollama/issues/13949)). Workarounds:
  `DISABLE_TELEMETRY=1`, `DISABLE_ERROR_REPORTING=1`,
  `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`.
- **PDF `document` content blocks — unsupported.** Only base64 images.
- **Token counts are approximations** based on the model's tokenizer — cost/limit
  tracking in Claude Code will be off.

**Context window — the big operational gotcha (verified from multiple sources):**

- Ollama's default context is now VRAM-dependent, not a flat 4096: **<24 GiB → 4k,
  24–48 GiB → 32k, ≥48 GiB → 256k**; cloud models default to their max
  ([context-length docs](https://docs.ollama.com/context-length)). On a 32–64 GB Mac
  this is 32k–256k, but the detection is VRAM-based, so check your actual default.
- **Claude Code assumes 200k context regardless** of what Ollama provides, and won't
  auto-compact to match ([issue #15316](https://github.com/ollama/ollama/issues/15316) —
  Anthropic's response is that this is deliberate; set
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW` yourself).
- If you hit it, set `OLLAMA_CONTEXT_LENGTH` (e.g. 64000) at server start
  ([PR #8938](https://github.com/ollama/ollama/pull/8938)). A June-2026 fix
  ([PR #16856](https://github.com/ollama/ollama/pull/16856)) removed a related regression
  where big prompts left only 1 token of generation headroom, surfacing as fake
  "exceeded the 32000 output token maximum" errors.
- **Thinking + tools:** Ollama now defaults thinking **off** when a thinking-capable
  model is used with tools and the client sends no thinking preference
  ([PR #16758](https://github.com/ollama/ollama/pull/16758)). Consequence: reasoning
  models (qwen3.5/3.6, deepseek-v4) may run in non-thinking mode for agent work unless
  Claude Code explicitly sends `thinking`. Verified that the endpoint *accepts* a
  `thinking` field (`budget_tokens` accepted but not enforced), but I could not verify
  from primary sources whether Claude Code currently sends it against a non-Anthropic
  endpoint — **inferred: assume it doesn't by default; test the resolver tier's reasoning
  mode explicitly.**

---

## Tool-calling reliability per candidate (critical for this use case)

Tool calling is the single most important quality for Claude Code agents (many tool calls
per turn). This is the least tidy part of the landscape — every strong candidate except
`qwen3-coder:30b` has had documented Ollama-side tool-calling bugs.

| Model | Tool-calling status on Ollama | Verdict for agent use |
|---|---|---|
| `qwen3-coder:30b` | First-class since Ollama v0.12.0 via custom XML renderer/parser ([#11621](https://github.com/ollama/ollama/issues/11621), [PR #12248](https://github.com/ollama/ollama/pull/12248)). Known edge cases: with 6+ tools it can fall back to XML in content ([goose #6883](https://github.com/aaif-goose/goose/issues/6883)); streaming with 20+ tools has an index bug ([#16212](https://github.com/ollama/ollama/issues/16212)); the base model sometimes omits the opening `<tool_call>` tag ([QwenLM #475](https://github.com/QwenLM/Qwen3-Coder/issues/475)). | **Best.** Default build works for typical agent tool counts. |
| `qwen3.6` / `qwen3.5` | Thinking blocks swallowing tool calls, fixed over several Ollama versions; `think: false` JSON-format bug fixed in v0.31.2 ([#14645](https://github.com/ollama/ollama/issues/14645)); some registry tags shipped the wrong renderer (re-pull fixes, [#14418](https://github.com/ollama/ollama/issues/14418)); tool block without closed think block printed as text ([#14745](https://github.com/ollama/ollama/issues/14745), [PR #15022](https://github.com/ollama/ollama/pull/15022)). | **Good** on recent Ollama; requires re-pull and ≥ 0.31.2. |
| `gpt-oss` (20b/120b) | OpenAI "Harmony" output format strains Ollama's generic parser. One tool call per turn (no parallel), context must be ≥16k or prompts corrupt ([#12187](https://github.com/ollama/ollama/issues/12187)); 500s on malformed JSON ([#11800](https://github.com/ollama/ollama/issues/11800)); malformed tool names fixed in v0.11.4 ([#11704](https://github.com/ollama/ollama/issues/11704)); must round-trip the `thinking` field. | **Avoid** for high-frequency multi-tool agents. |
| `gemma4` (12b/26b/31b) | Native function calling claimed by Google; Ollama tag `tools` present. No notable open bug threads found in my search. | **Good**, especially as a vision-capable option. |
| `deepseek-v4-*:cloud` | Tagged `tools`; agentic benchmarks (Toolathlon, MCPAtlas) cited on the library page. No Ollama bug threads found (cloud-hosted, less community surface). | **Good** (hosted). |
| `kimi-k2.7-code:cloud` | Tagged `tools`; "multi-step tool calling and MCP-based environments" claimed on the page. Cloud-only. | **Good** (hosted). |

---

## Per-model detail

### Qwen family (best overall local coverage)

**`qwen3-coder:30b`** — [Ollama library](https://ollama.com/library/qwen3-coder) (verified)
- MoE, 30B total / 3.3B active. 256K native ctx (up to 1M via extrapolation). Text-only,
  no thinking mode. 19 GB default build; Ollama's Anthropic-compat doc says "at least
  24 GB VRAM to run smoothly." Trained with long-horizon RL on SWE-Bench; the model
  Ollama itself recommends for Claude Code.
- `qwen3-coder:480b` variant: 290 GB build, "minimum 250 GB of memory or unified memory"
  locally, or `qwen3-coder:480b-cloud` (hosted). **Inference:** treat 480b as hosted-only.

**`qwen3.6:27b` / `:35b`** — [Ollama library](https://ollama.com/library/qwen3.6) (verified);
architecture per [DeepResearch Ninja analysis](https://deepresearch.ninja/2026/05/Qwen3.6-27B/35B-A3B-vs-Gemma-4-vs-DeepSeek-V4-A-Comprehensive-Analysis-of-the-Open-Weight-Frontier-May-2026/) (secondary)
- Released April 22, 2026. 256K ctx, vision + tools + thinking. 27b = 17 GB, 35b = 24 GB.
- The 27B is reported dense; the 35B is reported a 35B-A3B MoE (3B active) — **inferred**,
  the Ollama library page does not state dense vs MoE. Secondary analysis claims 99%
  tool-call schema validity and SWE-bench Verified 77.2% for the 27B (better than the
  Qwen3.5-397B flagship) — **secondary source, not verified on a primary one.**

**`qwen3.5`** — [Ollama library](https://ollama.com/library/qwen3.5) (verified)
- Flagship 397B-A17B MoE (cloud: `qwen3.5:397b-cloud`, or `qwen3.5:cloud`). Local tags
  from 0.8b to 122b (81 GB). 256K ctx, vision + tools + thinking. Superseded by 3.6 for
  agentic coding (secondary sources).
- Also on the library: `qwen3-coder-next` (tools; ~80B class per secondary source) and
  `qwen3-next:80b` (tools, thinking). Thin primary-source detail — **flagged**.

**Not on Ollama:** Qwen 3.7-Max launched API-only (not on Ollama) — flagged, secondary
source (Kilo blog).

### DeepSeek family

**`deepseek-v4-pro:cloud`** — [Ollama library](https://ollama.com/library/deepseek-v4-pro),
[DeepSeek HF blog](https://huggingface.co/blog/deepseekv4) (verified)
- MoE 1.6T total / 49B active, 1M ctx, text-only. Three reasoning modes: No thinking,
  Thinking, Max thinking (Max requires ≥384K ctx). Cloud-only on Ollama (no local tag).
- Weights are open on Hugging Face (MIT), but "requires ~400 GB+ VRAM" per secondary
  analysis — datacenter-scale. **This is the strongest reasoning model on Ollama.**

**`deepseek-v4-flash:cloud`** — [Ollama library](https://ollama.com/library/deepseek-v4-flash) (verified)
- MoE 284B total / 13B active (library page shows a 304B badge — an internal
  inconsistency in the page itself, **flagged**). 1M ctx, text-only, three reasoning
  modes. Cloud-only on Ollama. HF blog calls it the efficient member of the family
  (~10% of V3.2's FLOPs); community GGUF quantization exists (~150 GB of weights,
  [antirez repo via The Neural Feed](https://theneuralfeed.com/article/deepseek-v4-flash-q4kexperts-f16hc-f16compressor-f16indexer-q8attn-q8shared-q8ou/zRxNXq14))
  for very large machines (512 GB-class). SWE-bench Verified ~79 at Max per library page.

### Google Gemma

**`gemma4`** — [Ollama library](https://ollama.com/library/gemma4) (verified)
- 12B dense (7.6 GB), 26B MoE 25.2B/3.8B active (18 GB), 31B dense (20 GB). 256K ctx
  (12/26/31B), vision + tools + thinking, native `system` role support. Google claims
  "native function-calling support, powering highly capable autonomous agents."
- 26B MoE is the sweet spot on paper (near-31B benchmarks at 18 GB). No official
  SWE-bench Verified number; secondary sources say it trails Qwen on agentic reasoning
  but is the best multimodal/compliance option.

### Mistral family

**`mistral-medium-3.5`** — [Ollama library](https://ollama.com/library/mistral-medium-3.5) (verified)
- Dense 128B, 256K ctx, vision + tools + thinking, 80 GB build. SWE-bench Verified 77.6%.
  Replaces Magistral (24B) and Devstral 2 in Mistral's own products. Too big for a 64 GB
  Mac.

**`devstral-2`** — [Ollama library](https://ollama.com/library/devstral-2) (verified)
- 123B agentic-coding model, 256K ctx, text-only, no thinking, 75 GB build. SWE-bench
  Verified 72.2%. Modified-MIT license with a $20M-revenue commercial carve-out. Largely
  superseded by Mistral Medium 3.5.

### Others

- **`gpt-oss:20b` / `:120b`** — [Ollama library](https://ollama.com/library/gpt-oss)
  (verified): OpenAI open-weights, MoE, MXFP4 quantization natively (no extra
  quant/conversion needed). 128K ctx, text-only, configurable reasoning effort, full
  chain-of-thought. 20b = 14 GB (runs in 16 GB+), 120b = 65 GB (single 80 GB GPU).
  **Tool-calling reliability is the weak spot** (see table above) — single tool call per
  turn and a history of parser bugs.
- **`nemotron-3-super`** — [Ollama library](https://ollama.com/library/nemotron-3-super)
  (verified): 120B MoE / 12B active, 256K ctx, tools + thinking, text-only, 87 GB.
  Optimized for multi-agent apps; trails peers on Terminal Bench (31.0).
- **`kimi-k2.7-code:cloud`** — [Ollama library](https://ollama.com/library/kimi-k2.7-code)
  (verified): 1.04T total, 256K ctx, native multimodal (image/video), agentic tool use +
  MCP, interleaved thinking preserved across turns. Coding-focused, ~30% lower
  thinking-token usage than K2.6. Cloud-only on Ollama.
- **`gemma4` cloud variants, `qwen3.5:397b-cloud`, `qwen3-coder:480b-cloud`,
  `minimax-m2.7/m3`, `glm-5.1`, `kimi-k3`** — hosted options on the library (verified to
  exist; not individually benchmarked here).

---

## Local vs hosted feasibility (realistic footprints)

| Model | Build size | Realistic host |
|---|---|---|
| `qwen3-coder:30b` | 19 GB | 24 GB+ GPU / 32 GB Mac |
| `qwen3.6:27b` | 17 GB | 24 GB GPU / 32 GB Mac |
| `qwen3.6:35b` | 24 GB | 32 GB+ GPU / 64 GB Mac |
| `gemma4:26b` | 18 GB | 24 GB GPU / 32 GB Mac |
| `gemma4:31b` | 20 GB | 24–32 GB GPU / 64 GB Mac |
| `gpt-oss:20b` | 14 GB | 16 GB+ (documented) |
| `gpt-oss:120b` | 65 GB | single 80 GB GPU |
| `qwen3.5:122b` | 81 GB | ~96 GB+ — **not a 64 GB Mac** |
| `mistral-medium-3.5` | 80 GB | ~96 GB+ — **not a 64 GB Mac** |
| `devstral-2` | 75 GB | ~96 GB+ — **not a 64 GB Mac** |
| `nemotron-3-super` | 87 GB | ~96 GB+ — **not a 64 GB Mac** |
| `qwen3-coder:480b` | 290 GB | 250 GB+ unified / multi-GPU, or hosted |
| `deepseek-v4-flash` | ~150 GB (community GGUF) | 512 GB-class Mac / multi-GPU, or hosted |
| `deepseek-v4-pro` | weights ~400 GB+ VRAM | datacenter, or hosted |

Footprints are the default (≈Q4-class) Ollama builds as listed on each library page —
verified. The "≥96 GB needed" calls for 75–87 GB builds are **inference** (Q4 build +
KV cache headroom for 200K+ agent contexts). Secondary sources agree the practical
agentic floor is Q4_K_M — going below roughly doubles tool-call malformation
([InsiderLLM](https://insiderllm.com/guides/best-local-coding-models-2026/),
**secondary**).

---

## Ranked recommendations

### Tier 2 — resolver (rubric weighing, adversarial self-check; needs frontier reasoning)

1. **`deepseek-v4-pro:cloud`** — the strongest reasoning model on Ollama (1.6T/49B,
   Max-thinking mode, 1M ctx). Hosted-only; treat as "needs a server/Ollama cloud."
2. **`kimi-k2.7-code:cloud`** — coding-focused frontier, multimodal, MCP support; a
   reasonable alternative if DeepSeek-V4-Pro isn't available, with 30% less thinking
   overhead.
3. **`qwen3.6:35b`** (local, 64 GB Mac) — the strongest locally-runnable thinking model,
   *provided* the reasoning mode is actually engaged on the Anthropic endpoint (see
   endpoint caveats). If thinking isn't being sent, this tier degrades to Tier-1 quality.

### Tier 1 — seed reviewers / PR review / react-performance (reliable tool use, good analysis)

1. **`qwen3-coder:30b`** — best tool-calling reliability on Ollama of any candidate,
   19 GB, no thinking overhead, 256K ctx. The default choice for local work.
2. **`qwen3.6:27b`** — vision + thinking + 99% tool-call schema validity (secondary),
   same footprint class; pick when vision or reasoning-on-findings matters.
3. **`gemma4:26b`** — native tool calling + vision at 18 GB; solid third, best if you
   also want multimodal in this tier. Hosted alternative: **`deepseek-v4-flash:cloud`**
   (cheap "Haiku-tier" pricing per secondary source, 1M ctx, strong tool use).

### Driver loop

- Hosted: **`deepseek-v4-pro:cloud`** (best all-round) — or `qwen3-coder:480b-cloud` /
  `kimi-k2.7-code:cloud` if cost/latency favors a coding-specialist.
- Local: **`qwen3-coder:30b`** (fast, reliable tools) or **`qwen3.6:35b`** (stronger
  reasoning, slower, needs a 64 GB Mac).

---

## Sources

Primary (verified by direct fetch):
- Ollama library — https://ollama.com/library
- Model pages: https://ollama.com/library/qwen3-coder · qwen3.6 · qwen3.5 · deepseek-v4-pro · deepseek-v4-flash · gpt-oss · gemma4 · mistral-medium-3.5 · devstral-2 · nemotron-3-super · kimi-k2.7-code
- Anthropic compatibility — https://docs.ollama.com/api/anthropic-compatibility
- Context length — https://docs.ollama.com/context-length
- OpenAI compatibility (alias model management) — https://docs.ollama.com/api/openai-compatibility
- DeepSeek-V4 release blog — https://huggingface.co/blog/deepseekv4
- Ollama tool support blog — https://ollama.com/blog/tool-support

Ollama GitHub issues / PRs (tool-calling and Claude Code operational bugs):
- https://github.com/ollama/ollama/issues/13949 · issues/15316 · issues/11621 · issues/16212 · issues/14645 · issues/14418 · issues/14745 · issues/12187 · issues/11800 · issues/11704
- https://github.com/ollama/ollama/pull/12248 · pull/16758 · pull/8938 · pull/16856 · pull/15022
- https://github.com/QwenLM/Qwen3-Coder/issues/475 · https://github.com/aaif-goose/goose/issues/6883

Secondary (context, flagged as such in the text):
- DeepResearch Ninja (Qwen3.6 vs Gemma 4 vs DeepSeek V4 analysis) — https://deepresearch.ninja/2026/05/Qwen3.6-27B/35B-A3B-vs-Gemma-4-vs-DeepSeek-V4-A-Comprehensive-Analysis-of-the-Open-Weight-Frontier-May-2026/
- Kilo blog — https://blog.kilo.ai/p/the-best-local-coding-models-for
- Convly — https://convly.ai/best-local-llms-to-run-on-ollama-2026/
- InsiderLLM — https://insiderllm.com/guides/best-local-coding-models-2026/
- BobbyEncoded Claude Code + Ollama walkthrough — https://www.bobbyencoded.com/blog/2026/05/20/run-claude-code-with-local-ollama
- The Neural Feed (DeepSeek-V4 GGUF) — https://theneuralfeed.com/article/deepseek-v4-flash-q4kexperts-f16hc-f16compressor-f16indexer-q8attn-q8shared-q8ou/zRxNXq14

## Confidence notes

- **Verified vs inferred is marked inline.** The single largest uncertainty: whether
  Claude Code actually sends a `thinking` preference to Ollama's `/v1/messages` endpoint,
  and therefore whether reasoning models (qwen3.6, deepseek-v4) run in their strong
  thinking mode during agent work. With tools present, Ollama defaults thinking off unless
  the client asks. Test this before betting the resolver tier on a thinking model.
- The Ollama library page numbers (pulls, "updated" timestamps, one 304B/284B mismatch on
  deepseek-v4-flash) are taken as-is; I did not reconcile them further.
- "Not on Ollama" list (Qwen 3.7-Max, no Llama 5, closed GPT-5.x/Claude) is based on the
  library listing plus secondary sources — absence is inherently a negative claim.
