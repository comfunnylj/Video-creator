#!/usr/bin/env python3
"""Daily Quote Maker 1.1.0: real photographs, configurable typography, independent crops.
Rendering never submits publisher jobs. Automated measurements do not replace visual review.
"""
from __future__ import annotations
import argparse, copy, hashlib, io, json, math, os, re, tempfile, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from functools import lru_cache
from fontTools.ttLib import TTFont
from PIL import Image, ImageCms, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat

VERSION = '1.1.0'
MAX_DOWNLOAD = 38 * 1024 * 1024
SIZES = {'4:5': (1080, 1350, 'IG_4x5'), '9:16': (1080, 1920, 'STORY_9x16')}
PRESETS = {
    'center': {'position': [.5, .43], 'max_width': .78, 'align': 'center'},
    'upper': {'position': [.5, .25], 'max_width': .78, 'align': 'center'},
    'side': {'position': [.69, .64], 'max_width': .46, 'align': 'right'},
}
DEFAULT = {
    'preset': 'center', 'font_path': None, 'font_index': 0,
    'font_size': 38, 'min_font_size': 28, 'color': 'auto', 'line_spacing': 1.65,
    'author': {'font_size': 21, 'color': 'auto', 'gap': 28},
    'work': {'font_size': 18, 'color': 'auto', 'gap': 12},
    'safe_margin': .075, 'max_lines': 7, 'contrast_min': 3., 'contrast_coverage_min': .88,
    'shadow_opacity': 0, 'shadow_offset': [0, 1], 'crop_center': [.5, .5],
    'protected_regions': [], 'recommend': False,
}
FONT_PATHS = ('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
              '/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf')

