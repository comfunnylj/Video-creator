#!/usr/bin/env python3
"""Original 10s steampunk brass-and-engine score: self-contained, no external samples."""
import math
import random
import struct
import sys
import wave
from pathlib import Path

SR = 44100
DUR = 10.0
TAU = 2.0 * math.pi
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
rng = random.Random(117)
minor = [55.0, 65.4064, 73.4162, 82.4069]

def bell(t, at, freq, power=1.0):
    d = t-at
    if d < 0 or d > 2.9:
        return 0.
    env = math.exp(-2.4*d) * (1-math.exp(-160*d))
    return power * env * (
        math.sin(TAU*freq*d)*.50 +
        math.sin(TAU*freq*2.756*d)*.28 +
        math.sin(TAU*freq*5.405*d)*.13
    )

with wave.open(str(out), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    block = bytearray()
    for i in range(round(SR*DUR)):
        t=i/SR
        root = minor[min(3,int(t//2.5))]
        swell=min(1.,max(0.,(t-.35)/2.2))*(1.0-.22*max(0.,(t-8.2)/1.8))
        phase=TAU*root*t
        drone=(.14*math.sin(phase) + .065*math.sin(2*phase+.24)
              + .035*math.sin(.5*phase-.14) + .022*math.sin(3*phase+.2))
        horn=.045*(math.sin(TAU*110*t)+.37*math.sin(TAU*220*t))*swell
        tic_t=t%0.5
        click=.048*math.exp(-90*tic_t)*math.sin(TAU*2300*tic_t)
        piston=t%1.0
        thud=.11*math.exp(-13*piston)*math.sin(TAU*(39+30*math.exp(-11*piston))*piston)
        steam=0.0
        for at in (2.35,4.25,6.9,8.1):
            d=t-at
            if 0<d<.85:
                steam+=.037*math.exp(-4*d)*(2*rng.random()-1)
        bells=(bell(t,1.1,440,.1)+bell(t,3.0,329.6,.17)
               +bell(t,5.35,293.67,.23)+bell(t,8.3,440,.12))
        atmosphere=(.0075*(2*rng.random()-1)+.009*math.sin(TAU*89*t))
        airship=.023*math.sin(TAU*(54 + 2*math.sin(t*.3))*t)*(1. if t>2.6 else t/2.6)
        value = (drone*swell + horn + click + thud + steam + bells + atmosphere + airship)
        env=min(1.,t/.28,(DUR-t)/.55)
        value=max(-.96,min(.96,value*max(0.,env)))
        block.extend(struct.pack('<h',int(value*27000)))
        if len(block)>=32768:
            w.writeframesraw(block)
            block.clear()
    if block:
        w.writeframesraw(block)
print('original WAV',out,round(SR*DUR),'samples')