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

def ass(path,text,width,height,kind="place",duration=5.0):
    size=29 if width==540 else 40
    style = "Center" if kind!="place" else "Default"
    caption = r"\N".join(quote_ass(x) for x in text.split("\n"))
    event_end = f"0:00:{duration:05.2f}"
    prefix=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,NanumGothic,{size},&H00FFFFFF,&H000000FF,&H77000000,&H77000000,-1,0,0,0,100,100,0,0,1,4,1,7,32,32,175,1
Style: Center,NanumGothic,{size+6},&H00FFFFFF,&H000000FF,&H77000000,&H77000000,-1,0,0,0,100,100,0,0,1,4,1,5,35,35,20,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
Dialogue: 0,0:00:00.00,{event_end},{style},,0,0,0,,{caption}
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

def soundtrack(out,seconds=30):
    """Original, reproducible 120 BPM instrumental beat; no third-party music samples."""
    import math, wave, random, struct
    rng=random.Random(77)
    sr=22050
    chords=((261.63,311.13,392.00),(207.65,261.63,311.13),(233.08,293.66,349.23),(196.00,246.94,293.66))
    with wave.open(str(out),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        buf=bytearray()
        for i in range(seconds*sr):
            t=i/sr
            ch=chords[int(t//4)%4]
            pad=0.053*sum(math.sin(2*math.pi*f*t) for f in ch)/3
            beat=t%0.5
            kick=0.28*math.exp(-21*beat)*math.sin(2*math.pi*(100-65*min(beat,0.2))*beat)
            back=(t-0.5)%1.0
            snare=(0.11*(rng.random()*2-1)*math.exp(-27*back)) if back<0.14 else 0
            hat=t%0.25
            hats=0.035*(rng.random()*2-1)*math.exp(-75*hat)
            bass=0.075*math.sin(2*math.pi*ch[0]/2*t)
            env=min(1,t/0.4,(seconds-t)/0.6)
            val=max(-0.9,min(0.9,env*(pad+kick+snare+hats+bass)))
            buf.extend(struct.pack("<h",int(val*24000)))
            if len(buf)>16384:
                w.writeframesraw(buf);buf.clear()
        if buf:w.writeframesraw(buf)

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
    entries=[("아시아 여행 명소 TOP 5\n5 SPOTS TO EXPLORE IN ASIA",None)]+[(f"TOP {5-i}\n{p['name']}"+("\n"+p["name_en"] if p.get("name_en") else ""),p) for i,p in enumerate(places)]+[("어디가 가장 가고 싶나요?\nCOMMENT YOUR FAVORITE",None)]
    for i,(label,place) in enumerate(entries):
        dur=2.0 if i==0 else (3.0 if i==len(entries)-1 else 5.0)
        sub=work/f"subtitle_{i}.ass";ass(sub,label,w,h,"place" if place else "center",dur)
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
    audio=work/"original_beat.wav";soundtrack(audio)
    video=out/"top5.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-i",str(audio),"-map","0:v","-map","1:a","-t","30","-c:v","copy","-c:a","aac","-b:a","96k","-movflags","+faststart",str(video)])
    meta={"topic":topic,"mode":mode,"created_at":datetime.now(timezone.utc).isoformat(),"places":[p["name"] for p in places],"sources":sources,"music":"Original synthesized 120 BPM instrumental generated by renderer (no third-party sample)","notice":("SYNTHETIC DEMO -- NOT REAL PLACE FOOTAGE" if mode=="demo" else "Pexels licensed stock footage; locations reviewed against source descriptions")}
    (out/"metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf8")
    print("RENDER_OK",video,"bytes",video.stat().st_size)

if __name__=="__main__":
    main()
