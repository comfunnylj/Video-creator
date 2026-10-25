"""Offline regression tests; synthetic fixtures are tests, never production samples."""
import copy, importlib.util, io, json, os, tempfile, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('renderer',ROOT/'render_quote_card.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
pspec=importlib.util.spec_from_file_location('payloads',ROOT/'build_publisher_payloads.py')
p=importlib.util.module_from_spec(pspec);pspec.loader.exec_module(p)

class RendererTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name);self.source=self.d/'photo.jpg'
        Image.new('RGB',(3200,4000),(190,180,155)).save(self.source,quality=95)
        self.job={'quote_id':'Q0039','quote':'아직 나의 청춘이\n다하지 않은 까닭입니다.','author':'윤동주','work':'별 헤는 밤',
            'source_verified':True,'caption':'시의 한 대목입니다. 출처를 함께 남깁니다.',
            'photo':{'local_path':str(self.source),'source_url':'https://example.org/photo',
            'photographer':'Test fixture','license_url':'https://example.org/license'}}
    def runjob(self,job=None,formats=None):
        f=self.d/'job.json';f.write_text(json.dumps(job or self.job,ensure_ascii=False))
        return r.run(f,self.d/'out',formats=formats)
    def test_default_only_feed_srgb_and_payload_compatibility(self):
        result=self.runjob();self.assertEqual(len(result['outputs']),1)
        im_path=self.d/'out'/result['outputs'][0]['filename']
        with Image.open(im_path) as im:
            self.assertEqual(im.size,(1080,1350));self.assertEqual(im.mode,'RGB');self.assertTrue(im.info['icc_profile'])
        self.assertEqual(result['publication_status'],'NOT_PUBLISHED')
        prov=self.d/'out/Q0039_daily_quote_provenance.json'
        with self.assertRaises(RuntimeError):p.build(im_path,prov,'https://raw.githubusercontent.com/comfunnylj/telegram-market-feed/'+'a'*40+'/x.jpg','2099-01-01',False)
        ig,th=p.build(im_path,prov,'https://raw.githubusercontent.com/comfunnylj/telegram-market-feed/'+'a'*40+'/x.jpg','2099-01-01',True)
        self.assertEqual(ig['media'][0]['sha256'],result['outputs'][0]['sha256'])
        self.assertEqual(th['dedup_key'],'quote:2099-01-01:Q0039')
    def test_independent_story_crop_and_layout(self):
        self.job['design']={'formats':{'9:16':{'crop_center':[.1,.8],'position':[.5,.25]}}}
        v=self.runjob(formats=['4:5','9:16'])['outputs']
        self.assertNotEqual(v[0]['crop_box'],v[1]['crop_box'])
        self.assertEqual(v[1]['output_height'],1920)
        self.assertNotEqual(v[0]['text_segments'][0]['bbox'],v[1]['text_segments'][0]['bbox'])
    def test_exif_rotation(self):
        im=Image.new('RGB',(4000,3000));ex=Image.Exif();ex[274]=6;b=io.BytesIO();im.save(b,'JPEG',exif=ex)
        out,meta=r.decode_source(b.getvalue());self.assertEqual(out.size,(3000,4000));self.assertEqual(meta['exif_orientation'],6)
    def test_no_upscale_even_with_large_long_edge(self):
        with self.assertRaises(ValueError):r.crop_photo(Image.new('RGB',(400,4000)),1080,1350,[.5,.5])
        b=io.BytesIO();Image.new('RGB',(1200,1800)).save(b,'JPEG')
        with self.assertRaises(ValueError):r.decode_source(b.getvalue())
    def test_protected_subject_and_crop_rejection(self):
        self.job['design']={'style':{'protected_regions':[[.2,.2,.8,.7]]}}
        with self.assertRaises(ValueError):self.runjob()
        style=r.resolve_style({'style':{'protected_regions':[[0,0,.1,.1]]}},'9:16')
        with self.assertRaises(ValueError):r.render(Image.new('RGB',(4000,3000)),self.d/'p.jpg','문장','저자','작품','9:16',style)
    def test_poor_contrast_fails_without_darkening_photo(self):
        self.job['design']={'style':{'color':'#beb49b'}}
        with self.assertRaises(ValueError):self.runjob()
    def test_auto_color_and_recommendation(self):
        self.job['design']={'style':{'recommend':True}}
        v=self.runjob()['outputs'][0];self.assertGreaterEqual(v['min_coverage'],.88)
        self.assertIn(v['text_segments'][0]['color'],('#242422','#111111'))
    def test_safe_bounds_and_long_quote_rejection(self):
        self.job['design']={'style':{'position':[.01,.01]}}
        with self.assertRaises(ValueError):self.runjob()
        self.job['design']={};self.job['quote']='문구가 너무 길어집니다. '*100
        with self.assertRaises(ValueError):self.runjob()
    def test_banned_source_and_missing_provenance(self):
        for mutation in ({'source_url':'https://pexels.com/video/37522118/'},{'ai_generated':True},{'license_url':''}):
            job=copy.deepcopy(self.job);job['photo'].update(mutation)
            with self.assertRaises(ValueError):self.runjob(job)
    def test_invalid_config_and_no_glyph_substitution(self):
        for design in ({'style':{'crop_center':[2,.5]}},{'style':{'shadow_opacity':180}},
                       {'output_formats':['16:9']},{'style':{'font_path':'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'}}):
            job=copy.deepcopy(self.job);job['design']=design
            with self.assertRaises((ValueError,RuntimeError)):self.runjob(job)
    def test_source_verified_must_be_boolean(self):
        self.job['source_verified']='true'
        with self.assertRaises(ValueError):self.runjob()
    def test_original_bytes_and_dimensions_recorded(self):
        v=self.runjob();self.assertEqual(v['source_width'],3200)
        self.assertEqual((self.d/'out/original_photo').read_bytes(),self.source.read_bytes())
        self.assertTrue(v['outputs'][0]['no_global_grade'])
        self.assertEqual(v['outputs'][0]['resolved_style']['shadow_opacity'],0)

    def test_transparent_colors_rejected_for_every_role(self):
        for role in ('quote','author','work'):
            j=copy.deepcopy(self.job)
            j['design']={'style':{'color':'#11111100'} if role=='quote' else {role:{'color':'#11111100'}}}
            with self.assertRaises(ValueError): self.runjob(j)

    def test_failed_rerender_preserves_all_previous_outputs(self):
        self.runjob(formats=['4:5','9:16'])
        old={p.name:p.read_bytes() for p in (self.d/'out').iterdir()}
        self.job['quote']='완전히 다른 문장입니다.'
        self.job['design']={'formats':{'9:16':{'position':[0,0]}}}
        with self.assertRaises(ValueError):self.runjob(formats=['4:5','9:16'])
        self.assertEqual(old,{p.name:p.read_bytes() for p in (self.d/'out').iterdir()})

    def test_new_feed_only_run_removes_stale_story(self):
        self.runjob(formats=['4:5','9:16']);self.runjob()
        self.assertFalse((self.d/'out/Q0039_daily_quote_STORY_9x16.jpg').exists())

    def test_every_preset_works_without_manual_position(self):
        for preset in ('center','upper','side'):
            job=copy.deepcopy(self.job);job['design']={'style':{'preset':preset}}
            self.assertEqual(self.runjob(job)['outputs'][0]['resolved_style']['preset'],preset)

if __name__=='__main__':unittest.main()
