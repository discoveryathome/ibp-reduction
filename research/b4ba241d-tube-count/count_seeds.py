"""Reproduce the frozen Eq. (16) on-cut tube sets; no upstream code or solve.

Construction: Berman et al., arXiv:2606.10698v1 Eqs. (12), (16).
Author source/data pin: ec955d46f26ef497ca5ee7053f6f0286efb7971b.
This is a fixed 11-index, zero-dot, width-four, cut-[1,3,6,8] experiment.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations_with_replacement
import json
from math import comb
from pathlib import Path
import platform
import resource
import time

HERE = Path(__file__).resolve().parent
TRIVIAL_SHA256 = '36a0b7e133584d892301d8b2e167ec81c565d6ab9129cbcabc1f0514e4bbc57f'
CUT_MASK = 165  # One-based propagators 1, 3, 6, 8.
EXCEPTION_MASK = 167
RANKS = (4, 5, 6)
PUBLISHED = {4: 358, 5: 589, 6: 820}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def trivial_sectors():
    path = HERE / 'fixtures/trivialsector'
    if digest(path) != TRIVIAL_SHA256:
        raise ValueError('trivial-sector fixture differs from the pinned source')
    values = list(map(int, path.read_text().strip().split(',')))
    if len(set(values)) != len(values) or any(not 0 <= s < 2**11 for s in values):
        raise ValueError('malformed trivial-sector fixture')
    return frozenset(values)


def sectors():
    trivial = trivial_sectors()
    return tuple(s for s in range(256) if s & CUT_MASK == CUT_MASK and s not in trivial)


def cap(sector):
    # The exception applies to sector 167 and all of its subsectors.
    return max(1, sector.bit_count() - 4 + int(sector & ~EXCEPTION_MASK == 0))


def check_rank(rank):
    if type(rank) is not int or rank < 4:
        raise ValueError('this experiment requires an integer rank >= 4')


def enumerate_seeds(rank):
    check_rank(rank)
    result = set()
    for sector in sectors():
        support = tuple((sector >> i) & 1 for i in range(11))
        absent = tuple(i for i, a in enumerate(support) if not a)
        # A numerator monomial is a multiset of absent index positions.
        for degree in range(cap(sector) + 1):
            for monomial in combinations_with_replacement(absent, degree):
                counts = Counter(monomial)
                base = tuple(a - counts[i] for i, a in enumerate(support))
                for shift in range(rank - 3):
                    result.add(base[:-1] + (base[-1] - shift,))
    return sorted(result)


def sector_counts(rank):
    """Count contiguous last-index columns, independently of tuple generation."""
    check_rank(rank)
    rows = {}
    for sector in sectors():
        z, width = 11 - sector.bit_count(), cap(sector)
        rows[sector] = comb(width + z, z) + (rank - 4) * comb(width + z - 1, z - 1)
    return rows


def validate(seeds, rank):
    check_rank(rank)
    unique = set()
    counts = Counter()
    allowed = frozenset(sectors())
    for seed in seeds:
        if len(seed) != 11 or any(type(a) is not int for a in seed):
            raise ValueError('a seed must have 11 integer indices')
        seed = tuple(seed)
        if seed in unique:
            raise ValueError('duplicate seed in the unique-set artifact')
        unique.add(seed)
        if any(a > 1 for a in seed[:8]) or any(a > 0 for a in seed[8:]):
            raise ValueError('dots or positive ISP outside the frozen construction')
        sector = sum(1 << i for i, a in enumerate(seed) if a > 0)
        if sector not in allowed:
            raise ValueError('seed is off cut or outside a nontrivial top-sector subsector')
        transverse = sum(-a for a in seed[:-1] if a < 0)
        if transverse > cap(sector) or -seed[-1] > cap(sector) - transverse + rank - 4:
            raise ValueError('seed lies outside its contiguous tube column')
        counts[sector] += 1
    if dict(counts) != sector_counts(rank):
        raise ValueError('incomplete or incorrect per-sector unique counts')
    if rank in PUBLISHED and len(unique) != PUBLISHED[rank]:
        raise ValueError('published count disagreement')
    return len(unique)


def read_seeds(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    if any(type(row) is not list for row in rows):
        raise ValueError('expected one index-array per line')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path, help='New output directory; existing paths are refused.')
    group.add_argument('--check', type=Path, help='Read and validate previously saved tuple sets.')
    args = parser.parse_args()
    if args.check:
        rows = {rank: validate(read_seeds(args.check / f'rank-{rank}.jsonl'), rank) for rank in RANKS}
        print(json.dumps(dict(valid=True, counts=rows, scope='Frozen seed sets only; no reduction.')))
        return
    args.out.mkdir(parents=True, exist_ok=False)
    rows = []
    for rank in RANKS:
        start = time.perf_counter()
        seeds = enumerate_seeds(rank)
        elapsed = time.perf_counter() - start
        count = validate(seeds, rank)
        path = args.out / f'rank-{rank}.jsonl'
        path.write_text(''.join(json.dumps(seed, separators=(',', ':')) + '\n' for seed in seeds))
        rows.append(dict(rank=rank, unique_seeds=count, enumeration_seconds=elapsed,
                         sha256=digest(path), by_sector=sector_counts(rank)))
    report = dict(evidence_level='author-checked', python=platform.python_version(),
                  source_sha256=digest(__file__), fixture_sha256=TRIVIAL_SHA256,
                  peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if platform.system() == 'Darwin' else 1024),
                  rss_scope='Process maximum including interpreter/setup/checks; Darwin bytes/Linux KiB; not reduction memory.',
                  rows=rows, upstream_code_executed=False, reduction_performed=False)
    (args.out / 'counts.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
