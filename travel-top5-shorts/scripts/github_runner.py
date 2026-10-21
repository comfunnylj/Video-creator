#!/usr/bin/env python3
"""Render verified 23.2s bilingual TOP5 from a GitHub owner issue or a local job JSON.

The only remote media source accepted is HTTPS *.pexels.com. NEVER downloads music.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HEADER = 'TOP5_STYLE_V2\n'
MAX_BYTES = 180_000_000

def accepted(url):
    if not isinstance(url, str):
        return False
    u = urllib.parse.urlsplit(url)
    return u.scheme == 'https' and bool(u.hostname) and (u.hostname == 'pexels.com' or u.hostname.endswith('.pexels.com')) and not u.username and not u.password

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not accepted(newurl):
            raise ValueError('Redirect blocked: media URL must remain under pexels.com')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def download(url, dest):
    if not accepted(url):
        raise ValueError('Only verified https://*.pexels.com direct video links allowed')
    opener = urllib.request.build_opener(SafeRedirect)
    request = urllib.request.Request(url, headers={'User-Agent':'TravelTOP5Skill/1.1'})
    with opener.open(request, timeout=90) as response, open(dest,'wb') as output:
        length=0
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            length+=len(chunk)
            if length>MAX_BYTES:raise ValueError('Clip exceeds size cap')
            output.write(chunk)
    if length<1000:raise ValueError('Downloaded media is suspiciously small')

def validate_media(item, idx):
    if not isinstance(item,dict):raise ValueError(f'{idx} must be an object')
    media=item.get('media') or {}
    if not isinstance(media,dict):raise ValueError(f'{idx}.media must be an object')
    for flag in ['approved','license_checked','location_verified']:
        if media.get(flag) is not True:raise ValueError(f'{idx} requires explicit {flag}=true')
    for key in ['download_url','source_url','license_url','source_creator','location_evidence','rights_checked_date']:
        val=media.get(key)
        if (not isinstance(val,str) or not val.strip() or 'REPLACE' in val.upper() or 'YYYY-MM-DD' in val.upper()):raise ValueError(f'{idx}: missing or placeholder {key}')
    if not accepted(media['download_url']):raise ValueError(f'{idx}: media link must be Pexels HTTPS')
    if not str(media['rights_checked_date']).startswith('20') or len(str(media['rights_checked_date'])) != 10:
        raise ValueError(f'{idx}: requires reviewed date YYYY-MM-DD')
    for key in ['source_url','license_url']:
        u=urllib.parse.urlsplit(media[key])
        if u.scheme!='https' or not u.hostname:raise ValueError(f'{idx}.{key} needs HTTPS URL')
    if str(media['source_url']).startswith('https://example.'):
        raise ValueError(f'{idx}: placeholder source URL')
    return media

def load_job(args):
    if args.issue_event:
        obj=json.loads(Path(args.issue_event).read_text(encoding='utf-8'))
        issue=obj.get('issue') or {}
        owner=(obj.get('repository') or {}).get('owner') or {}
        login=owner.get('login')
        if not login or (issue.get('user') or {}).get('login')!=login:
            raise ValueError('Only repo owner issues are accepted')
        body=issue.get('body') or ''
        if not body.startswith(HEADER):raise ValueError('V2 issue header missing')
        return json.loads(body[len(HEADER):])
    return json.loads(Path(args.job).read_text(encoding='utf-8'))

def make_manifest(job, work, fetch=True):
    if not isinstance(job,dict) or job.get('mode')!='approved_media':
        raise ValueError('Only approved_media is allowed (no synthetic demo)')
    if job.get('audio_mode','silent')!='silent':
        raise ValueError('GitHub runner intentionally exports SILENT videos; music licensing must occur outside this job')
    places=job.get('places')
    if not isinstance(places,list) or len(places)!=5:raise ValueError('Expected five places')
    if [p.get('rank') for p in places]!=[5,4,3,2,1]:raise ValueError('Rank order must be 5..1')
    for title in ('title_ko','title_en'):
        if not isinstance(job.get(title),str) or not 1<=len(job[title])<=120:
            raise ValueError('Missing '+title)
    m={'title_ko':job['title_ko'],'title_en':job['title_en'],'intro_footage':'assets/intro.mp4','intro_trim_start':float(job.get('intro_trim_start',0)),'places':[]}
    assets=work/'assets';assets.mkdir(parents=True,exist_ok=True)
    intro=validate_media(job.get('intro'), 'intro')
    if fetch:download(intro['download_url'],assets/'intro.mp4')
    audit={'intro':{k:v for k,v in intro.items() if k!='download_url'},'places':[]}
    for place in places:
        if not isinstance(place,dict):raise ValueError('Places must be objects')
        rank=place['rank']
        for key in ('place_ko','place_en','country_ko','country_en'):
            if not isinstance(place.get(key),str) or not place[key].strip() or len(place[key])>100:
                raise ValueError(f'rank {rank}: missing {key}')
        media=validate_media(place,'rank '+str(rank))
        rel=f'assets/place{rank}.mp4'
        if fetch:download(media['download_url'],work/rel)
        m['places'].append({**{k:place[k] for k in ('rank','place_ko','place_en','country_ko','country_en')}, 'footage':rel,'trim_start':float(place.get('trim_start',0)), 'crop_x':float(place.get('crop_x',0.5)), **{k:media[k] for k in ('source_url','license_url','source_creator','location_evidence','rights_checked_date')}})
        audit['places'].append({'rank':rank,'name':place['place_ko'],**{k:v for k,v in media.items() if k!='download_url'}})
    (work/'source_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    (work/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
    return work/'manifest.json'

def main():
    parser=argparse.ArgumentParser()
    a=parser.add_mutually_exclusive_group(required=True)
    a.add_argument('--job',type=Path)
    a.add_argument('--issue-event',type=Path)
    parser.add_argument('--output-dir',type=Path,default=Path('output_top5_v2'))
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    job=load_job(args)
    work=args.output_dir/'project'
    mf=make_manifest(job,work,fetch=not args.validate_only)
    if args.validate_only:
        print('VALID: 5 approved sites, licensing metadata, Pexels URLs, silent export');return
    root=Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable,str(root/'scripts'/'render_top5.py'),str(mf),'--output-dir',str(args.output_dir/'render')],check=True)
    subprocess.run([sys.executable,str(root/'scripts'/'verify_top5.py'),str(args.output_dir/'render'/'top5_ko_SILENT.mp4'),str(args.output_dir/'render'/'top5_en_SILENT.mp4')],check=True)
    print('SUCCESS: two bilingual silent 23.2s Shorts, audited clips')

if __name__=='__main__':
    main()