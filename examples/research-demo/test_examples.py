"""Meaningful known-answer and invalid-input tests for the teaching calculations."""
import csv, json, math, tempfile, unittest
from pathlib import Path
from statistics import fmean
import research
from equivalence import tost_normal


class TeachingCalculations(unittest.TestCase):
    def test_simple_ols_known_line(self):
        rows=[{'study_hours':x,'baseline':0,'score':5+3*x} for x in range(1,7)]
        fit=research.fit_ols(rows)
        self.assertAlmostEqual(fit['beta_hours'],3)
        self.assertAlmostEqual(fit['intercept'],5)
        self.assertAlmostEqual(fit['r_squared'],1)

    def test_adjusted_ols_known_plane(self):
        rows=[{'study_hours':x,'baseline':z,'score':5+3*x+2*z} for x,z in [(1,2),(2,3),(3,1),(4,5),(5,2),(6,4)]]
        fit=research.fit_ols(rows,True)
        for key,value in [('beta_hours',3),('beta_baseline',2),('intercept',5),('r_squared',1)]:
            self.assertAlmostEqual(fit[key],value)

    def test_singular_design_rejected(self):
        rows=[{'study_hours':x,'baseline':2*x,'score':5+3*x} for x in range(1,5)]
        with self.assertRaises(ValueError): research.fit_ols(rows,True)

    def test_data_and_all_paths(self):
        rows=research.load_data(research.ROOT/'synthetic.csv')
        self.assertEqual(len(rows),12)
        self.assertAlmostEqual(fmean(r['score'] for r in rows),808/12)
        paths=research.analysis_paths(rows)
        self.assertEqual(len(paths),6)
        self.assertEqual([p['n'] for p in paths],[12,12,10,10,8,8])
        self.assertTrue(all(math.isfinite(p['beta_hours']) for p in paths))

    def test_tost_independent_normal_tail(self):
        fit=tost_normal(0.2,0.15,-0.5,0.5)
        self.assertAlmostEqual(fit['p_tost'],math.erfc(2/math.sqrt(2))/2,places=12)
        self.assertAlmostEqual(fit['equivalence_interval'][0],-0.046728044043,places=10)
        self.assertAlmostEqual(fit['equivalence_interval'][1],0.446728044043,places=10)
        self.assertTrue(fit['equivalent']);self.assertFalse(fit['different_from_zero'])
        self.assertFalse(tost_normal(0.2,1,-0.5,0.5)['equivalent'])
        for args in [(0.2,0,-0.5,0.5),(0.2,1,0.5,-0.5),(float('nan'),1,-1,1)]:
            with self.assertRaises(ValueError): tost_normal(*args)

    def test_invalid_inputs_and_output_agreement(self):
        with tempfile.TemporaryDirectory(dir=research.ROOT) as folder:
            folder=Path(folder);bad=folder/'bad.csv'
            original=(research.ROOT/'synthetic.csv').read_text()
            for modified in [original.replace('S02','S01'),original.replace(',2,52,58,',',25,52,58,'),original.replace(',58,none',',nan,none'),original.replace(',none',',UNKNOWN')]:
                bad.write_text(modified)
                with self.assertRaises(ValueError): research.load_data(bad)
            result=research.run_project(output=folder/'output')
            summary=json.loads((folder/'output/summary.json').read_text())
            self.assertEqual(summary,result['summary'])
            with (folder/'output/paths.csv').open() as handle: exported=list(csv.DictReader(handle))
            self.assertEqual(len(exported),6)
            for saved,actual in zip(exported,result['paths']): self.assertEqual(float(saved['beta_hours']),actual['beta_hours'])
            self.assertIn(summary['source_sha256'],(folder/'output/index.html').read_text())


if __name__=='__main__': unittest.main()
