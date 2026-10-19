"""Regression checks for editorial records, timeline validation, and audio output."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import wave
import studio

class PipelineChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.p=json.loads((studio.ROOT/'projects/frame-story/project.json').read_text())

    def save(self,p):
        studio.write_json(self.root/'project.json',p)
        return self.root

    def test_example_records_valid(self):
        studio.load(self.save(self.p))

    def test_scene_gap_rejected(self):
        self.p['scenes'][1]['start']+=.1
        with self.assertRaisesRegex(ValueError,'gap'):studio.load(self.save(self.p))

    def test_subtitle_overlap_rejected(self):
        self.p['subtitles'][1]['start']-=.1
        with self.assertRaisesRegex(ValueError,'overlap'):studio.load(self.save(self.p))

    def test_unverified_claim_rejected(self):
        self.p['claims'][0]['status']='pending'
        with self.assertRaisesRegex(ValueError,'not verified'):studio.load(self.save(self.p))

    def test_broken_source_reference_rejected(self):
        self.p['claims'][0]['sources']=['missing']
        with self.assertRaisesRegex(ValueError,'missing source'):studio.load(self.save(self.p))

    def test_factual_subtitle_without_claim_rejected(self):
        self.p['subtitles'][0]['claims']=[]
        with self.assertRaisesRegex(ValueError,'factual subtitle'):studio.load(self.save(self.p))

    def test_odd_output_size_rejected(self):
        self.p['width']=1919
        with self.assertRaisesRegex(ValueError,'even integer'):studio.load(self.save(self.p))

    def test_audio_has_exact_duration_and_is_nonzero(self):
        self.p['duration']=1.25
        path=studio.synth(self.root,self.p)
        import numpy as np
        with wave.open(str(path),'rb') as f:
            self.assertEqual(f.getnframes(),60000)
            pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        self.assertGreater(abs(pcm).max(),100)
        self.assertLess(abs(pcm).max(),32767)

if __name__=='__main__':unittest.main()
