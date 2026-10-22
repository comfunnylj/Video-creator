#!/usr/bin/env python3
"""Verify two rendered TOP5 mp4s for frame count, dimensions, fps, silent streams."""
import argparse
import json
import subprocess
from pathlib import Path


def call(cmd):
    p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-1300:])
    return p.stdout


def inspect(p):
    obj=json.loads(call(["ffprobe","-v","error","-count_frames","-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames:format=duration","-of","json",p]))
    vids=[s for s in obj["streams"] if s.get("codec_type")=="video"]
    aud=[s for s in obj["streams"] if s.get("codec_type")=="audio"]
    if len(vids)!=1:
        raise AssertionError("Expected exactly one video stream")
    v=vids[0]
    n=int(v.get("nb_read_frames",0))
    wh=(v["width"],v["height"])
    expected=(360,640) if "DRAFT" in Path(p).name else (1080,1920)
    secs=float(obj["format"]["duration"])
    check=(wh==expected and n==696 and v["r_frame_rate"]=="30/1" and not aud and abs(secs-23.2)<.04)
    if not check:
        raise AssertionError(f"Metadata mismatch: {p}: {wh=}, {n=}, {secs=}, audio={len(aud)}, fps={v['r_frame_rate']}")
    call(["ffmpeg","-hide_banner","-loglevel","error","-i",p,"-f","null","-"])
    return {"path":str(p),"frames":n,"width":wh[0],"height":wh[1],"seconds":secs,"audio_streams":len(aud),"decode":"ok"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+",type=Path)
    args=ap.parse_args()
    for p in args.videos:
        print(json.dumps(inspect(p),ensure_ascii=False))
    print("PASS: technical checks only; geographical identity and licensed rights must be verified separately")

if __name__=="__main__":
    main()