#!/usr/bin/env python3
"""Mux a separately licensed audio file locally. NEVER assume Shorts music rights.

You must possess synchronization/distribution rights for the actual intended use.
"""
import argparse, subprocess
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video',required=True,type=Path,help='silent verified MP4')
    ap.add_argument('--audio',required=True,type=Path,help='properly licensed WAV/MP3 file')
    ap.add_argument('--audio-start',type=float,default=0.0,help='audio file offset in seconds')
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--rights-confirmed',action='store_true',help='you have the required music synchronization/republication rights')
    args=ap.parse_args()
    if not args.rights_confirmed:
        ap.error('Music synchronization and distribution rights must be confirmed for external MP4 publishing.')
    if args.audio_start<0:ap.error('audio-start must not be negative')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(args.video),'-ss',str(args.audio_start),'-i',str(args.audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','23.2','-movflags','+faststart',str(args.output)]
    subprocess.run(cmd,check=True)
    print(f'Created {args.output}; do not assume music rights were granted by this program')

if __name__=='__main__':main()