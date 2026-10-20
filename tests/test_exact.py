import copy,json,unittest
import sympy as S
from ibp.reducer import BASELINES,reduce,encode_row
from ibp.validator import check,prune,decode,input_row,exact_zero,D,s,m
from ibp.families import NAMES,family,equations

class ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate=prune(reduce('bubble_massless',BASELINES['sparse']))
    def test_certificate(self):self.assertTrue(check(self.certificate)['valid'])
    def test_reject_changed_output(self):
        c=copy.deepcopy(self.certificate);c['outputs'][0]['row'][0][1][0][0][1]+=1
        with self.assertRaises(ValueError):check(c)
    def test_reject_missing_target(self):
        c=copy.deepcopy(self.certificate);c['outputs'].pop()
        with self.assertRaises(ValueError):check(c)
    def test_reject_zero_denominator(self):
        c=copy.deepcopy(self.certificate);c['outputs'][0]['row'][0][1][1]=[]
        with self.assertRaises(ValueError):check(c)
    def test_reject_forward_reference(self):
        c=copy.deepcopy(self.certificate)
        node=next(x for x in c['nodes'] if x['op']=='scale');node['row']=len(c['nodes'])
        with self.assertRaises(ValueError):check(c)
    def test_reject_changed_proof(self):
        c=copy.deepcopy(self.certificate)
        node=next(x for x in c['nodes'] if x['op']=='input');node['seed'][0]+=2
        with self.assertRaises(ValueError):check(c)
    def test_reject_unreduced_master(self):
        c=copy.deepcopy(self.certificate);o=c['outputs'][0];o['row'].append([[9,9],o['row'][0][1]])
        with self.assertRaises(ValueError):check(c)
    def test_reject_fake_symmetry(self):
        c=copy.deepcopy(self.certificate);c['nodes'][0]={'op':'symmetry'}
        with self.assertRaises(ValueError):check(c)
    def test_reject_polynomial_that_matches_three_dimensions(self):
        from ibp.families import FIELD
        from ibp.reducer import encode
        c=copy.deepcopy(self.certificate);out=c['outputs'][0]
        entry=next(e for e in out['row'] if e[0]==[1,1])
        entry[1]=encode(FIELD.from_sympy(decode(entry[1])+(D-4)*(D-6)*(D-8)))
        with self.assertRaises(ValueError):check(c)
    def test_online_certificate_and_accounting(self):
        from ibp.contributor import online
        c=online('triangle_one_mass',dict(seed='rectangular',order='sector',schedule='simple',reuse=True),True)
        self.assertTrue(c['metrics']['success'])
        self.assertTrue(check(prune(c))['valid'])
        self.assertEqual(c['metrics']['attempted_operations'],c['metrics']['arithmetic_operations']+c['metrics']['cache_hits'])
    def test_fallback_costs_include_failed_cache_hits(self):
        from ibp.experiment import guarded
        c=guarded('box_massless',dict(BASELINES['improved'],reuse=True))
        self.assertTrue(c['metrics']['fallback'])
        self.assertEqual(c['metrics']['attempted_operations'],c['metrics']['arithmetic_operations']+c['metrics']['cache_hits'])
    def test_known_massless_bubble_gamma_ratio(self):
        for out in self.certificate['outputs']:
            a,b=out['target'];r={tuple(k):decode(v) for k,v in out['row']};q=a+b-2
            expected=(-1)**q*S.rf(2-D/2,q)*S.rf(D-a-b,q)/(S.rf(2-D/2,a-1)*S.rf(2-D/2,b-1)*S.factorial(a-1)*S.factorial(b-1)*s**q)
            self.assertTrue(exact_zero(-r[(1,1)]-expected))
    def test_known_tadpole_gamma_ratio(self):
        c=prune(reduce('tadpole',BASELINES['laporta']));self.assertTrue(check(c)['valid'])
        for out in c['outputs']:
            a=out['target'][0];r={tuple(k):decode(v) for k,v in out['row']}
            expected=S.rf(1-D/2,a-1)/(S.factorial(a-1)*m**(a-1))
            self.assertTrue(exact_zero(-r[(1,)]-expected))
    def test_independent_input_derivation(self):
        # Every input on small families; deterministic strided sample on medium.
        for name in NAMES:
            rows=list(equations(family(name)))
            for a,j,row in rows[::max(1,len(rows)//12)]:
                independent=input_row(name,list(a),j)
                original={tuple(k):decode(v) for k,v in encode_row(row)}
                for k in set(independent)|set(original):
                    self.assertTrue(exact_zero(independent.get(k,0)-original.get(k,0)),(name,a,j,k))
    def test_reuse_preserves_results_and_cost_accounting(self):
        c=reduce('triangle_one_mass',dict(BASELINES['sparse'],reuse=True))
        self.assertTrue(check(prune(c))['valid'])
        self.assertEqual(c['metrics']['attempted_operations'],c['metrics']['arithmetic_operations']+c['metrics']['cache_hits'])

if __name__=='__main__':unittest.main()
