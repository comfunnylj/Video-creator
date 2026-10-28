#!/usr/bin/env python3
"""Render public-download fallback for China Top5, matching user's ~23-second reference.
Five actual Pexels photographs animated subtly. No audio track.
"""
import io, json, math, os, subprocess, urllib.request, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS = 720, 1280, 30
ROOT = Path("output_verified")
ROOT.mkdir(exist_ok=True)
IMAGE_DIR = ROOT / "images"
IMAGE_DIR.mkdir(exist_ok=True)
OUT = ROOT / "China_Top5_Reference_Style_SILENT.mp4"
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumSquareEB.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]
FONT_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
def font(sz, bold=True):
    for candidate in FONT_BOLD_CANDIDATES if bold else FONT_REG_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, sz)
    raise RuntimeError("Korean font not installed")
PLACES = [
    {"rank": 5,"name":"충칭 홍야동","eng":"HONGYADONG","detail":"황금빛 야경의 절벽마을","id":14741960,"author":"WC OY"},
    {"rank": 4,"name":"구이린 리강","eng":"LI RIVER","detail":"산수화처럼 펼쳐지는 절경","id":36535019,"author":"Willian Justen"},
    {"rank": 3,"name":"장가계","eng":"ZHANGJIAJIE","detail":"구름 위로 솟은 사암 봉우리","id":33231936,"author":"Deimantas Viburys"},
    {"rank": 2,"name":"윈난 리장","eng":"LIJIANG","detail":"설산 아래 빛나는 고성 지붕","id":5204101,"author":"STEVE CHAI"},
    {"rank": 1,"name":"장시 망선곡","eng":"WANGXIAN VALLEY","detail":"계곡을 따라 들어선 산속 마을","id":22043310,"author":"jason hu"}
]
SEGMENTS = [
    ("intro",0,90,None),("rank",90,119,0),("scene",119,206,0),
    ("rank",206,241,1),("scene",241,323,1),
    ("rank",323,359,2),("scene",359,447,2),
    ("rank",447,482,3),("scene",482,574,3),
    ("rank",574,604,4),("scene",604,689,4)
]
def grab_p(j):
    ident = p["id"]
    url = f"https://images.pexels.com/photos/{ident}/pexels-photo-{ident}.jpeg?auto=compress&cs=tinysrgb&w=1000"
    req = urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (TravelTop5Renderer/2.0)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                b = response.read(8_000_001)
            if len(b) > 8_000_000 or len(b) < 6000:
                raise ValueError("Invalid image size")
            pic = Image.open(io.BytesIO(b)).convert("RGB")
            pic.save(IMAGE_DIR / f"{ident}.jpg",quality=88)
            return pic, url
        except Exception as exc:
            if attempt == 3: raise
            time.sleep(2 + attempt)
def star(draw,x,y,r):
    pts=[]
    for i in range(10):
        a=(-90+i*36)*math.pi/180
        rad=r if i%2==0 else r*.42
        pts.append((x+rad*math.cos(a),y+rad*math.sin(a)))
    draw.polygon(pts, fill=(255,221,36))
def flag(im,x,y,w=62,h=43):
    d=ImageDraw.Draw(im)
    d.rectangle((x,y,x+w,y+h), fill=(222,23,32))
    star(d,x+w*.19,y+h*.30,7)
    for dx,dy in [(0.38,.15),(.48,.31),(.48,.52),(.38,.70)]:
        star(d,x+w*dx,y+h*dy,2.4)
def labeled(d,pos,t,size,color="white"):
    d.text(pos,t,font=font(size),fill=color,stroke_width=3,stroke_fill="black")
