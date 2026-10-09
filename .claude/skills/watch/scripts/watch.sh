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
  yt-dlp -q --no-playlist \
    -f "bv*[height<=720]+ba/b[height<=720]/b" --merge-output-format mp4 \
    --write-subs --write-auto-subs --sub-langs "ko.*,en.*" --sub-format vtt \
    --write-info-json \
    -o "$OUT/video.%(ext)s" "$SRC"
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
