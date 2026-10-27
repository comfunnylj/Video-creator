#!/usr/bin/env python3
"""Fetch verified CC0 PBR textures and city-dusk HDRI for an upstream Lemo 3D scene.
Downloads links from Poly Haven's API on the disposable GitHub Actions runner, not Oracle.
"""
from pathlib import Path
import hashlib, json, os, sys, urllib.request

DST=Path(sys.argv[1]); DST.mkdir(parents=True,exist_ok=True)
HEAD={"User-Agent":"LemoOpuscar-OriginalRenderer/1.0 (CC0 environment evaluation)"}
def getjson(url):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=45) as f:
        return json.load(f)

def download(url,target,expected_md5=None):
    if not url.startswith("https://"): raise RuntimeError("non-HTTPS asset rejected")
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=120) as source,open(target,"wb") as out:
        while chunk:=source.read(1<<20):out.write(chunk)
    size=target.stat().st_size
    if size<10000:raise RuntimeError(f"unexpectedly small downloaded asset: {target} {size}")
    if expected_md5:
        digest=hashlib.md5(target.read_bytes()).hexdigest()
        if digest.lower()!=expected_md5.lower():raise RuntimeError(f"hash mismatch {target}")
    print(target.name,size,url,flush=True)

def pathcase(d,names):
    for n in names:
        for k,v in d.items():
            if k.lower()==n.lower():return v
    return None

def variant(tree,kind):
    layer=pathcase(tree,kind)
    if layer is None:raise KeyError(f"no {kind}: found {list(tree)}")
    for resolution in ("2k","1k","4k"):
        levels=pathcase(layer,[resolution])
        if not levels:continue
        for ext in ("jpg","png"):
            obj=pathcase(levels,[ext])
            if obj and isinstance(obj,dict) and "url" in obj:return obj
    raise KeyError(f"no JPG/PNG file for {kind} in {list(layer)}")

for slug,prefix in [("red_brick_03","brick"),("cobblestone_01","cobble")]:
    tree=getjson(f"https://api.polyhaven.com/files/{slug}")
    for kind,aliases in [("diff",("Diffuse","diff","Albedo")),("nor",("nor_gl","Normal (GL)","Normal GL")),("rough",("Rough","rough","Roughness"))]:
        obj=variant(tree,aliases)
        url=obj["url"]; suffix=url.rsplit(".",1)[-1].split("?")[0].lower()
        if suffix not in ("jpg","png"):raise ValueError(url)
        download(url,DST/f"{prefix}_{kind}.{suffix}",obj.get("md5"))
        (DST/f"{prefix}_{kind}.path").write_text(f"{prefix}_{kind}.{suffix}")

hdr=getjson("https://api.polyhaven.com/files/sunset_jhbcentral")
data=variant(hdr,("hdri",)) if False else hdr["hdri"]
obj=data["1k"]["hdr"]
download(obj["url"],DST/"sunset_city.hdr",obj.get("md5"))
(DST/"ASSET_PROVENANCE.txt").write_text(
"Poly Haven CC0 scanned materials and sky, downloaded via https://api.polyhaven.com/files/...\n"
"Assets: red_brick_03, cobblestone_01, sunset_jhbcentral\n"
"https://polyhaven.com/a/red_brick_03\nhttps://polyhaven.com/a/cobblestone_01\n"
"https://polyhaven.com/a/sunset_jhbcentral\n")
