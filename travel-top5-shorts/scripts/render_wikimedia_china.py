#!/usr/bin/env python3
"""China Travel Top5: real Wikimedia Commons photography animated into a short.
Licensed still images, not original motion footage. No copyrighted music.
"""
import argparse
import hashlib
import json
import math
import random
import shutil
import struct
import subprocess
import time
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H, FPS = 720, 1280, 30
MARKERS = [0, 91, 121, 212, 242, 333, 363, 454, 484, 575, 605, 696]
TITLE = "중국, 현실 아닌 풍경 TOP 5"
SUBTITLE = "CHINA'S UNREAL TRAVEL SPOTS"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def cmd(*args):
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"Command failed {args[:3]}: {p.stderr[-2300:]}")
    return p.stdout

def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=1)

def validated_job(event):
    payload = json.loads(Path(event).read_text(encoding="utf-8"))
    issue = payload.get("issue", {})
    if issue.get("user", {}).get("login") != "comfunnylj":
        raise ValueError("Only repo owner can trigger.")
    body = issue.get("body", "")
    if not body.startswith("CHINA_TOP5_V1\n"):
        raise ValueError("Missing job prefix.")
    job = json.loads(body.split("\n", 1)[1])
    places = job.get("places")
    if not isinstance(places, list) or len(places) != 5:
        raise ValueError("Five places required.")
    for p in places:
        for key in ("ko", "en", "region", "file", "author", "license"):
            if not isinstance(p.get(key), str) or not p[key] or len(p[key]) > 180:
                raise ValueError(f"Missing or invalid {key}")
        if "/" in p["file"] or "\\" in p["file"] or not p["file"].lower().endswith((".jpg", ".jpeg", ".png")):
            raise ValueError("Wikimedia Commons file basename expected.")
        if p["license"] not in ("CC BY 2.0", "CC BY-SA 4.0"):
            raise ValueError("Unsupported copyright license.")
    return job

def commons_url(basename):
    name = basename.replace(" ", "_")
    md5 = hashlib.md5(name.encode("utf-8")).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{md5[0]}/{md5[:2]}/{urllib.parse.quote(name)}"

def fetch_photo(p, out):
    url = commons_url(p["file"])
    req = urllib.request.Request(url, headers={
        "User-Agent": "TravelTop5Shorts/1.0 (https://github.com/comfunnylj/Video-creator)"
    })
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as reply:
                body = reply.read(16 * 1024 * 1024 + 1)
            if len(body) < 10000 or len(body) > 16 * 1024 * 1024:
                raise ValueError("Unreasonable image file size.")
            out.write_bytes(body)
            with Image.open(out) as im:
                im.verify()
            return url
        except Exception as exc:
            last_err = exc
            time.sleep(1 + attempt * 2)
    raise RuntimeError(f"Image download failed: {p['file']}: {last_err}")

def gradient_mask(top, bottom):
    m = Image.new("L", (1, H))
    m.putdata([int(top + (bottom - top) * y / (H - 1)) for y in range(H)])
    return m.resize((W, H))

def picture(path):
    photo = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    base = ImageOps.fit(photo, (W, H), method=Image.Resampling.LANCZOS)
    base = base.filter(ImageFilter.GaussianBlur(25))
    base = ImageEnhance.Brightness(base).enhance(.52)
    # Put the entire actual view in a central cinematic window; do not misrepresent location.
    target_w, target_h = W, 860
    fit = ImageOps.contain(photo, (target_w, target_h), method=Image.Resampling.LANCZOS)
    x, y = (W - fit.width) // 2, (H - fit.height) // 2 + 75
    base.paste(fit, (x, y))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H))
    dr = ImageDraw.Draw(mask)
    for yy in range(H):
        amt = max(0, 205-int(yy / 3.2)) if yy < 460 else max(0, int((yy-930)*.34))
        dr.line((0, yy, W, yy), fill=min(215, amt))
    shade.putalpha(mask)
    base = Image.alpha_composite(base.convert("RGBA"), shade).convert("RGB")
    return base

def place_card(im, place, rank, mode):
    draw = ImageDraw.Draw(im)
    if mode == "intro":
        draw.text((43, 65), "TRAVEL / TOP 05", fill=(229, 200, 133), font=font(25, True))
        draw.text((43, 177), "중국 여행", fill="white", font=font(68, True), stroke_width=2, stroke_fill="#182029")
        draw.text((43, 272), "버킷리스트 TOP 5", fill="white", font=font(53, True), stroke_width=2, stroke_fill="#182029")
        draw.text((43, 364), "5 UNREAL PLACES IN CHINA", fill=(240, 215, 164), font=font(28, True))
        draw.text((43, 1100), "실제 여행지 사진으로 만나는 중국", fill="white", font=font(25, True))
        draw.text((43, 1150), "REAL LOCATIONS · LICENSED PHOTOS", fill="white", font=font(17))
    elif mode == "rank":
        draw.rounded_rectangle((42, 68, 204, 117), radius=15, fill=(226, 175, 85))
        draw.text((58, 71), f"RANK {rank:02}", fill=(23, 31, 39), font=font(29, True))
        draw.text((50, 370), f"{rank:02}", font=font(230, True), fill="white", stroke_width=3, stroke_fill="#1A212C")
        draw.text((51, 615), "CHINA TOP 5", font=font(36, True), fill="white", stroke_width=2, stroke_fill="#1A212C")
    else:
        draw.rounded_rectangle((40, 54, 144, 100), radius=13, fill=(225, 176, 93))
        draw.text((50, 58), f"TOP {rank}", font=font(25, True), fill="#182433")
        draw.text((42, 130), place["ko"], font=font(59, True), fill="white", stroke_width=2, stroke_fill="#121C25")
        draw.text((42, 213), place["en"], font=font(30, True), fill="white", stroke_width=2, stroke_fill="#121C25")
        draw.text((44, 265), place["region"], font=font(22), fill=(239, 220, 175))
        draw.text((42, 1157), "CHINA TRAVEL   •   2026", font=font(18), fill="white")
    return im

