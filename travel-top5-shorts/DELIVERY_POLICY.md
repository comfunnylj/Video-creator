# Travel Top5 Shorts — Reliable file delivery (2026-10-28)

## Observed issue
ChatGPT mobile app users may see `Library not found` when attempting to open an assistant-produced `sandbox:/mnt/data/...` file (particularly buttons that call `GenUI.openUrl("sandbox:...")`).
This is **not** evidence that the MP4 is corrupt or that any particular Python or FFmpeg library is missing.
The root cause of the mobile UI error is not established. Do not claim the platform issue itself is fixed.

## Default handoff — mandatory for every future generated TOP5 video
1. Confirm real MP4 bytes exist on disk, run ffprobe, and check the duration, dimensions and audio/video streams.
2. Upload the **MP4 itself** (not only a ZIP) to the owner's connected Google Drive folder:
   - `프로젝트/멀티미디어/TOP 5`
   - Observed folder ID on 2026-10-28: `1HoKHsWusXlzIJ1r0TbyrX295SbUKLKfU`
   - Name files `YYYYMMDD_<topic>_Top5.mp4`.
3. Use the connected Google Drive upload capability, or Files Library operation `upload` from a verified container path to `/Google Drive/프로젝트/멀티미디어/TOP 5/<file>.mp4`. The latter may return an external-gdrive file ID.
4. **Read back** the newly created file's Google Drive metadata using the *real* Drive file ID:
   - MIME type is `video/mp4`;
   - byte size matches the source file;
   - parent folder is the intended folder;
   - retrieve the actual returned `url`/browser link.
5. Only after readback, show the real Drive browser URL as the **primary user-facing video link**.
6. If the Drive upload or verification fails, do not claim the link works. Clearly report the failure and provide the GitHub Actions artifact/run link as a temporary fallback (artifacts expire after 14 days).
7. Where licensing requires it, also upload `ATTRIBUTION.txt` and `source_audit.json`, and keep media license provenance explicit.
8. Do **not** render `GenUI.openUrl("sandbox:/...")` as a user button; this is not an ordinary website URL and may trigger a missing-library or file resolver error. Sandbox links may be optional secondary downloads only when the backing file was actually generated/verified during this conversation.

## Operational security
- Never put Google Drive credentials, SSH keys, OAuth tokens, temporary signed URLs or raw access secrets into GitHub issues, files, Actions logs, or artifacts.
- A GitHub Actions artifact is transient; it is **not** a persistent distribution channel.
- A file uploaded to an owner's private Drive is accessible to that owner's account; do not change sharing permissions without instruction.
- Treat a successful GitHub render and successful Google Drive handoff as separate verifiable steps.

## Verified correction — China Top5 2026-10-28
- Local rendered file: `China_Top5_KO_EN.mp4`
- FFprobe: 23.2s, 720 × 1280, H.264 with AAC audio, 1,244,351 bytes.
- Uploaded to `프로젝트/멀티미디어/TOP 5/20261028_China_Travel_Top5_Lijiang_Wangxian.mp4`.
- Google Drive read-back: `17AZa7eAQq6tIGIl8rLzIAX-Ou81Vexmz`, `video/mp4`, `1244351` bytes, expected parent folder confirmed.
- Durable owner link: https://drive.google.com/file/d/17AZa7eAQq6tIGIl8rLzIAX-Ou81Vexmz/view?usp=drivesdk
- Render run: https://github.com/comfunnylj/Video-creator/actions/runs/40705776917
