#!/usr/bin/env python3
"""10-second Seoul quote-card renderer with high-resolution, realtime-only source gating.
Previous Pexels stock ID 37522118 is explicitly rejected as an unsuitable example.
Requires a newly reviewed actual recording, not timelapse or a low-quality upscale.
"""
from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT=Path(os.environ.get("QUOTE_OUTPUT","output_quote_seoul"))
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=os.environ.get("QUOTE_SOURCE_URL","").strip()
PAGE=os.environ.get("QUOTE_SOURCE_PAGE","").strip()
CREATOR=os.environ.get("QUOTE_SOURCE_CREATOR","").strip()
CAPTURE_STYLE=os.environ.get("QUOTE_CAPTURE_STYLE","").strip().lower()
REVIEWED=os.environ.get("QUOTE_VISUAL_REVIEWED","").strip().lower()
if not SOURCE or not PAGE or not CREATOR:
    raise RuntimeError("Approved new high-resolution source URL, source page and creator are required")
if "37522118" in SOURCE or "37522118" in PAGE:
    raise RuntimeError("Rejected: previous Seoul stock source produced an unacceptable result")
if CAPTURE_STYLE != "real_time" or REVIEWED != "yes":
    raise RuntimeError("Source must be visually verified as natural-speed realtime footage; no timelapse/hyperlapse")
if any(word in (SOURCE+" "+PAGE).lower() for word in ("timelapse","time-lapse","hyperlapse","speedup","speed-up")):
    raise RuntimeError("Rejected: timelapse or accelerated footage")
source=OUT/"seoul_stock.mp4"
cmd=["curl","--location","--fail","--retry","3","--connect-timeout","25","--max-time","360",
     "-A","Mozilla/5.0","-o",str(source),SOURCE]
subprocess.run(cmd,check=True)
if source.stat().st_size<100_000:
    raise RuntimeError("Stock source is unexpectedly short")
print("Stock file:",source.stat().st_size,flush=True)
p=subprocess.run(["ffprobe","-v","error","-show_entries",
"format=duration:stream=width,height,avg_frame_rate","-select_streams","v:0",
"-of","json",str(source)],capture_output=True,text=True,check=True)
metadata=json.loads(p.stdout)
duration=float(metadata["format"]["duration"])
stream=metadata["streams"][0]
width,height=int(stream["width"]),int(stream["height"])
fps_str=stream.get("avg_frame_rate","0/1")
n,d=map(int,fps_str.split("/"))
source_fps=n/d if d else 0
# An actual native 1080x1920 center crop must exist. Upscaling HD landscape is forbidden.
native_crop_width=min(width,height*9/16)
native_crop_height=min(height,width*16/9)
if native_crop_width<1080 or native_crop_height<1920:
    raise RuntimeError(f"Rejected: original {width}x{height} cannot yield native 1080x1920 portrait crop")
if duration<10 or source_fps<24:
    raise RuntimeError(f"Rejected: source duration={duration:.2f}s fps={source_fps:.2f}; minimum 10s/24fps")
print("Source validated",width,height,duration,source_fps,flush=True)

W,H=1080,1920
overlay=Image.new("RGBA",(W,H),(0,0,0,0))
d=ImageDraw.Draw(overlay)
fontpaths=[
"/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
"/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
fontpath=next((p for p in fontpaths if Path(p).exists()),None)
if not fontpath: raise RuntimeError("Korean font missing")
font=ImageFont.truetype(fontpath,60)
small=ImageFont.truetype(fontpath,30)
for line,y in zip(["너는 누구에게","한 번이라도","뜨거운 사람이었느냐"],[646,738,830]):
    x=(W-d.textbbox((0,0),line,font=font)[2])//2
    d.text((x,y),line,font=font,fill=(255,252,249,255),
           stroke_width=2,stroke_fill=(25,20,25,190))
s="— 안도현 · 너에게 묻는다"
x=(W-d.textbbox((0,0),s,font=small)[2])//2
d.text((x,967),s,font=small,fill=(246,242,242,244),
       stroke_width=1,stroke_fill=(25,20,25,160))
overlay_path=OUT/"quote_overlay.png"
overlay.save(overlay_path)
outfile=OUT/"daily_quote_seoul_andohyeon_sample_10s.mp4"
# Fill full vertical frame with the actual moving footage; show the central region.
# The picture itself is not AI generated or animated from a still.
video_filter=("[0:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,"
              "crop=1080:1920,eq=brightness=-0.07:saturation=0.87,"
              "format=yuv420p[footage];"
              "[footage][1:v]overlay=0:0:shortest=1,"
              "fade=t=in:st=0:d=0.6,fade=t=out:st=9.4:d=0.6,"
              "format=yuv420p[v]")
ff=[
"ffmpeg","-hide_banner","-loglevel","warning","-y",
"-i",str(source),"-loop","1","-i",str(overlay_path),
"-filter_complex",video_filter,"-map","[v]","-an",
"-frames:v","300","-r","30","-c:v","libx264","-preset","fast",
"-crf","18","-movflags","+faststart","-pix_fmt","yuv420p",str(outfile)]
subprocess.run(ff,check=True)
probe=subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
"-show_entries","stream=width,height,nb_frames,r_frame_rate,duration","-of","json",str(outfile)],
capture_output=True,text=True,check=True)
info=json.loads(probe.stdout)["streams"][0]
if int(info["width"])!=1080 or int(info["height"])!=1920 or int(info["nb_frames"])!=300:
    raise RuntimeError("Output failed dimensions/frame count: "+str(info))
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","5",
"-i",str(outfile),"-frames:v","1",str(OUT/"daily_quote_seoul_preview.jpg")],check=True)
manifest={
"footage_type":"real Seoul stock video, NOT AI-generated", "stock_page":PAGE,
"stock_download":SOURCE,"stock_creator":CREATOR,
"source_native_resolution":f"{width}x{height}","source_fps":source_fps,
"capture_style":"real_time","timelapse_excluded":True,"visual_reviewed":True,
"stock_license":"https://www.pexels.com/license/","quote":"너는 누구에게 / 한 번이라도 / 뜨거운 사람이었느냐",
"poet":"안도현","work":"너에게 묻는다","duration_seconds":10,
"resolution":"1080x1920","fps":30,"audio":"none",
"caption":"안도현의 「너에게 묻는다」는 연탄재의 이미지를 통해 누군가에게 온기를 건네는 삶을 돌아보게 합니다. 오늘 당신이 누군가에게 남긴 온기는 무엇인가요?"
}
(OUT/"source_and_caption.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("DONE",outfile,info,flush=True)
