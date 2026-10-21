import json,unittest
from tools.check_kira import OUT,compare,expression
class KiraTests(unittest.TestCase):
    def test_export_positive_and_negative_controls(self):
        c=json.loads((OUT/'two-loop-online.json').read_text());text=(OUT/'kira/kira_targets.kira').read_text()
        self.assertEqual(compare(text,c),9)
        for bad in ('',text.replace('(-d+3)','(-d+4)',1),text.split('\n\n',1)[1]):
            with self.assertRaises(ValueError):compare(bad,c)
    def test_coefficient_parser_rejects_calls(self):
        with self.assertRaises(ValueError):expression('print(123)')
if __name__=='__main__':unittest.main()
