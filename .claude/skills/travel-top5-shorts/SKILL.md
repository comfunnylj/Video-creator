---
name: travel-top5-shorts
description: Produce bilingual 23.2-second TOP5 travel Shorts/Reels with verified real-world location footage, a fixed 696-frame timing pattern, top-left Korean/English place labels, no narration, and silent MP4s ready for adding licensed sound in YouTube Shorts. Use when the user requests ranked real-location short-form videos, especially the existing Sail-style series.
---

# Travel TOP5 Shorts (23.2s fixed-cut edition)

## Scope and prerequisites
- This is a **user-produced skill bundle**, not an assertion of installation into the current ChatGPT account. The execution agent needs Python 3.10+, `Pillow`, `ffmpeg`, `ffprobe`, and the bundled `scripts/render_top5.py`.
- It does not acquire or redistribute AWOLNATION's copyrighted `Sail`, access the user's YouTube account, or automatically approve licensing. Never embed that recording without separate rights.
- If the user asks for a particular theme, independently verify **five real places** and acquire five clips depicting the named sites, with source and license records. Do not present AI visuals or an unrelated view as documented footage. Honor restricted sites and uncertain filming locations: rename the label to what the source can establish or choose another clip.

## Workflow
1. Clarify only if the topic itself is missing; otherwise select five thematic places. State the ranking is **editorial**, not official.
2. Find actual videos with reusable/commercial permissions (e.g. Pexels, Pixabay) and capture source URL, creator, license URL, date checked, depicted location, rights/restrictions. Check each item individually; no blanket assertion that every clip is safe. Check logos, recognizable people, private property when relevant.
3. Prefer moving footage without visible watermarks and with sufficient duration for 3.033s view. Choose crop anchor by inspecting frames so the landmark survives vertical crop; never substitute unrelated geography.
4. Make an `examples/manifest.json`-compatible project manifest; place all five original clips into a project `assets` folder. Include English name + Korean name, source URL, verified filming-place support. Exclude any user's API key from the manifest, logs, ZIP, and repository.
5. Run `python scripts/render_top5.py path/to/manifest.json --output-dir outputs`. Make both Korean/English 1080×1920, 30fps, H.264 MP4s; use no narration and **no embedded audio**. If no real licensed footage exists for a requested location, stop or change that location transparently.
6. Validate both videos with `scripts/verify_top5.py`. Check the frame count 696, length 23.200s, zero audio streams, correct safe-area labels and all 5 correct places. Use contact sheet and spot-check each place. Output source/rights table and final cut-markers CSV.
7. The user's established music workflow: upload silent MP4, choose the **official AWOLNATION – Sail** sound inside YouTube Shorts, reuse the same **user-tested sound excerpt/start position**, and manually verify beat synchronization. 119 BPM is only nominal; do not claim waveform/first downbeat synchronization without inspecting the specific licensed audio recording.
8. If publishing the video on the user's behalf via supported app, do not assume app music licensing applies to externally embedded sounds. YouTube Shorts in-app sound selection is a different operation from MP4 audio composition. No publish without an executable authorized workflow.

## Immutable style contract (unless user asks to change)
- 9:16, 1080×1920, 30 fps, exactly **696 frames / 23.200s**.
- 0–91f intro, then 5 repetitions of 30f rank/country slate + 91f real scenery, ordered #5 to #1.
- Exact cut frame boundaries: `0, 91, 121, 212, 242, 333, 363, 454, 484, 575, 605, 696`.
- Location overlay only at **top-left**, small text. KO variant: Korean location title + English title underneath. EN variant: English title + country (English) underneath. Bottom-left stays free due to app UI.
- Natural stock video motion; do not transform actual geography or architecture. Intro and rank cards may be graphical; avoid implying their backgrounds are an authentic landmark.
- Produce KO and EN silent MP4, manifest, source log, and QA results. Clearly distinguish a prepared silent render from a video with finalized audio sync.

## Command
```bash
pip install Pillow
python scripts/render_top5.py project/manifest.json --output-dir project/outputs
python scripts/verify_top5.py project/outputs/top5_ko_SILENT.mp4 project/outputs/top5_en_SILENT.mp4
```

## Security and reproducibility
Never paste Gemini or other API keys into deliverables. Use `GEMINI_API_KEY` from secured local environment if watch-gemini video analysis is separately requested. The rendering script itself needs **no API key**. Save the manifest and source-rights audit as evidence; do not treat file titles or download links as proof of filmed geography. For an unverified clip, no output is preferable to false geography.

## Persistent global numbering and Drive archive (user rule, 2026-10-22)
- All TOP5 Shorts in this project share **one sequential series counter across every topic**. Never restart #1 for a new category. As of 2026-10-22, completed items are #1 original surreal nature, #2 alternate surreal nature, #3 Seoul Hangang, and #4 unbelievable Earth scenery. Always derive the next number from the current CSV, not this example.
- The source of truth is the CSV `TOP5_영상제작목록.csv` under **Google Drive → 프로젝트 → 멀티미디어** (folder ID `1Au5KF_gCQEwMZ4u2dHwV8FCHXmmCMrsI`). Before starting a new installment, read it and choose max existing serial + 1. Retain failed/incomplete rows with explicit status; never call a failed render 'completed'. Avoid conflicts if parallel jobs exist.
- Append the serial suffix to the Korean title, English title, final MP4 filenames and production-list entry (e.g. `... TOP5 #4`). Do not confuse a rank (`#1` inside the video) with the global production serial (`#4`).
- After technical QA succeeds, archive both KO and EN finished MP4s, the optional source/rights package and contact preview in **that exact Drive Multimedia folder**, and verify read-back from Google Drive. Do not claim Drive upload succeeded before listing the files.
- Keep the production list intentionally simple: production date (KST), video title, locations shown (rank 5→1), status, stored filenames. For old items with unknown dates, record unknown instead of guessing. Update the CSV only after determining verified work status. Preserve prior rows.
- YouTube-app-added copyrighted music is NOT embedded in stored silent master files; the original user-posted MP4 with YouTube audio, if provided, may be privately archived separately without using that embedded track as a blanket reuse license.

## Global visual quality preference (2026-10-24)
- User rejects low-quality images/videos and any **timelapse, hyperlapse, accelerated or artificially sped-up footage**. These are prohibited in TOP5 projects as well as Daily Quote Maker, unless the user explicitly changes this rule.
- Favor sharply focused 4K/UHD-or-better native footage with an authentic, cinematic composition; keep true real-time speed. Reject blurry, heavily compressed, low-bitrate or obviously upscaled source clips.
- Before accepting a clip, inspect its actual native resolution, vertical crop quality, speed and a few nonadjacent frames. An exported 1080×1920 file is not evidence the original was high-resolution.
- When suitable real-time video cannot be obtained, prefer an excellent authentic high-resolution **long-exposure still** in the separate Daily Quote Maker workflow; do not substitute a low-quality timelapse.
- See `daily-quote-maker/QUALITY_POLICY.md` for shared quality standards.
