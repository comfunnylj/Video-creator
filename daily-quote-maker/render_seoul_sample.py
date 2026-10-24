#!/usr/bin/env python3
"""A 10-second real Seoul footage quote-card sample (no AI-generated footage).
Source page: https://www.pexels.com/video/scenic-seoul-cityscape-at-twilight-37522118/
Author: Jueon Kim (김주언), Pexels; free license listed by Pexels.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT=Path(os.environ.get("QUOTE_OUTPUT","output_quote_seoul"))
OUT.mkdir(parents=True,exist_ok=True)
SOURCE="https://www.pexels.com/download/video/37522118/"
PAGE="https://www.pexels.com/video/scenic-seoul-cityscape-at-twilight-37522118/"
source=OUT/"seoul_stock.mp4"
cmd=["curl","--location","--fail","--retry","3","--connect-timeout","25","--max-time","360",
     "-A","Mozilla/5.0","-o",str(source),SOURCE]
subprocess.run(cmd,check=True)
if source.stat().st_size<100_000:
    raise RuntimeError("Stock source is unexpectedly short")
print("Stock file:",source.stat().st_size,flush=True)
p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(source)],capture_output=True,text=True,check=True)
duration=float(json.loads(p.stdout)["format"]["duration"])
print("Source duration:",duration,flush=True)
if duration<4:
    raise RuntimeError("Source is too short for credible moving-video sample")

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
"-stream_loop","-1","-i",str(source),"-loop","1","-i",str(overlay_path),
"-filter_complex",video_filter,"-map","[v]","-an",
"-frames:v","300","-r","30","-c:v","libx264","-preset","fast",
"-crf","20","-movflags","+faststart","-pix_fmt","yuv420p",str(outfile)]
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
"stock_download":SOURCE,"stock_creator":"Jueon Kim 김주언",
"stock_license":"https://www.pexels.com/license/","quote":"너는 누구에게 / 한 번이라도 / 뜨거운 사람이었느냐",
"poet":"안도현","work":"너에게 묻는다","duration_seconds":10,
"resolution":"1080x1920","fps":30,"audio":"none",
"caption":"안도현의 「너에게 묻는다」는 연탄재의 이미지를 통해 누군가에게 온기를 건네는 삶을 돌아보게 합니다. 오늘 당신이 누군가에게 남긴 온기는 무엇인가요?"
}
(OUT/"source_and_caption.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("DONE",outfile,info,flush=True)