def synth_music(path, duration):
    """Deterministic original percussion/ambient, no third-party sound samples."""
    sr = 22050
    rng = random.Random(20261028)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        block = bytearray()
        for i in range(round(duration*sr)):
            t = i/sr
            down = t % .5
            kick = .29 * math.exp(-22*down) * math.sin(2*math.pi*(92 - 42*min(down,.15))*down)
            clap_t = (t-.5) % 1.
            clap = (.085*(rng.random()*2-1)*math.exp(-37*clap_t)) if clap_t < .14 else 0
            hat_t = t % .25
            hat = .025*(rng.random()*2-1)*math.exp(-85*hat_t)
            root = [174.61, 146.83, 164.81, 130.81][int(t//4) % 4]
            pad = .055*(math.sin(2*math.pi*root*t) + math.sin(2*math.pi*root*1.5*t))/2
            fade = min(1, t/.45, (duration-t)/.65)
            s = max(-1, min(1, fade*(kick + clap + hat + pad)))
            block += struct.pack("<h", int(s*28000))
            if len(block) > 32768:
                wf.writeframesraw(block)
                block.clear()
        if block:
            wf.writeframesraw(block)

def render_segment(image_path, nframes, segment_path):
    vf = ("zoompan=z='min(zoom+0.00020,1.046)':"
          "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          f"d=1:s={W}x{H}:fps={FPS},format=yuv420p")
    cmd("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-i", str(image_path),
        "-vf", vf, "-frames:v", str(nframes), "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", str(FPS), str(segment_path))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--out", default="output_china_top5")
    args = parser.parse_args()
    job = validated_job(args.event)
    out = Path(args.out)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    images = []
    attributions = []
    for i, p in enumerate(job["places"]):
        photo_path = work / f"licensed_{i}.jpg"
        url = fetch_photo(p, photo_path)
        images.append(photo_path)
        attributions.append({
            "place": p["ko"], "file": p["file"], "author": p["author"],
            "license": p["license"], "license_url": (
                "https://creativecommons.org/licenses/by-sa/4.0/" if p["license"] == "CC BY-SA 4.0"
                else "https://creativecommons.org/licenses/by/2.0/"),
            "source_url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(p["file"].replace(" ", "_")),
            "image_url": url,
            "modification": "Centered/letterboxed, cropped/blurred background and text overlays, animated as video."
        })
    scenes = [("intro", None, 91)]
    for i, p in enumerate(job["places"]):
        scenes.append(("rank", i, 30))
        scenes.append(("view", i, 91))
    if sum(frames for _, _, frames in scenes) != 696:
        raise RuntimeError("Invalid cut markers")
    segments = []
    for seq, (mode, i, frames) in enumerate(scenes):
        p = job["places"][i] if i is not None else None
        img = picture(images[i] if i is not None else images[-1])
        rank = 5-i if i is not None else 0
        png = work / f"scene{seq:02}.png"
        place_card(img, p, rank, mode).save(png, optimize=True)
        mp4 = work / f"segment{seq:02}.mp4"
        render_segment(png, frames, mp4)
        segments.append(mp4)
        print("SCENE_OK", seq, mode, frames, flush=True)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{mp4.resolve()}'\n" for mp4 in segments), encoding="utf-8")
    silent = work / "silent.mp4"
    cmd("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
        "-safe", "0", "-i", str(concat), "-c", "copy", str(silent))
    music = work / "original_music.wav"
    synth_music(music, 696/FPS)
    video = out / "China_Top5_KO_EN.mp4"
    cmd("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent),
        "-i", str(music), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k", "-t", "23.2", "-movflags", "+faststart", str(video))
    info = json.loads(cmd("ffprobe", "-v", "error", "-count_frames",
        "-select_streams", "v:0", "-show_entries",
        "stream=width,height,nb_read_frames,r_frame_rate", "-show_entries",
        "format=duration", "-of", "json", str(video)))
    st = info["streams"][0]
    assert st["width"] == W and st["height"] == H and int(st["nb_read_frames"]) == 696, info
    (out / "source_audit.json").write_text(json.dumps({
        "video": video.name, "subjective_order": True,
        "notes": "This MP4 animates licensed photographs; it is not filmed moving footage.",
        "music": "Original synthesized beat included; no AWOLNATION audio is used.",
        "cut_frames_30fps": MARKERS,
        "license_of_adaptation": "CC BY-SA 4.0; follow attribution and ShareAlike conditions.",
        "attributions": attributions, "ffprobe": info
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "ATTRIBUTION.txt").write_text(
        "CHINA TRAVEL TOP 5 — PHOTO CREDIT & LICENSES\n"
        "Edited images: background blur, crop, typography, animation.\n"
        "Video photo adaptation licensed CC BY-SA 4.0.\n\n" +
        "\n".join(f"{a['place']}: {a['author']} — {a['license']}\n"
                  f"{a['source_url']}\n{a['license_url']}\n" for a in attributions) +
        "\nMusic: original synthesized instrumental (no third-party samples).\n",
        encoding="utf-8")
    print("RENDER_OK", video, "size", video.stat().st_size, flush=True)

if __name__ == "__main__":
    main()
