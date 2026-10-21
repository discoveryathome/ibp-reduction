"""Compare actual pinned Kira modular multiplication against a 128-bit oracle.

Requires the optional source/build under scratch; never patches upstream source.
"""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scratch/kira-3.0'
PROBE=r'''
#include "pyred/coeff_helper.h"
#include <cfloat>
#include <iostream>
#include <random>
// Link-only lifecycle state for the unused configuration methods in this TU.
bool pyred::Config::s_finished=false;
int main() {
  std::mt19937_64 rng(20261021);
  uint64_t m=9223372036854775783ULL, failures=0;
  for (int i=0;i<100000;i++) {
    uint64_t a=rng()%m,b=rng()%m;
    auto exact=(uint64_t)(((unsigned __int128)a*b)%m);
    failures += pyred::CoeffHelper::mod_mul(a,b,m)!=exact;
  }
  for(auto a:{0ULL,1ULL,m-1}) for(auto b:{0ULL,1ULL,m-1})
    failures += pyred::CoeffHelper::mod_mul(a,b,m)!=(uint64_t)(((unsigned __int128)a*b)%m);
  std::cout<<"{\"mantissa_bits\":"<<LDBL_MANT_DIG<<",\"cases\":100009,\"failures\":"<<failures<<"}";
}
'''
def main():
    rows=[]
    config=(SOURCE/'build/src/pyred/config.h').read_text()
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);(p/'pyred').mkdir();(p/'probe.cpp').write_text(PROBE)
        for mode in ('release','integer'):
            cfg=config.replace('#define VALGRIND','#undef VALGRIND')
            if mode=='integer':cfg=cfg.replace('#undef VALGRIND','#define VALGRIND')
            (p/'pyred/config.h').write_text(cfg)
            subprocess.run(['c++','-std=c++17','-O2','-I'+str(p),'-I'+str(SOURCE/'src'),str(p/'probe.cpp'),str(SOURCE/'src/pyred/coeff_helper.cpp'),'-o',str(p/'probe')],check=True)
            rows.append(dict(mode=mode,**json.loads(subprocess.check_output([str(p/'probe')],text=True))))
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),
      source_sha256=hashlib.sha256((SOURCE/'src/pyred/coeff_helper.cpp').read_bytes()).hexdigest(),rows=rows,
      scope='Deterministic architecture diagnostic, not exhaustive correctness proof.')
    (ROOT/'research/readiness-20261021/kira/arithmetic-probe.json').write_text(json.dumps(result,indent=2)+'\n')
    if rows[1]['failures']:raise ValueError(result)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
