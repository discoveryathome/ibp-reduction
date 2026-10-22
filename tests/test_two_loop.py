import copy,json,unittest
from pathlib import Path
from ibp.validator import check
class TwoLoopTests(unittest.TestCase):
 def test_saved_certificates_and_numerator_coverage(self):
  for name in ('sparse','online'):
   c=json.loads(Path(f'research/readiness-20261021/two-loop-{name}.json').read_text())
   self.assertEqual(check(c)['identities'],9)
   bad=copy.deepcopy(c);bad['outputs']=[o for o in bad['outputs'] if min(o['target'])>=0]
   with self.assertRaises(ValueError):check(bad)
if __name__=='__main__':unittest.main()
