#!/usr/bin/env python3
"""Daily Quote Maker v1.0: a verifiable high-quality real-photo quote card renderer."""
from __future__ import annotations
import argparse, hashlib, io, json, os, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

MAX_DOWNLOAD = 38 * 1024 * 1024
FONT_PATHS = (
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
def get_font(size):
    for path in FONT_PATHS:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise RuntimeError("Korean serif font unavailable")

def source_file(job, dest:Path)->bytes:
    media=job["photo"]
    url=media.get("download_url", "").strip()
    if not url.startswith("https://"):
        raise ValueError("Require approved direct HTTPS download URL")
    if not media.get("source_url") or not media.get("photographer"):
        raise ValueError("Provenance (source page + photographer) required")
    if any(k in url.lower() for k in ("timelapse", "hyperlapse", "video")):
        raise ValueError("Quote photo mode never accepts video/timelapse")
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 DailyQuoteMaker/1.0","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"})
    with urllib.request.urlopen(req,timeout=60) as resp:
        if resp.headers.get("Content-Length") and int(resp.headers["Content-Length"])>MAX_DOWNLOAD:
            raise RuntimeError("Photo download too large")
        data=resp.read(MAX_DOWNLOAD+1)
    if len(data)>MAX_DOWNLOAD: raise RuntimeError("Too large")
    if len(data)<40_000: raise RuntimeError("Source file too small")
    dest.write_bytes(data)
    return data

def wrap_text(text, draw, font, max_width):
    # Preserve intentional lines, otherwise wrap at whole-word or Hangul-character boundaries.
    lines=[]
    for raw in text.split("\n"):
        line=""
        for ch in raw:
            test=line+ch
            if draw.textbbox((0,0),test,font=font)[2]>max_width and line:
                lines.append(line.strip())
                line=ch
            else:
                line=test
        lines.append(line.strip())
    return [x for x in lines if x]

def make_card(source, outpath, quote, byline, width, height, position_y):
    src=ImageOps.exif_transpose(Image.open(io.BytesIO(source))).convert("RGB")
    sw,sh=src.size
    if min(sw,sh)<1800 or max(sw,sh)<3000:
        raise RuntimeError(f"Reject blurry/low-resolution original: {sw}x{sh}, require >=1800 short and >=3000 long")
    # Require native pixels for target crop, not faux-upscaled resolution.
    cut_w=min(sw,sh*width/height)
    cut_h=min(sh,sw*height/width)
    if cut_w<width or cut_h<height:
        raise RuntimeError(f"Insufficient native pixels for {width}x{height} crop")
    # Center crop; photographic compositional selection may be adjusted via crop_x/y.
    picture=ImageOps.fit(src,(width,height),method=Image.Resampling.LANCZOS,centering=(0.5,0.48))
    overlay=Image.new("RGBA",(width,height),(0,0,0,0))
    od=ImageDraw.Draw(overlay)
    # Gentle middle shading (not a title box).
    center=int(height*position_y)
    for y in range(max(0,center-int(height*.22)),min(height,center+int(height*.20))):
        frac=abs(y-center)/float(height*.23)
        opacity=max(0,int(60*(1-frac)))
        od.line((0,y,width,y),fill=(11,16,24,opacity),width=1)
    font=get_font(max(30,round(width*.043)))
    small=get_font(max(18,round(width*.025)))
    text=wrap_text(quote,od,font,int(width*.82))
    if len(text)>6:
        raise ValueError("Quote too long for calm minimalist card; select a shorter verified excerpt")
    line_h=int(font.size*1.72)
    total=len(text)*line_h+line_h*.9
    start=int(center-total/2)
    if start<int(height*.16) or start+total>height*.80:
        raise ValueError("Typography exceeds safe central range")
    for i,line in enumerate(text):
        bounds=od.textbbox((0,0),line,font=font,stroke_width=1)
        x=(width-(bounds[2]-bounds[0]))//2
        y=start+i*line_h
        od.text((x,y),line,font=font,fill=(250,249,246,255),
                anchor=None,stroke_width=2,stroke_fill=(10,12,19,145))
    attribution="— "+byline
    bounds=od.textbbox((0,0),attribution,font=small)
    x=(width-(bounds[2]-bounds[0]))//2
    od.text((x,start+len(text)*line_h+int(line_h*.25)),attribution,font=small,
            fill=(248,248,246,232),stroke_width=1,stroke_fill=(12,12,15,150))
    result=Image.alpha_composite(picture.convert("RGBA"),overlay).convert("RGB")
    result.save(outpath,format="JPEG",quality=95,subsampling=0,optimize=True)
    return {"source_width":sw,"source_height":sh,"crop_native_width":round(cut_w),
            "crop_native_height":round(cut_h),"output_width":width,"output_height":height}

def run(job_path:Path,output:Path):
    job=json.loads(job_path.read_text(encoding="utf-8"))
    quote=job["quote"].strip()
    author=job["author"].strip()
    work=job["work"].strip()
    if not quote or not author or not work: raise ValueError("Quote, author and work required")
    if not job.get("quote_id") or not re.fullmatch(r"Q\d{4}",job["quote_id"]):
        raise ValueError("Quote ID (Q0001) required for dedup")
    if not job.get("source_verified"): raise RuntimeError("Human-verified exact quotation required")
    if job.get("photo",{}).get("timelapse") or job.get("photo",{}).get("ai_generated"):
        raise RuntimeError("Photo must be genuine, non-timelapse still image")
    output.mkdir(parents=True,exist_ok=True)
    data=source_file(job,output/"original_photo")
    name=job["quote_id"]+"_daily_quote"
    formats=[("IG_4x5",1080,1350,.46),("STORY_9x16",1080,1920,.44)]
    results=[]
    for suffix,w,h,pos in formats:
        path=output/(name+"_"+suffix+".jpg")
        meta=make_card(data,path,quote,author+" · "+work,w,h,pos)
        results.append({"filename":path.name,"bytes":path.stat().st_size,**meta})
    provenance={
        "quote_id":job["quote_id"],"quote":quote,"author":author,"work":work,
        "quote_reference":job.get("quote_reference",""),"caption":job.get("caption",""),
        "media_source":job["photo"]["source_url"],"photographer":job["photo"]["photographer"],
        "original_sha256":hashlib.sha256(data).hexdigest(),
        "outputs":results,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "publication_status":"NOT_PUBLISHED","capture_type":"REAL_STILL_IMAGE_NO_TIMELAPSE",
    }
    (output/(name+"_provenance.json")).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"success":True,"results":results,"quote_id":job["quote_id"]},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--job",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("output_quote_cards"))
    args=parser.parse_args()
    run(args.job,args.output)