def rank_screen(p):
    im=Image.new("RGB",(W,H),"black")
    d=ImageDraw.Draw(im)
    flag(im,329,532,62,43)
    def center(y,t,size,color="white"):
        f=font(size)
        bb=d.textbbox((0,0),t,font=f)
        d.text(((W-(bb[2]-bb[0]))/2,y),t,font=f,fill=color)
    center(598,"중국",37)
    center(656,"CHINA",24)
    center(710,f"TOP {p['rank']}",23,"#b8b8b8")
    return np.array(im)
def size_to_crop(pic):
    iw,ih=pic.size
    scale=max((W*1.18)/iw,(H*1.18)/ih)
    tw,th=round(iw*scale),round(ih*scale)
    if max(tw,th)>4000:
        f=4000/max(tw,th)
        tw,th=int(tw*f),int(th*f)
    pic=pic.resize((tw,th),Image.Resampling.LANCZOS)
    if tw < W or th < H:
        pic=ImageOps.fit(pic,(int(W*1.18),int(H*1.18)),method=Image.Resampling.LANCZOS)
    return np.array(pic)
images=[]; attributions=[]
for p in PLACES:
    picture, url=grab_p(p)
    images.append(size_to_crop(picture))
    attributions.append(f"TOP {p['rank']} {p['name']} - {p['author']} - Pexels License - https://www.pexels.com/photo/{p['id']}/")
    print("PHOTO",p["name"],picture.size,flush=True)
cards=[rank_screen(p) for p in PLACES]
def frame_from_array(arr,k,n,side):
    ih,iw=arr.shape[:2]
    wx,wy=iw-W,ih-H
    f=k/max(1,n-1)
    dx=min(wx*.30,96)
    x=int(wx/2 + ((-1 if side%2==0 else 1)*dx*(f-.5)*2))
    y=int(wy/2 + min(wy*.15,22)*math.sin(f*math.pi*1.1))
    x=max(0,min(wx,x))
    y=max(0,min(wy,y))
    return Image.fromarray(arr[y:y+H,x:x+W])
cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo",
     "-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
     "-an","-c:v","libx264","-preset","veryfast","-crf","20",
     "-pix_fmt","yuv420p","-movflags","+faststart",str(OUT)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    for mode,start,end,target in SEGMENTS:
        n=end-start
        for k in range(n):
            if mode=="rank":
                frame=cards[target]
            else:
                i=2 if mode=="intro" else target
                im=frame_from_array(images[i],k,n,i)
                d=ImageDraw.Draw(im)
                if mode=="intro":
                    labeled(d,(32,58),"중국 비현실적인",42)
                    labeled(d,(32,115),"여행지",42)
                    labeled(d,(185,114),"TOP5",43,(247,213,95))
                else:
                    place=PLACES[target]
                    flag(im,34,61,54,36)
                    labeled(d,(100,56),"중국 China",30)
                    labeled(d,(34,107),f"TOP {place['rank']}  {place['name']}  |  {place['eng']}",26)
                    labeled(d,(34,145),place["detail"],26)
                frame=np.asarray(im)
            p.stdin.write(frame.tobytes())
        print("SEGMENT",mode,start,end,flush=True)
    p.stdin.close()
    err=p.stderr.read().decode("utf8","replace")
    status=p.wait()
    if status: raise RuntimeError("ffmpeg "+str(status)+" "+err[-4000:])
except Exception:
    p.kill()
    raise
info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(OUT)]))
assert len(info["streams"])==1 and info["streams"][0]["codec_type"]=="video",info
assert int(info["streams"][0]["nb_frames"])==689,info
assert abs(float(info["format"]["duration"])-689/FPS)<0.04,info
(ROOT/"SOURCE_CREDITS.txt").write_text(
    "China Top 5 - photo-motion adaptation; 0 audio streams.\n"
    "Each photograph from the specifically named Pexels location, under https://www.pexels.com/license/.\n"
    "Photographs cropped, animated, captioned. Order is subjective.\n\n"+"\n".join(attributions)+"\n",encoding="utf8")
print("OUTPUT_SUCCESS",OUT,OUT.stat().st_size,flush=True)
