#!/usr/bin/env python3
"""Render the established 696-frame TOP5 template from verified local footage.

Does NOT download videos, decide licenses, use an API key, or include music.
"""
import argparse
import csv
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FPS = 30
TOTAL = 696
INTRO = 91
SLATE = 30
VIEW = 91
BOUNDARIES = [0,91,121,212,242,333,363,454,484,575,605,696]
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/malgun.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
]


def run(cmd):
    p = subprocess.run(list(map(str, cmd)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str,cmd[:8]))}\n{p.stderr[-2000:]}")
    return p.stdout


def font_path(value=None):
    if value and Path(value).exists():
        return value
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    if shutil.which("fc-match"):
        p = run(["fc-match", "-f", "%{file}", "Noto Sans CJK KR"]).strip()
        if Path(p).exists():
            return p
    raise RuntimeError("No Korean-capable font found. Install Noto Sans CJK KR or pass font_path in manifest.")


def fn(path, size):
    return ImageFont.truetype(str(path), max(10, int(size)))


def font_fit(draw, text, fp, size, width):
    while size >= 17:
        f = fn(fp, size)
        b = draw.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= width:
            return f
        size -= 2
    return fn(fp, 17)


def centered(draw, text, y, fp, size, w, color="white"):
    draw.text((w/2, y), text, fill=color, font=font_fit(draw, text, fp, size, w*.87), anchor="mm", stroke_width=1, stroke_fill="black")


def slate_png(item, lang, out, dims, font):
    w, h = dims
    s = w / 1080
    bg = Image.new("RGB", dims, (11, 18, 29))
    d = ImageDraw.Draw(bg)
    accent = (255, 218, 93)
    d.rectangle((0, 0, max(2, int(10*s)), h), fill=accent)
    d.rounded_rectangle((int(68*s),int(280*s),int(1010*s),int(1515*s)), radius=int(35*s), outline=(85,95,110), width=max(1,int(3*s)))
    centered(d, f"{item['rank']:02}", int(590*s), font, 188*s, w)
    centered(d, "TOP 5", int(940*s), font, 94*s, w, accent)
    name = item["country_ko"] if lang == "ko" else item["country_en"]
    centered(d, name, int(1155*s), font, 94*s, w)
    centered(d, "REAL PLACES", int(1420*s), font, 40*s, w, (199,208,219))
    bg.save(out)


def overlay_png(item, lang, out, dims, font):
    w, h = dims
    s = w/1080
    img = Image.new("RGBA", dims, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    title = item["place_ko"] if lang == "ko" else item["place_en"]
    sub = item["place_en"] if lang == "ko" else item["country_en"]
    # The user's requested safe zone: top left, no text in the lower-left area.
    x = int(80*s)
    title_f = font_fit(d, title, font, int(54*s), int(860*s))
    sub_f = font_fit(d, sub, font, int(34*s), int(860*s))
    a = d.textbbox((0,0),title,font=title_f)
    b = d.textbbox((0,0),sub,font=sub_f)
    bw = min(int(1015*s), x + max(a[2]-a[0], b[2]-b[0]) + int(44*s))
    d.rounded_rectangle((int(52*s),int(260*s),max(bw,int(390*s)),int(462*s)), radius=int(21*s), fill=(5,12,22,205))
    d.text((x,int(294*s)),f"#{item['rank']}  {title}",font=title_f,fill="white",stroke_width=1,stroke_fill=(0,0,0,170))
    d.text((x,int(386*s)),sub,font=sub_f,fill=(215,232,242))
    img.save(out)


def intro_png(config, lang, out, dims, font):
    w,h = dims
    s = w/1080
    img=Image.new("RGBA",dims,(3,9,14,100))
    d=ImageDraw.Draw(img)
    title=config[f"title_{lang}"]
    d.rounded_rectangle((int(308*s),int(660*s),int(772*s),int(730*s)),radius=int(25*s),fill=(255,218,93,255))
    centered(d,"TOP 5",int(695*s),font,42*s,w,(7,14,24))
    # Break lines explicitly for long titles by comma or spaces if needed.
    words = title.split()
    if len(words) > 5:
        split = (len(words)+1)//2
        lines=[' '.join(words[:split]),' '.join(words[split:])]
    else:
        lines=[title]
    for i,line in enumerate(lines):
        centered(d,line,int((990+135*(i-(len(lines)-1)/2))*s),font,80*s,w)
    centered(d,"5 REAL PLACES  /  23 SECONDS",int(1330*s),font,35*s,w)
    img.save(out)


def duration(path):
    info=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path]))
    return float(info["format"]["duration"])


