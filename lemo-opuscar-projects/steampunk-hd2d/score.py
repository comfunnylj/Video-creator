#!/usr/bin/env python3
"""Original synth score and mechanical ambience for Clockwork Dawn. No external samples."""
import math
import struct
import sys
import wave
from pathlib import Path
from random import Random

SR = 22050
SEC = 10
N = SR * SEC
notes = (110.0, 130.81, 146.83, 164.81)
rng = Random(42)
output = Path(sys.argv[1])
output.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(output), "wb") as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(SR)
    data = bytearray()
    for i in range(N):
        t = i / SR
        beat = t % .5
        root = notes[min(int(t // 2.5), 3)]
        pad = .14 * (math.sin(2*math.pi*root*t) +
                      .32 * math.sin(2*math.pi*root*2*t) +
                      .20 * math.sin(2*math.pi*root*1.5*t))
        pulse = .14 * math.exp(-14*beat) * math.sin(2*math.pi*(60+75*math.exp(-18*beat))*beat)
        chug = .035 * math.exp(-28*(t % .25)) * (rng.random()*2-1)
        spark = 0.0
        for when in (3.4, 5.2, 6.1, 6.9, 8.8):
            dt = t - when
            if 0 <= dt < .5:
                spark += .18 * math.exp(-8*dt)*math.sin(2*math.pi*(740+when*43)*dt)
        envelope = min(1,t/.7,(SEC-t)/.8)
        v = max(-.96,min(.96,envelope*(pad+pulse+chug+spark)))
        data.extend(struct.pack('<h',int(v*26000)))
        if len(data) > 16384:
            out.writeframesraw(data)
            data.clear()
    if data:
        out.writeframesraw(data)
print(f'Wrote original audio to {output}')
