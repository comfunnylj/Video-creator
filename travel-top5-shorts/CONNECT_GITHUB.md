# Travel TOP5 Shorts - GitHub connection

Repository: https://github.com/comfunnylj/Video-creator

## Architecture

- ChatGPT checks real places, footage links and individual licenses, then prepares a V2 job JSON.
- A GitHub issue written by the repository owner starts with the exact line `TOP5_STYLE_V2` followed immediately by the JSON job.
- `.github/workflows/travel-top5-style-v2.yml` runs only for owner-created V2 issues, or manually with `workflow_dispatch`.
- `travel-top5-shorts/scripts/github_runner.py` validates five authorized clips, downloads approved source files only from HTTPS Pexels hosts, and calls `render_top5.py` and `verify_top5.py`.
- Outputs: `top5_ko_SILENT.mp4`, `top5_en_SILENT.mp4`, `cut_markers.csv`, `source_audit.json`, attached to the GitHub Actions run for 14 days.

This is a **rendering pipeline**, not yet an automatic topic-only source-discovery or a YouTube uploading/publishing app. A video job needs 5 concrete verified location/media pairs before executing. The included `remote_job.sample.json` is a placeholder (NOT immediately executable) and must be filled with valid sources.

## Reference music

User-uploaded short `비현실적인 풍경 TOP5 #1.mp4` has a 23.3-second AAC track, and its picture is 696 frames at 30 fps. It can be analyzed as a **reference** for timing but is not supplied to GitHub and does not grant a master synchronization license. Do not copy its musical recording into public repositories, issue payloads or source archives.

For AWOLNATION – Sail, use the official sound inside YouTube's Shorts editing tools. Embedding an excerpt of Sail into a new MP4 externally may trigger ordinary Content ID rights handling. For different music with appropriate explicit sync and distribution rights, it may be muxed locally under the licensed use scope; do not assume the Shorts sound-library permission covers that.

## Exact frame timeline

0 (intro), 91 (rank 5), 121 (view 5), 212 (rank 4), 242 (view 4), 333 (rank 3), 363 (view 3), 454 (rank 2), 484 (view 2), 575 (rank 1), 605 (view 1), 696 (end).

## Security / restrictions

- The repo is public: avoid posting secrets, copyrighted song files, unreleased footage, and signed access tokens.
- The pipeline never stores user-provided API keys.
- It refuses unapproved or unverified footage and forbids fetching from arbitrary hosts.
- License approval fields represent the editor's completed review; the renderer does not itself decide copyright ownership.
- GitHub Actions artifacts are temporary; back up outputs elsewhere.

## Mandatory final delivery — avoid `Library not found`

For all future Top5 jobs, video rendering is **not** completion until the MP4 has been uploaded as a raw `video/mp4` to the connected Google Drive folder `프로젝트/멀티미디어/TOP 5` and the actual Google Drive file metadata (`mime_type`, file size, parent folder, browser URL) has been read back. Show the verified Drive URL as the primary open/download link. Never use `GenUI.openUrl("sandbox:/...")` buttons. The GitHub Actions artifact is a **14-day fallback**, not the canonical final delivery. Full procedure and validated 2026-10-28 recovery: [`DELIVERY_POLICY.md`](DELIVERY_POLICY.md).
