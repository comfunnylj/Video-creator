#!/usr/bin/env python3
"""Build (not submit) immutable, source-checked Instagram and Threads outbox envelopes."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

def build(img_path:Path,prov_path:Path,immutable_url:str,day:str,allow:bool):
    prov=json.loads(prov_path.read_text(encoding="utf-8"))
    src=img_path.read_bytes()
    sha=hashlib.sha256(src).hexdigest()
    if not allow:
        raise RuntimeError("Explicit approved-for-posting gate is required; producing an image is not publication permission")
    if not immutable_url.startswith("https://raw.githubusercontent.com/comfunnylj/telegram-market-feed/"):
        raise ValueError("Only allow pinned GitHub image from publisher repo")
    if not re.search(r"/[0-9a-f]{40}/",immutable_url):
        raise ValueError("Require immutable 40-character Git commit in URL")
    if not (30_000 <= len(src) < 8_000_000):
        raise ValueError("JPEG size must fit both Meta platforms")
    if prov.get("publication_status") not in ("NOT_PUBLISHED","READY_FOR_REVIEW"):
        raise ValueError("Already-published or unknown provenance not accepted")
    from PIL import Image
    with Image.open(img_path) as im:
        if im.format!="JPEG" or im.size!=(1080,1350):
            raise ValueError("Only 1080x1350 4:5 JPEG allowed")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",day):
        raise ValueError("date must be YYYY-MM-DD")
    day_obj=datetime.strptime(day,"%Y-%m-%d").replace(tzinfo=ZoneInfo("Asia/Seoul"))
    quote_id=prov["quote_id"]
    caption=prov.get("caption","")
    if not caption.strip(): raise ValueError("Nonempty caption required")
    instagram_at=day_obj.replace(hour=9,minute=0)
    threads_at=day_obj.replace(hour=9,minute=10)
    if day_obj < datetime.now(ZoneInfo("Asia/Seoul")).replace(hour=0,minute=0,second=0,microsecond=0):
        raise ValueError("Cannot create scheduled job for a past date")
    # No 2nd identifier for retry: caller must reconcile already accepted ids.
    base=f"quote:{day}:{quote_id}"
    instagram={
      "dedup_key":"instagram:"+base, "approved":True,
      "not_before":instagram_at.isoformat(),
      "expires_at":(instagram_at+timedelta(minutes=15)).isoformat(),
      "caption":caption,
      "media_type":"image",
      "media":[{"url":immutable_url,"sha256":sha,"size":len(src)}],
    }
    # Threads 450 UTF-16 unit limit - no splitting: 1 card/1 root post.
    text=f'{prov["quote"]}\n\n— {prov["author"]}, {prov["work"]}\n\n{caption}'
    units=len(text.encode("utf-16-le"))//2
    if units>450: raise ValueError(f"Threads caption {units} UTF16 units >450, edit excerpt")
    threads={
       "dedup_key":base,
       "created_at":datetime.now(timezone.utc).isoformat(),
       "not_before":threads_at.isoformat(),
       "expires_at":(threads_at+timedelta(minutes=5)).isoformat(),
       "topic":"기타",
       "text":text,"parts":[text],
       "image":{"url":immutable_url,"sha256":sha,"size":len(src)},
    }
    return instagram,threads

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--image",type=Path,required=True)
    parser.add_argument("--provenance",type=Path,required=True)
    parser.add_argument("--immutable-url",required=True)
    parser.add_argument("--date",required=True)
    parser.add_argument("--approved-for-posting",action="store_true")
    parser.add_argument("--output",type=Path,default=Path("quote_payloads"))
    args=parser.parse_args()
    ig,th=build(args.image,args.provenance,args.immutable_url,args.date,args.approved_for_posting)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"instagram_job.json").write_text(json.dumps(ig,ensure_ascii=False,indent=2)+"\n")
    (args.output/"threads_job.json").write_text(json.dumps(th,ensure_ascii=False,indent=2)+"\n")
    print("Local payloads prepared. NOT SUBMITTED OR PUBLISHED.",args.output)
if __name__=="__main__": main()