def encode(out, source, start, frames, dims, anchor=.5, overlay=None):
    w,h=dims
    vf=f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}:(in_w-out_w)*{anchor}:(in_h-out_h)/2,setsar=1"
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",str(source)]
    if overlay:
        cmd.extend(["-loop","1","-framerate",str(FPS),"-i",str(overlay),"-filter_complex",f"[0:v]{vf}[base];[base][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[v]","-map","[v]"])
    else:
        cmd.extend(["-vf",vf])
    cmd.extend(["-frames:v",str(frames),"-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-r",str(FPS),"-movflags","+faststart",str(out)])
    run(cmd)


def still(out, overlay, frames, dims):
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),"-i",str(overlay),"-frames:v",str(frames),"-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-r",str(FPS),str(out)])


def validate_sources(config, base):
    places=config.get("places", [])
    if len(places)!=5 or [p.get("rank") for p in places]!=[5,4,3,2,1]:
        raise ValueError("Exactly 5 places with ranks [5,4,3,2,1] are required")
    must=["place_ko","place_en","country_ko","country_en","footage","source_url","license_url","source_creator","location_evidence","rights_checked_date"]
    for p in places:
        for field in must:
            if not str(p.get(field,"")).strip() or str(p[field]).upper() in {"REPLACE","YYYY-MM-DD"} or "example.org" in str(p[field]):
                raise ValueError(f"Rank {p['rank']}: unverified or empty {field}; use real source metadata")
        path=base / p["footage"]
        if not path.is_file():
            raise FileNotFoundError(path)
        start=float(p.get("trim_start",0))
        if start<0 or duration(path)<start+VIEW/FPS-0.02:
            raise ValueError(f"Insufficient clip duration: {path}")
        if not 0<=float(p.get("crop_x",.5))<=1:
            raise ValueError("crop_x must be in [0, 1]")
    intro=base/config.get("intro_footage",places[0]["footage"])
    if not intro.exists():
        raise FileNotFoundError(intro)
    if duration(intro)<float(config.get("intro_trim_start",0))+INTRO/FPS-.02:
        raise ValueError("Insufficient intro footage")
    return places, intro


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest",type=Path)
    ap.add_argument("--output-dir",default=None,type=Path)
    ap.add_argument("--draft",action="store_true",help="Quick QA-sized 360x640 render, SAME 696-frame timing")
    args=ap.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe are required")
    mf=args.manifest.resolve()
    config=json.loads(mf.read_text(encoding="utf-8"))
    base=mf.parent
    places,intro=validate_sources(config,base)
    out=(args.output_dir or base/"outputs").resolve()
    out.mkdir(parents=True,exist_ok=True)
    build=out/"_build"
    build.mkdir(exist_ok=True)
    dims=(360,640) if args.draft else (1080,1920)
    font=font_path(config.get("font_path"))
    print("Font:",font)
    for lang in ("ko","en"):
        seg=[]
        intro_ov=build/f"intro_{lang}.png"
        intro_png(config,lang,intro_ov,dims,font)
        intro_seg=build/f"seg_{lang}_intro.mp4"
        encode(intro_seg,intro,float(config.get("intro_trim_start",0)),INTRO,dims,.5,intro_ov)
        seg.append(intro_seg)
        for p in places:
            rank=p["rank"]
            rank_png=build/f"slate_{lang}_{rank}.png"
            slate_png(p,lang,rank_png,dims,font)
            rank_seg=build/f"seg_{lang}_{rank}_slate.mp4"
            still(rank_seg,rank_png,SLATE,dims)
            seg.append(rank_seg)
            ov=build/f"overlay_{lang}_{rank}.png"
            overlay_png(p,lang,ov,dims,font)
            footage_seg=build/f"seg_{lang}_{rank}_view.mp4"
            encode(footage_seg,base/p["footage"],float(p.get("trim_start",0)),VIEW,dims,float(p.get("crop_x",.5)),ov)
            seg.append(footage_seg)
        concat=build/f"concat_{lang}.txt"
        concat.write_text(''.join("file '"+s.as_posix().replace("'","'\\''")+"'\n" for s in seg),encoding="utf-8")
        dest=out/f"top5_{lang}_{'DRAFT_' if args.draft else ''}SILENT.mp4"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,"-c","copy","-an","-movflags","+faststart",dest])
        print("Rendered:",dest)
    with (out/"cut_markers.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.writer(f)
        wr.writerow(["segment","start_frame","start_seconds"])
        names=["intro","rank5","view5","rank4","view4","rank3","view3","rank2","view2","rank1","view1","end"]
        for name,n in zip(names,BOUNDARIES):
            wr.writerow([name,n,f"{n/FPS:.3f}"])
    (out/"source_audit.json").write_text(json.dumps(places,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Done: 696 frames at 30 FPS; check with verify_top5.py")

if __name__=="__main__":
    main()