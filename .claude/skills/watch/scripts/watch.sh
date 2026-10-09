#!/usr/bin/env bash
# Usage: watch.sh <video URL or local path> <output dir> [max frames]
# Produces: <out>/video.*, <out>/frames/*.jpg, <out>/transcript.txt (if captions exist), <out>/info.txt
set -euo pipefail

SRC="${1:?video URL or path required}"
OUT="${2:?output dir required}"
MAX_FRAMES="${3:-40}"
mkdir -p "$OUT/frames"

if ! command -v yt-dlp >/dev/null 2>&1; then
  pip install -q yt-dlp >/dev/null 2>&1 || { echo "yt-dlp install failed" >&2; exit 1; }
fi

if [[ "$SRC" =~ ^https?:// ]]; then
  JS=(); command -v node >/dev/null 2>&1 && JS=(--js-runtimes node)
  # YouTube blocks cloud IPs ("confirm you're not a bot"); YT_COOKIES holds a Netscape cookies.txt
  if [[ -n "${YT_COOKIES:-}" ]]; then
    # Accept raw cookies.txt or a one-line base64 of it (env var UIs often drop newlines/tabs)
    if [[ "$YT_COOKIES" == *$'\t'* ]]; then printf '%s\n' "$YT_COOKIES" > "$OUT/.cookies.txt"
    else printf '%s' "$YT_COOKIES" | base64 -d > "$OUT/.cookies.txt"; fi
    JS+=(--cookies "$OUT/.cookies.txt")
  fi
  if ! yt-dlp -q --no-warnings --no-playlist "${JS[@]}" \
    -f "bv*[height<=720]+ba/b[height<=720]/b" --merge-output-format mp4 \
    --write-info-json -o "$OUT/video.%(ext)s" "$SRC"; then
    # YouTube bot-blocks cloud IPs. The mweb client still returns metadata and storyboard
    # mosaics (3x3 thumbnail grids from i.ytimg.com), which is enough to see the video roughly.
    echo "video download blocked; falling back to metadata + storyboard thumbnails" >&2
    yt-dlp -q --no-warnings --no-playlist "${JS[@]}" --extractor-args "youtube:player_client=mweb" \
      --skip-download --write-info-json -o "$OUT/video.%(ext)s" "$SRC"
    python3 - "$OUT" <<'PY'
import json, subprocess, sys
out = sys.argv[1]
d = json.load(open(f"{out}/video.info.json"))
sb = [f for f in d["formats"] if f["format_id"].startswith("sb")]
best = max(sb, key=lambda f: f.get("width") or 0)
t = 0.0
per_tile = best["fragments"][0]["duration"] / (best["rows"] * best["columns"])
for i, fr in enumerate(best["fragments"]):
    path = f"{out}/frames/storyboard_{i:02d}_t{int(t):05d}s.jpg"
    subprocess.run(["curl", "-sS", "-o", path, fr["url"]], check=True)
    t += fr["duration"]
with open(f"{out}/info.txt", "w") as fh:
    fh.write(f"source: {d['webpage_url']}\ntitle: {d['title']}\nuploader: {d.get('uploader')}\n"
             f"duration_sec: {d['duration']}\nmode: storyboard only ({best['rows']}x{best['columns']} grid per image, "
             f"{per_tile:.1f}s per tile, left-to-right then top-to-bottom; file name = start time)\n"
             f"description:\n{d.get('description','')}\n")
print(open(f"{out}/info.txt").read())
PY
    exit 0
  fi
  # Captions are best effort: original ko/en only (translated tracks trigger 429s)
  yt-dlp -q --no-warnings --no-playlist "${JS[@]}" --skip-download \
    --write-subs --write-auto-subs --sub-langs "ko,en,ko-orig,en-orig" --sub-format vtt \
    -o "$OUT/video.%(ext)s" "$SRC" || echo "captions: download failed (continuing without)" >&2
  VIDEO="$(ls "$OUT"/video.mp4 "$OUT"/video.mkv "$OUT"/video.webm 2>/dev/null | head -1)"
else
  VIDEO="$SRC"
fi
[[ -f "$VIDEO" ]] || { echo "video not found: $VIDEO" >&2; exit 1; }

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" | cut -d. -f1)"
DUR="${DUR:-1}"; (( DUR < 1 )) && DUR=1
INTERVAL=$(( (DUR + MAX_FRAMES - 1) / MAX_FRAMES )); (( INTERVAL < 1 )) && INTERVAL=1

# One frame every INTERVAL seconds, 768px wide; file name = timestamp in seconds
ffmpeg -v error -i "$VIDEO" -vf "fps=1/$INTERVAL,scale=768:-2" -q:v 4 "$OUT/frames/f_%04d.jpg"
i=0
for f in "$OUT"/frames/f_*.jpg; do
  t=$(( i * INTERVAL )); mv "$f" "$OUT/frames/t$(printf '%05d' "$t")s.jpg"; i=$((i+1))
done

# Captions -> plain text with timestamps (dedupe rolling auto-caption lines)
VTT="$(ls "$OUT"/video*.ko*.vtt "$OUT"/video*.en*.vtt 2>/dev/null | head -1 || true)"
if [[ -n "$VTT" ]]; then
  awk '
    /-->/ { split($1,a,"."); ts=a[1]; next }
    /^WEBVTT|^Kind:|^Language:|^[[:space:]]*$/ { next }
    { gsub(/<[^>]*>/,""); if ($0 != last) { print "[" ts "] " $0; last=$0 } }
  ' "$VTT" > "$OUT/transcript.txt"
fi

{
  echo "source: $SRC"
  echo "video: $VIDEO"
  echo "duration_sec: $DUR"
  echo "frame_interval_sec: $INTERVAL"
  echo "frames: $(ls "$OUT"/frames | wc -l)"
  echo "transcript: $([[ -s "$OUT/transcript.txt" ]] && echo "$OUT/transcript.txt ($VTT)" || echo none)"
} | tee "$OUT/info.txt"
