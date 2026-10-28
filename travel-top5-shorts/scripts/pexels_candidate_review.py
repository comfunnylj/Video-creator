#!/usr/bin/env python3
import urllib.request,urllib.error,json,time,io,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
photos=[
("HONGYA",14741960,"WC OY"),("HONGYA",14785197,"Tom Zhou"),("HONGYA",11975552,"Chengxin Zhao"),
("LIRIVER",36535019,"Willian Justen"),("LIRIVER",36398296,"Willian Justen"),("LIRIVER",36535024,"Willian Justen"),("LIRIVER",36398286,"Willian Justen"),
("ZHANGJIAJIE",33231936,"Deimantas Viburys"),("ZHANGJIAJIE",33231945,"Deimantas Viburys"),("ZHANGJIAJIE",33231933,"Deimantas Viburys"),
("LIJIANG",5204101,"STEVE CHAI"),("LIJIANG",10670163,"Franklin David"),("LIJIANG",34644900,"David Tran"),("LIJIANG",32205195,"Kunanon Kongsomwach"),
("WANGXIAN",22043310,"jason hu"),("WANGXIAN",33933702,"Happiness 44"),("WANGXIAN",33933703,"Happiness 44"),("WANGXIAN",22043319,"jason hu"),
]
root=Path("pexels_review");root.mkdir(exist_ok=True)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
records=[];tiles=[]
for kind,id,author in photos:
 url=f"https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=1000"
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; TravelTop5Review/1.0)"})
 try:
  with urllib.request.urlopen(req,timeout=40) as resp:data=resp.read(4000000)
  im=Image.open(io.BytesIO(data)).convert("RGB")
  im.save(root/f"{kind}_{id}.jpg",quality=88)
  r={"id":id,"place":kind,"photographer":author,"source":f"https://www.pexels.com/photo/{id}/","image_url":url,"width":im.width,"height":im.height}
  records.append(r)
  thumb=ImageOps.contain(im,(320,430))
  tile=Image.new("RGB",(340,472),"#111111");tile.paste(thumb,((340-thumb.width)//2,(430-thumb.height)//2))
  draw=ImageDraw.Draw(tile);draw.text((10,437),f"{kind} {id}",font=font,fill="white");tiles.append(tile)
  print("PHOTO",kind,id,im.size,flush=True)
 except Exception as e:
  print("FAILED",kind,id,str(e)[:250],flush=True)
  tile=Image.new("RGB",(340,472),"#551111")
  ImageDraw.Draw(tile).text((10,437),f"FAILED {id}",font=font,fill="white")
  tiles.append(tile)
board=Image.new("RGB",(340*6,472*math.ceil(len(tiles)/6)),"black")
for i,im in enumerate(tiles):board.paste(im,((i%6)*340,(i//6)*472))
board.save(root/"PEXELS_BOARD.jpg",quality=88)
(root/"sources.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
