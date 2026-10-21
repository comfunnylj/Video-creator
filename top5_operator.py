#!/usr/bin/env python3
"""Issue-driven Travel Top5 video renderer. Demo is synthetic and never depicts real hotels."""
import argparse, json, os, re, subprocess, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime, timezone

def run(argv):
    p=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("FFmpeg failed: "+p.stderr[-2500:])

def valid_name(s):
    return isinstance(s,str) and 1<=len(s)<=90 and not any(ord(c)<32 for c in s)

def quote_ass(s):
    return str(s).replace("\\","").replace("{","").replace("}","").replace("\n"," ").replace("\r"," ")

def ass(path,text,width,height):
    size=29 if width==540 else 37
    prefix=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,NanumGothic,{size},&H00FFFFFF,&H000000FF,&H77000000,&H77000000,-1,0,0,0,100,100,0,0,1,3,1,8,25,25,125,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
Dialogue: 0,0:00:00.00,0:00:06.00,Default,,0,0,0,,{quote_ass(text)}
"""
    path.write_text(prefix,encoding="utf8")

def download(url,out):
    u=urllib.parse.urlparse(url)
    if u.scheme!="https" or not u.hostname or not (u.hostname=="pexels.com" or u.hostname.endswith(".pexels.com")):
        raise ValueError("Only HTTPS media from Pexels may be fetched automatically")
    request=urllib.request.Request(url,headers={"User-Agent":"TravelTop5Operator/0.1"})
    with urllib.request.urlopen(request,timeout=90) as response,open(out,"wb") as fp:
        n=0
        while True:
            block=response.read(1024*1024)
            if not block:break
            n+=len(block)
            if n>140*1024*1024:
                raise ValueError("Media exceeds allowed download size")
            fp.write(block)

def project_from_issue(path):
    event=json.loads(Path(path).read_text(encoding="utf8"))
    issue=event.get("issue") or {}
    if (issue.get("user") or {}).get("login")!="comfunnylj":
        raise PermissionError("Only repository owner may start jobs")
    body=issue.get("body") or ""
    if not body.startswith("TOP5_JOB_V1\n"):
        raise ValueError("Issue body lacks TOP5_JOB_V1 header")
    return json.loads(body.split("\n",1)[1])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--job",help="Local JSON job")
    ap.add_argument("--issue-event",help="GitHub event JSON path")
    ap.add_argument("--output-dir",default="output")
    args=ap.parse_args()
    if bool(args.job)==bool(args.issue_event):
        ap.error("Choose exactly one of --job and --issue-event")
    job=project_from_issue(args.issue_event) if args.issue_event else json.loads(Path(args.job).read_text(encoding="utf8"))
    topic=job.get("topic")
    places=job.get("places")
    mode=job.get("mode","demo")
    if not valid_name(topic) or not isinstance(places,list) or len(places)!=5 or mode not in ("demo","approved_media"):
        raise ValueError("Invalid topic, mode or count: requires exactly five places")
    if any(not valid_name(p.get("name")) for p in places if isinstance(p,dict)) or any(not isinstance(p,dict) for p in places):
        raise ValueError("Invalid place names")
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    work=out/"work";work.mkdir(exist_ok=True)
    w,h=(540,960) if mode=="demo" else (720,1280)
    fps=24
    paths=[]; sources=[]
    entries=[("INTRO",None)]+[(f"TOP {5-i} | {p['name']}"+(" / "+p["name_en"] if p.get("name_en") else ""),p) for i,p in enumerate(places)]+[("Follow for more travel ideas",None)]
    for i,(label,place) in enumerate(entries):
        dur=2.0 if place is None else 5.2
        sub=work/f"subtitle_{i}.ass";ass(sub,label,w,h)
        item=work/f"clip_{i}.mp4"
        if place is not None and mode=="approved_media":
            media=place.get("media") or {}
            if not (place.get("place_verified") is True and media.get("approved") is True and media.get("license_checked") is True and media.get("source_url") and media.get("credit")):
                raise ValueError("Real-place identity, source and commercial use require approval")
            source=work/f"source_{i}.mp4"
            download(media["download_url"],source)
            inp=["-stream_loop","-1","-i",str(source)]
            vf=f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},ass={sub}"
            sources.append({"place":place["name"],"source":media["source_url"],"credit":media["credit"],"license":media.get("license","reviewed by operator")})
        else:
            # Never depict or imply the colored placeholder is genuine footage.
            colors=["0x1c354e","0x154957","0x54486c","0x28556b","0x475872","0x324567","0x1c354e"]
            inp=["-f","lavfi","-i",f"color=c={colors[i]}:s={w}x{h}:r={fps}:d={dur}"]
            vf=f"fps={fps},ass={sub}"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y",*inp,"-t",str(dur),"-vf",vf,"-an","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",str(item)])
        paths.append(item)
    concat=work/"concat.txt"
    concat.write_text("".join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in paths),encoding="utf8")
    video=out/"top5.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-map","0:v","-map","1:a","-t","30","-c:v","copy","-c:a","aac","-b:a","96k","-movflags","+faststart",str(video)])
    meta={"topic":topic,"mode":mode,"created_at":datetime.now(timezone.utc).isoformat(),"places":[p["name"] for p in places],"sources":sources,"notice":("SYNTHETIC DEMO -- NOT REAL PLACE FOOTAGE" if mode=="demo" else "operator approved commercial media")}
    (out/"metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf8")
    print("RENDER_OK",video,"bytes",video.stat().st_size)

if __name__=="__main__":
    main()
