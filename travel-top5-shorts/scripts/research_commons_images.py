#!/usr/bin/env python3
"""Build review contact sheets of Wikimedia Commons photographs by named location."""
import json,urllib.parse,urllib.request,io,re,sys,os,time,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont

cats=[
("WANGXIAN","Category:Wangxian Valley"),
("LIJIANG","Category:Views of Lijiang Old Town"),
("HONGYADONG","Category:Hongya Cave"),
("ZHANGJIAJIE","Category:Zhangjiajie National Forest Park"),
("LIRIVER","Category:Li River"),
]
out=Path("commons_research");out.mkdir(exist_ok=True)
opener=urllib.request.build_opener()
def api(params):
  url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json",**params})
  req=urllib.request.Request(url,headers={"User-Agent":"TravelTop5Research/1.0 (https://github.com/comfunnylj/Video-creator)"})
  for i in range(3):
    try:
      with opener.open(req,timeout=45) as r:return json.load(r)
    except Exception as e:
      if i==2:raise
      time.sleep(1+i)
def download(url):
 req=urllib.request.Request(url,headers={"User-Agent":"TravelTop5Research/1.0 (https://github.com/comfunnylj/Video-creator)"})
 with opener.open(req,timeout=30) as r:return r.read(2_500_000)
def strip(html):
 return re.sub("<[^>]*>","",html or "").strip()[:180]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
for name,cat in cats:
 try:
  pages=[]
  try:
   data=api({"generator":"categorymembers","gcmtitle":cat,"gcmtype":"file","gcmlimit":"60","prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":"310"})
   pages=list(data.get("query",{}).get("pages",{}).values())
  except Exception as exc:print(cat,"API_ERR",repr(exc),flush=True)
  if not pages:continue
  pages=sorted(pages,key=lambda p:p.get("title",""))
  meta=[];tiles=[]
  for idx,p in enumerate(pages):
   infos=p.get("imageinfo",[]); info=infos[0] if infos else {}
   x=info.get("extmetadata",{})
   record={"title":p["title"],"url":info.get("url"),"thumburl":info.get("thumburl"),
      "width":info.get("width"),"height":info.get("height"),
      "license":x.get("LicenseShortName",{}).get("value",""),
      "author":strip(x.get("Artist",{}).get("value","")),
      "description":strip(x.get("ImageDescription",{}).get("value",""))}
   meta.append(record)
   try:
    b=download(record["thumburl"] or record["url"])
    im=Image.open(io.BytesIO(b)).convert("RGB")
    image=Image.new("RGB",(330,246),"#141414")
    tile=ImageOps.contain(im,(326,210))
    image.paste(tile,((330-tile.width)//2,(210-tile.height)//2))
    draw=ImageDraw.Draw(image)
    title=record["title"].replace("File:","")
    if len(title)>41:title=title[:38]+"..."
    draw.text((5,213),f"{idx:02} {title}",font=font,fill="white")
    tiles.append(image)
   except Exception as e:print("IMG_ERR",name,idx,str(e)[:200],flush=True);tiles.append(Image.new("RGB",(330,246),"#441111"))
  ncols=5; board=Image.new("RGB",(330*ncols,246*math.ceil(len(tiles)/ncols)),"#141414")
  for i,im in enumerate(tiles):board.paste(im,((i%ncols)*330,(i//ncols)*246))
  board.save(out/f"{name}_candidates.jpg",quality=83)
  (out/f"{name}_metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf8")
  print("DONE",name,len(tiles),flush=True)
 except Exception as e:print("FAILED",name,str(e)[:500],flush=True)
