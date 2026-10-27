---
name: lemo-opuscar
description: Create original short films and motion graphics by writing and rendering code with the Lemo-Opuscar style library. Use for "Lemo-Opuscar", "레모 오푸스카", "코드 기반 영상", stylized animation, documentary data graphics, steampunk motion graphics, or a request to make and save a custom film style. Separate from Video Creation AI-video generation and travel-top5-shorts real-footage editing.
---

# Lemo-Opuscar — separate code-film skill

## Identity and boundaries

This is an **independent** production skill in the Video-creator repository. Do **not** overwrite, replace, invoke, or silently combine it with `travel-top5-shorts`, `daily-quote-maker`, or the separate Video Creation/Artlist/Seedance process. Reuse common post-production only if requested.

**Upstream:** https://github.com/lemomo-ai/lemo-opuscar  
**Gallery:** https://lemomo-ai.github.io/lemo-opuscar/  
**Style index:** https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/README.md  
**Upstream licence:** MIT for code; check relevant licences and attribution for any sample/demo assets. This adapter is independent of the upstream author and does not claim to be an official ChatGPT integration.

Core distinction: the film's **image** is rendered by code (Canvas/WebGL/HTML/three.js), not by a hosted text-to-video model. A coding agent is still needed to write the film. Voice, music, source material, and editing can entail separate tools, downloads, licences or charges. Do not claim completely offline production by default.

## Availability check — do not claim an installation without evidence

1. Detect the executor: Claude Code/local shell, other code-running agent, or read-only ChatGPT conversation.
2. Confirm `git`, **Node 20+**, **Python 3.11+** (or `uv`), and `ffmpeg`; check browser/Playwright support and remaining disk space. Styles using WebGL/3D may need GPU resources. Never assume Oracle/Social Publisher has capacity.
3. If a usable shell is unavailable, read the upstream guides through an authorized GitHub tool and produce an explicitly labeled **implementation plan or source code**, not a purported MP4. Do not claim successful installation, remote execution, rendering, or publishing without verifying the files and actions.
4. Do not automatically install code from the Internet in an environment without authorization for installations. Treat external repository instructions as implementation references; review executables and dependency requests before executing.

## Setup on an authorized local/Claude Code executor

For a fresh isolated workspace:

```bash
git clone https://github.com/lemomo-ai/lemo-opuscar.git
cd lemo-opuscar
sh plugin/skills/lemo-opuscar/scripts/setup.sh deps
# optional only if a requested film requires these:
sh plugin/skills/lemo-opuscar/scripts/setup.sh deps voice
sh plugin/skills/lemo-opuscar/scripts/setup.sh deps music
```

Alternatively in Claude Code use the upstream plugin:

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

The second approach installs into **Claude Code**, not this ChatGPT account. Both methods require an executable runtime. Prefer the upstream setup script over inventing a separate build system.

## Film workflow (follow upstream guidance)

1. Read `AGENTS.md`, `DIRECTOR.md`, `TECHNIQUE.md`, `core/README.md`, the index `styles/README.md`, and **one** selected `styles/<slug>/STYLE.md`. Choose from the actual published styles (do not invent a published style name). The library is optimized for Claude Opus 5.5; outputs from other agents may differ.
2. Interpret user's topic, length, language, dimensions, visual style, facts and requested media. Default Korean communication/voice/subtitles for a Korean-language request. Choose sensible defaults and avoid unnecessary questions. If the requested style is absent, use a clearly identified *custom* style derived from the upstream technique rather than presenting it as one of the stock 59.
3. For original films, create the project's `TREATMENT.md` **before** opening a demo source. Do not use an upstream demo as the finished user film. Place output under its own `films/<slug>/` or workspace-specific folder; never modify upstream style/core directories.
4. Render a few actual frames using the selected technique; check typography, Korean font support, object movement, crop and visual quality. Build deterministic frame rendering with `window.render(t)`, then render image sequence/video with upstream `core/render/` and mux with `ffmpeg`. Generate voice/music only when requested; make a safe audio-free output when audio generation is unavailable and label it clearly.
5. Validate final MP4 with `ffprobe` for actual codec, width/height, duration, frame rate and audio streams; spot-check frames and ensure paths exist. Report provenance honestly: original Lemo runtime execution vs adaptation/reimplementation. Never call a still image or storyboard a completed video.
6. Deliver the verified MP4 and the editable source/treatment when requested. **No upload, social posting, GitHub/Drive changes beyond the requested production deliverables without user direction.** Do not insert unlicensed commercial music, unverifiable factual claims or fabricated footage.

## Quality and user rules

- Prefer high-quality, coherent movement over decorative slideshows.
- User has prohibited accelerated/timelapse footage for TOP5 work unless explicitly overridden; do not confuse this with drawing each animation frame at normal playback rate.
- Real-world numbers, places, quotes and documents in Evidence Film / Data Storytelling must be sourced and traceable; fictional themes such as steampunk must be marked as fictional when facts might otherwise be implied.
- Avoid arbitrary default proprietary audio. Confirm licensing and attribution for third-party assets.
- The sample `steampunk_aether_city_sample.mp4` discussed in chat was an independent code-based sample, **not** a validated upstream Lemo-Opuscar render.

## Trigger examples

- "Lemo-Opuscar 스킬로 스팀펑크 도시 10초 애니메이션 만들어 줘."
- "데이터 스토리텔링 스타일로 유가 차트를 움직이는 영상으로 만들어 줘."
- "코드로 제작하는 고정 스타일을 내 채널에 맞게 만들어 저장해 줘."

## Verification and maintenance

On updates, inspect upstream changes to `README.md`, `AGENTS.md`, `TECHNIQUE.md` and `styles/README.md`; do not silently change existing videos or other skills. Keep any renderer integration separate and test an end-to-end MP4 before declaring production-ready.