def merge(a, b):
    out = copy.deepcopy(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out

def get_font(size, path=None, index=0):
    for p in ([path] if path else [os.environ.get('QUOTE_FONT_PATH'), *FONT_PATHS]):
        if p and Path(p).is_file():
            return ImageFont.truetype(str(p), round(size), index=index)
    raise RuntimeError('Korean serif font required: set font_path or QUOTE_FONT_PATH; no Latin-only fallback')

def unit_pair(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 2 or any(
        not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 1 for x in value):
        raise ValueError(f'{name} must contain two normalized numbers in [0,1]')
    return value

@lru_cache(maxsize=8)
def font_codepoints(path, index):
    with TTFont(path, fontNumber=index) as font:
        return set(font.getBestCmap())

def source_file(job, dest):
    media = job['photo']
    for field in ('source_url', 'photographer', 'license_url'):
        if not media.get(field): raise ValueError(f'Photo provenance missing: {field}')
    identifiers = ' '.join(str(media.get(k, '')) for k in ('source_url', 'download_url', 'id', 'capture_type'))
    if re.search(r'37522118|time.?lapse|hyper.?lapse', identifiers, re.I):
        raise ValueError('Rejected timelapse/hyperlapse or prohibited source 37522118')
    if media.get('timelapse') or media.get('ai_generated'): raise ValueError('Require genuine still photography')
    if media.get('local_path'):
        data = Path(media['local_path']).read_bytes()
    else:
        url = media.get('download_url', '').strip()
        if not url.startswith('https://'): raise ValueError('Require approved HTTPS photo URL or local_path')
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyQuoteMaker/1.1'})
        with urllib.request.urlopen(req, timeout=60) as response:
            if not response.url.startswith('https://'): raise ValueError('Reject HTTPS downgrade')
            data = response.read(MAX_DOWNLOAD + 1)
    if not 1000 <= len(data) <= MAX_DOWNLOAD: raise ValueError('Source byte count outside limits')
    with Image.open(io.BytesIO(data)) as im:
        if im.format not in ('JPEG', 'PNG', 'WEBP', 'TIFF') or getattr(im, 'n_frames', 1) != 1:
            raise ValueError('Require a single still image')
        im.verify()
    dest.write_bytes(data)
    return data

def decode_source(data):
    with Image.open(io.BytesIO(data)) as raw:
        encoded_size, orientation = list(raw.size), raw.getexif().get(274, 1)
        icc = raw.info.get('icc_profile')
        src = ImageOps.exif_transpose(raw)
        if icc:
            src = ImageCms.profileToProfile(src, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                    ImageCms.createProfile('sRGB'), outputMode='RGB')
        else: src = src.convert('RGB')
        src.load()
    if max(src.size) < 3000:
        raise ValueError(f'Actual original {src.width}x{src.height}: require long edge >=3000px')
    return src, {'encoded_dimensions': encoded_size, 'exif_orientation': orientation,
        'source_width': src.width, 'source_height': src.height,
        'color_conversion': 'embedded ICC to sRGB' if icc else 'untagged source assumed sRGB'}

def crop_photo(src, width, height, center):
    cx, cy = unit_pair(center, 'crop_center')
    sw, sh = src.size
    cw, ch = min(sw, sh * width / height), min(sh, sw * height / width)
    if cw < width or ch < height: raise ValueError('Insufficient native crop pixels; upscaling forbidden')
    left, top = (sw - cw) * cx, (sh - ch) * cy
    box = (round(left), round(top), round(left + cw), round(top + ch))
    return src.crop(box).resize((width, height), Image.Resampling.LANCZOS), box

def wrap_text(text, draw, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for ch in paragraph.strip():
            if line and draw.textlength(line + ch, font=font) > max_width:
                idx = line.rfind(' ')
                if idx > len(line) // 2:
                    lines.append(line[:idx]); line = line[idx + 1:] + ch
                else: lines.append(line.rstrip()); line = ch.lstrip()
            else: line += ch
        if line: lines.append(line)
    return lines

def opaque_color(value):
    rgba = ImageColor.getcolor(value, 'RGBA')
    if rgba[3] != 255:
        raise ValueError('Text colors must be fully opaque; transparent RGBA is forbidden')
    return '#%02x%02x%02x' % rgba[:3]

def resolve_style(settings, ratio):
    base = merge(DEFAULT, settings.get('style', {}))
    base = merge(base, settings.get('formats', {}).get(ratio, {}))
    if base['preset'] not in PRESETS: raise ValueError('preset must be center, upper or side')
    for style in (base, base['author'], base['work']):
        if style.get('color', 'auto') != 'auto': style['color'] = opaque_color(style['color'])
    return merge(PRESETS[base['preset']], base)

def layout(text, author, work, size, style):
    w, h = size
    unit_pair(style['position'], 'position')
    if style['align'] not in ('left', 'center', 'right'): raise ValueError('Invalid alignment')
    if not .04 <= style['safe_margin'] <= .2 or not .2 <= style['max_width'] <= .9:
        raise ValueError('Invalid safe_margin or max_width')
    if not 1.1 <= style['line_spacing'] <= 2.2 or not 28 <= style['min_font_size'] <= style['font_size'] <= 72:
        raise ValueError('Invalid quote type scale')
    if not 0 <= style['shadow_opacity'] <= 45: raise ValueError('Shadow must be subtle, <=45/255')
    for key in ('author', 'work'):
        if not 16 <= style[key]['font_size'] < style['min_font_size'] or style[key]['gap'] < 0:
            raise ValueError('Attribution must be distinctly smaller, >=16px, with nonnegative gap')
    if not 1 <= style['contrast_min'] <= 21 or not .5 <= style['contrast_coverage_min'] <= 1:
        raise ValueError('Invalid contrast thresholds')
    draw = ImageDraw.Draw(Image.new('L', (w, h)))
    kwargs = {'path': style['font_path'], 'index': style['font_index']}
    for fs in range(round(style['font_size']), round(style['min_font_size']) - 1, -1):
        font = get_font(fs, **kwargs)
        missing = {ord(ch) for ch in text+author+work if not ch.isspace()} - font_codepoints(font.path, style['font_index'])
        if missing: raise ValueError('Selected font lacks glyphs: '+','.join(hex(c) for c in sorted(missing)))
        lines = wrap_text(text, draw, font, w * style['max_width'])
        if len(lines) > style['max_lines']: continue
        segments, y = [], 0
        for line in lines:
            segments.append([line, font, y, 'quote']); y += round(fs * style['line_spacing'])
        y -= round(fs * style['line_spacing']) - fs
        for key, value in (('author', author), ('work', work)):
            if not value.strip():
                continue
            f = get_font(style[key]['font_size'], **kwargs); y += style[key]['gap']
            for line in wrap_text(value, draw, f, w * style['max_width']):
                segments.append([line, f, y, key]); y += round(f.size * 1.4)
        total = max(s[2] + draw.textbbox((0, 0), s[0], font=s[1], anchor='lt')[3] for s in segments)
        start_x = style['position'][0] * w - w * style['max_width'] / 2
        start_y = style['position'][1] * h - total / 2
        placed = []
        for line, f, y, key in segments:
            tw = draw.textlength(line, font=f)
            offset = {'left': 0, 'center': (w * style['max_width'] - tw) / 2,
                      'right': w * style['max_width'] - tw}[style['align']]
            xy = (round(start_x + offset), round(start_y + y))
            placed.append({'text': line, 'font': f, 'xy': xy,
                           'bbox': draw.textbbox(xy, line, font=f, anchor='lt'), 'role': key})
        m = style['safe_margin']
        if all(b[0] >= w*m and b[1] >= h*m and b[2] <= w*(1-m) and b[3] <= h*(1-m)
               for b in (s['bbox'] for s in placed)): return placed, fs
    raise ValueError('Type does not fit safe bounds; shorten or reposition, never clip')

def luminance(rgb):
    c = [v / 255 for v in rgb[:3]]
    c = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return .2126*c[0] + .7152*c[1] + .0722*c[2]

def contrast_for(picture, segment, color):
    mask = Image.new('L', picture.size)
    ImageDraw.Draw(mask).text(segment['xy'], segment['text'], font=segment['font'], fill=255, anchor='lt')
    a = luminance(ImageColor.getrgb(color))
    samples = []
    crop, ink = picture.crop(segment['bbox']), mask.crop(segment['bbox'])
    pixel_data = lambda im: im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata()
    for pixel, m in zip(pixel_data(crop), pixel_data(ink)):
        if m > 200:
            b = luminance(pixel); samples.append((max(a,b)+.05)/(min(a,b)+.05))
    samples.sort()
    if not samples: raise ValueError('No glyph interiors; check font coverage')
    return samples

def overlap(a, b):
    return max(0,min(a[2],b[2])-max(a[0],b[0])) * max(0,min(a[3],b[3])-max(a[1],b[1]))

def subject_boxes(style, source_size, crop_box, output_size):
    boxes = []; sw, sh = source_size; w, h = output_size; l,t,r,b = crop_box
    for region in style['protected_regions']:
        if len(region)!=4 or any(not 0<=x<=1 for x in region) or region[0]>=region[2] or region[1]>=region[3]:
            raise ValueError('protected_regions: [left,top,right,bottom] normalized to oriented original')
        original = (region[0]*sw,region[1]*sh,region[2]*sw,region[3]*sh)
        if original[0]<l or original[1]<t or original[2]>r or original[3]>b:
            raise ValueError('Crop cuts a protected subject; adjust crop_center or photo')
        boxes.append(((original[0]-l)*w/(r-l),(original[1]-t)*h/(b-t),
                      (original[2]-l)*w/(r-l),(original[3]-t)*h/(b-t)))
    return boxes

def render(src, outpath, quote, author, work, ratio, style):
    w,h,_ = SIZES[ratio]
    picture,crop_box = crop_photo(src,w,h,style['crop_center'])
    protected = subject_boxes(style,src.size,crop_box,(w,h))
    candidates = [style]
    if style['recommend']:
        candidates += [merge(style,PRESETS[k]) for k in PRESETS]
        candidates += [merge(style,{'position':[.70,.25],'max_width':.46,'align':'right'})]
    ranked = []
    for candidate in candidates:
        try:
            segments,actual_fs = layout(quote,author,work,(w,h),candidate)
            if any(overlap(s['bbox'],p)>0 for s in segments for p in protected): continue
            colors = ['#f7f4ed','#ffffff','#242422','#111111'] if candidate['color']=='auto' else [candidate['color']]
            options = []
            for color in colors:
                details = []
                for s in segments:
                    requested = candidate.get(s['role'],{}).get('color','auto') if s['role']!='quote' else 'auto'
                    c = opaque_color(color if requested=='auto' else requested)
                    values = contrast_for(picture,s,c)
                    details.append({'color':c,'p10_contrast':round(values[len(values)//10],3),
                        'coverage':round(sum(x>=candidate['contrast_min'] for x in values)/len(values),4)})
                options.append((min(d['coverage'] for d in details),min(d['p10_contrast'] for d in details),details))
            coverage,contrast,details = max(options,key=lambda x:(x[0],x[1]))
            texture = sum(ImageStat.Stat(picture.crop(s['bbox']).convert('L').filter(ImageFilter.FIND_EDGES)).mean[0]
                          for s in segments)/len(segments)
            ranked.append((coverage,contrast,-texture,candidate,segments,actual_fs,details))
        except ValueError: continue
    if not ranked: raise ValueError('No layout fits safe bounds and protected subjects')
    coverage,contrast,texture,style,segments,fs,details = max(ranked,key=lambda x:x[:3])
    if coverage<style['contrast_coverage_min']:
        raise ValueError(f'Readability gate failed: {coverage:.1%}; choose another position/color/photo')
    overlay = Image.new('RGBA',(w,h)); draw = ImageDraw.Draw(overlay)
    for s,d in zip(segments,details):
        if style['shadow_opacity']:
            dx,dy=style['shadow_offset']
            if abs(dx)>2 or abs(dy)>2: raise ValueError('Only <=2px shadow offsets allowed')
            draw.text((s['xy'][0]+dx,s['xy'][1]+dy),s['text'],font=s['font'],anchor='lt',fill=(0,0,0,style['shadow_opacity']))
        draw.text(s['xy'],s['text'],font=s['font'],anchor='lt',fill=d['color'])
    result = Image.alpha_composite(picture.convert('RGBA'),overlay).convert('RGB')
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    result.save(outpath,'JPEG',quality=96,subsampling=0,optimize=True,icc_profile=icc)
    with Image.open(outpath) as im:
        assert im.size==(w,h) and im.mode=='RGB' and im.format=='JPEG' and im.info.get('icc_profile')
        im.verify()
    return {'filename':outpath.name,'bytes':outpath.stat().st_size,
        'sha256':hashlib.sha256(outpath.read_bytes()).hexdigest(),'output_width':w,'output_height':h,
        'crop_box':list(crop_box),'crop_native_width':crop_box[2]-crop_box[0],'crop_native_height':crop_box[3]-crop_box[1],
        'resolved_style':style,'actual_font_size':fs,'contrast_min':style['contrast_min'],
        'font_path':str(segments[0]['font'].path),
        'font_sha256':hashlib.sha256(Path(segments[0]['font'].path).read_bytes()).hexdigest(),
        'min_coverage':coverage,'p10_contrast':contrast,'texture_score':-texture,
        'text_segments':[{'text':s['text'],'role':s['role'],'bbox':list(s['bbox']),'font_size':s['font'].size,**d}
                         for s,d in zip(segments,details)],'visual_review':'REQUIRED','no_global_grade':True}

def run(job_path,output,config_path=None,formats=None):
    job=json.loads(job_path.read_text(encoding='utf-8'))
    if not isinstance(job.get('quote'),str) or not job['quote'].strip():
        raise ValueError('Nonempty quote required')
    user_original=job.get('user_original') is True
    if user_original:
        if not isinstance(job.get('author',''),str) or not isinstance(job.get('work',''),str):
            raise ValueError('User original author/work must be strings if supplied')
        if (job.get('author','').strip() or job.get('work','').strip()) and job.get('attribution_approved') is not True:
            raise ValueError('Do not invent an attribution for user original text')
        job.setdefault('author','')
        job.setdefault('work','')
    else:
        for field in ('author','work'):
            if not isinstance(job.get(field),str) or not job[field].strip():
                raise ValueError(f'Nonempty {field} required')
    if not re.fullmatch(r'Q\d{4}',job.get('quote_id','')): raise ValueError('Quote ID Q0001 required')
    if job.get('source_verified') is not True: raise ValueError('Exact quotation source must be verified')
    settings=merge({},job.get('design',{}))
    if config_path: settings=merge(settings,json.loads(config_path.read_text(encoding='utf-8')))
    requested=formats or settings.get('output_formats',['4:5'])
    if not requested or any(f not in SIZES for f in requested) or len(set(requested))!=len(requested):
        raise ValueError('Unique output_formats must be 4:5 and/or 9:16')
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.render-', dir=output) as temp:
        stage=Path(temp)
        data=source_file(job,stage/'original_photo'); src,source_meta=decode_source(data)
        name=job['quote_id']+'_daily_quote'; results=[]
        for ratio in requested:
            path=stage/(name+'_'+SIZES[ratio][2]+'.jpg')
            results.append(render(src,path,job['quote'].strip(),job['author'].strip(),job['work'].strip(),ratio,resolve_style(settings,ratio)))
        provenance={'version':VERSION,'quote_id':job['quote_id'],'quote':job['quote'],'author':job['author'],'work':job['work'],
            'caption':job.get('caption',''),'quote_reference':job.get('quote_reference',''),
            'media_source':job['photo']['source_url'],'photographer':job['photo']['photographer'],
            'license_url':job['photo']['license_url'],'photo':job['photo'],
            'original_sha256':hashlib.sha256(data).hexdigest(),**source_meta,'outputs':results,
            'generated_at_utc':datetime.now(timezone.utc).isoformat(),'publication_status':'NOT_PUBLISHED',
            'capture_type':'REAL_STILL_IMAGE_NO_TIMELAPSE','visual_review':'REQUIRED','design_settings':settings}
        (stage/(name+'_provenance.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # Stage ALL formats and provenance before replacing anything. Preserve old output on failure.
        backup=stage/'backup';backup.mkdir()
        incoming=[p for p in stage.iterdir() if p.is_file()]
        old=set(output.glob(name+'_*.jpg')) | {output/p.name for p in incoming}
        moved=[];installed=[]
        try:
            for target in old:
                if target.is_file():
                    os.replace(target,backup/target.name);moved.append(target)
            for item in incoming:
                target=output/item.name
                os.replace(item,target);installed.append(target)
        except BaseException:
            for target in installed:target.unlink(missing_ok=True)
            for target in moved:os.replace(backup/target.name,target)
            raise
    print(json.dumps({'success':True,'quote_id':job['quote_id'],'results':[
        {k:r[k] for k in ('filename','output_width','output_height','min_coverage')} for r in results]},ensure_ascii=False))
    return provenance

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--job',type=Path,required=True);ap.add_argument('--output',type=Path,default=Path('output_quote_cards'))
    ap.add_argument('--config',type=Path);ap.add_argument('--formats',nargs='+',choices=list(SIZES))
    args=ap.parse_args();run(args.job,args.output,args.config,args.formats)
