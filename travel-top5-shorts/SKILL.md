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
