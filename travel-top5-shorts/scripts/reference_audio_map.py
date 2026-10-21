#!/usr/bin/env python3
"""Analyze cut points and rough audio energy peaks of a user-provided reference MP4.

Does not redistribute or save a copy of copyrighted audio. Beat peaks are
approximations of loudness transients, not verified musical downbeats.
"""
import argparse, array, json, math, subprocess
from pathlib import Path

FPS=30
CUTS=[0,91,121,212,242,333,363,454,484,575,605,696]
NAMES=['intro','rank5','view5','rank4','view4','rank3','view3','rank2','view2','rank1','view1','end']

def run(args):
    p=subprocess.run(list(map(str,args)),check=True,capture_output=True)
    return p.stdout

def inspect(source):
    return json.loads(run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,r_frame_rate,sample_rate:format=duration','-of','json',source]))

def analyze(source):
    meta=inspect(source)
    if not any(s['codec_type']=='audio' for s in meta['streams']):
        raise ValueError('Reference file has no audio stream')
    sr=8000
    raw=run(['ffmpeg','-v','error','-i',source,'-vn','-ac','1','-ar',str(sr),'-f','s16le','-acodec','pcm_s16le','-'])
    samples=array.array('h');samples.frombytes(raw)
    hop=int(sr*.010)
    block=int(sr*.040)
    rms=[]
    for off in range(0,len(samples)-block,hop):
        sq=sum(v*v for v in samples[off:off+block]) /block
        rms.append(math.sqrt(sq)/32768)
    times=[i*hop/sr for i in range(len(rms))]
    med=sum(rms)/max(1,len(rms))
    def local_peak(cue):
        lo=max(1,int((cue-.30)/.01));hi=min(len(rms)-1,int((cue+.55)/.01))
        if lo>=hi:return None
        p=max(range(lo,hi),key=lambda i:rms[i])
        return {'energy_peak_seconds':round(times[p],3),'offset_from_cut_seconds':round(times[p]-cue,3),'rms':round(rms[p],4)}
    return {
        'source_basename':Path(source).name,
        'duration_seconds':float(meta['format']['duration']),
        'audio_streams':len([s for s in meta['streams'] if s.get('codec_type')=='audio']),
        'note':'RMS peaks are measured loudness, not proven kick/snare/downbeats or any licensed music start timestamp.',
        'cut_markers':[{'segment':name,'frame':frame,'video_seconds':round(frame/FPS,3), 'nearest_loudness_peak':local_peak(frame/FPS) if frame not in (0,696) else None} for name,frame in zip(NAMES,CUTS)],
        'mean_rms':round(med,4),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('reference_mp4',type=Path)
    ap.add_argument('--out',default='beat_reference_report.json',type=Path)
    args=ap.parse_args()
    result=analyze(args.reference_mp4)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(args.out)

if __name__=='__main__':main()