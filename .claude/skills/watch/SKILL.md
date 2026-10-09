---
name: watch
description: Watch a video (URL or local path). Downloads with yt-dlp, extracts frames with ffmpeg, transcribes via captions, then summarizes or answers questions about the video. Use when the user runs /watch or asks to watch, summarize, or analyze a video.
---

# Watch a video

Input: a video URL (YouTube etc.) or a local file path, plus an optional question.

1. Run the script into the scratchpad (or a temp dir), not the repo:
   ```bash
   bash .claude/skills/watch/scripts/watch.sh "<url or path>" "<scratchpad>/watch/<name>" [max_frames]
   ```
   `max_frames` defaults to 40. Raise it for long or fast-cut videos, lower it for short ones.
   The script installs `yt-dlp` with pip if missing. `ffmpeg` must be installed.
2. Read `info.txt`, then `transcript.txt` if it exists (`[HH:MM:SS] text` lines from ko/en captions).
3. Look at the frames in `frames/` with the Read tool. File names are the timestamp (`t00120s.jpg` = 2:00).
   Read them in time order; for long videos skim evenly spaced ones first, then zoom in where needed.
4. Answer in the user's language: what happens, key points with timestamps, and anything the
   user specifically asked. Say clearly when there was no transcript and the answer is from frames only.

If the download fails (private video, geo block, proxy 403), report the yt-dlp error as-is and ask
for a local file instead.
