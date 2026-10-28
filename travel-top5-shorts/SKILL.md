---
name: travel-top5-shorts
description: 제작·검증·전달까지 완료하는 여행지 Top5 쇼츠/릴스 운영 스킬. 한/영 자막, 영상 소스 검증, 23.2초 컷 기준, Google Drive MP4 전달을 포함한다.
---

# Travel TOP5 Shorts — operating skill

## Trigger
When the owner requests a TOP5 travel short, use this repository's [production workflow](CONNECT_GITHUB.md) as an available rendering option.

## Production rules
- Verify that five locations exist. Never invent destinations or claim subjective rankings are official.
- Match each photo/video to the correct location and verify its license. Do not fake location footage.
- Preserve the previously confirmed 23.2s/30fps sequence and cuts when applicable: frame boundaries `[0,91,121,212,242,333,363,454,484,575,605,696]`.
- Keep bilingual captions in the top region, away from YouTube/Instagram bottom-left controls.
- Do not embed third-party commercial songs into MP4 without rights. Where a platform provides an authorized music catalog, the user may add the track within that platform.

## Completion contract — mandatory
An Actions render success does **not** mean the user has the final video.
- Obtain the output MP4 and verify it with ffprobe.
- Upload the **MP4 itself** to the connected owner Google Drive at `프로젝트/멀티미디어/TOP 5` (not just GitHub Actions temporary artifact).
- Re-read Drive metadata and verify `video/mp4`, correct byte size, parent and actual browser URL.
- Present that verified Drive link as the **primary** user-facing video link.
- Avoid `GenUI.openUrl("sandbox:/...")` buttons: they may fail in the mobile client with `Library not found`. Use normal Google Drive HTTPS URL instead.
- On failure to upload, report the failure and show the GitHub Actions run as fallback, noting the artifact expires after 14 days.
- Preserve attribution/license records. Never change file sharing to public without instruction.
- If this skill is present only in the GitHub repo and is not installed in ChatGPT, do not claim it has been installed or globally activated.

See [DELIVERY_POLICY.md](DELIVERY_POLICY.md) for a tested 2026-10-28 example, explicit path, and verification checklist.


## User-confirmed visual style — 2026-10-29 (priority over earlier default)
- The uploaded reference video titled `세계 비현실적인 장소 TOP5 🌎#34.mp4` was inspected directly: **720×1280 at 30fps, 689 frames, 22.9667s**.
- Editing pattern: 0.00–3.00s full-bleed opening footage with small two-line TOP5 heading; each ranked location begins with a brief **plain black flag/country transition card**, then a **full-bleed real-location scenic view** with compact white/black-outlined Korean and English caption positioned at the upper-left.
- Observed transitions approximately 3.000–3.967, 6.867–8.033, 10.767–11.967, 14.900–16.067, 19.133–20.133. Total ~22.967s. These override the older 23.2s cut timings **when this reference style is requested**.
- **NO BGM by default.** In this mode render `-an` and verify the MP4 has exactly **zero audio streams**. Do not add synthesized beats, stock music, or the reference video's copyrighted soundtrack unless the user explicitly authorizes a properly licensed audio track.
- **NO yellow rank pill, gold/yellow decorative frame, blurred/letterboxed center strip, oversized title block, or colored border.** An incidental yellow word 'TOP5' within the source reference's headline, and national flag colors, are not a decorative frame; other overlays must be restrained.
- **Use high-quality correctly identified source material**. For Wangxian Valley, source must actually depict Wangxian Valley (望仙谷); do not substitute generic canyon or modern bridges, or falsely claim a generic photograph depicts the iconic cliff houses. Lijiang must show verified Lijiang imagery. Inspect a contact sheet or a representative frame from every clip/photo before delivery.
- Footage is preferred because the reference contains real moving scenes. If only photographs are legally obtainable, animate with subtle pan but state clearly that the result uses photo movement rather than real recorded footage.
- Subjective TOP5 ranking must not be described as an official tourism ranking.
- Example generated for reference style: `China_Top5_Reference_Style_SILENT.mp4` (2026-10-29), local inspection verified 689 frames at 30fps, 720×1280, 22.9667s, video-only MP4; sources recorded separately in `China_Top5_Reference_Style_SOURCES.txt`.
- Keep verified Google Drive delivery as a backup; **also provide a direct verified sandbox download link** when a generated local MP4 is available, since the user explicitly wants to download the file directly. Do not wrap the sandbox URL inside `GenUI.openUrl`.
