# Exact Kira cross-check and Apple Silicon arithmetic diagnostic

Kira 3.0, commit `fb745431f97c8899a512e638da8598b0cfad7521`, independently
reduced the same nine sunset targets to the same two preferred masters. All
coefficients match both local certificate implementations as exact rational
functions of generic `d` and nonzero squared mass `m`. See `comparison.json`.
This is software cross-validation by the same author, not independent human review.
No production speed or broad multi-loop performance claim follows.

Recheck the saved export without installing Kira:

```sh
python tools/check_kira.py
python -m unittest discover -s tests -p test_kira.py -v
```

The importer rejects an empty export, missing targets, a different master basis,
incorrect coefficients and executable expressions. Exit status zero alone is
insufficient. `kira_targets.kira` is the raw successful text export; `masters`
contains the two master integrals. `run-receipt.json` binds the locally built
executable and source revision. `sunset/` contains exact input files.

## Conventions

Kira propagators use momentum squared minus the supplied mass-squared expression.
The supplied `-m` therefore gives `k1^2+m`, `k2^2+m`, `(k1-k2)^2+m`, matching the
formal Euclidean vacuum family. No external momenta or kinematic invariants are
introduced besides `m`. Master choices are `sunset[1,1,1]` and `sunset[1,1,0]`.
The nine non-master targets include three numerator insertions. All local target
indices are already in the same canonical permutation convention as the export.
Master minimality is not asserted.

## Arithmetic issue and tested workaround

On this Apple M2/macOS host, `LDBL_MANT_DIG` is 53. The release implementation of
`pyred::CoeffHelper::mod_mul` explicitly assumes at least 64 mantissa bits. A
fixed-seed probe of the actual pinned upstream function, using the first upstream
prime and a separate `unsigned __int128` remainder oracle, found **96,911 failures
in 100,009 cases**. The upstream integer implementation had **zero failures**.
`arithmetic-probe.json` records both outcomes and the source hash.

The initial release sunset runs and an upstream one-loop box control returned zero
exit status but zero masters and empty reduction output. They are failed controls,
retained in `sunset-run.log`, `sunset-v2.log` and `upstream-control.log`. Rebuilding
with upstream `--buildtype=debugoptimized` defines `VALGRIND` and selects integer
modular multiplication without patching Kira. The same sunset inputs then reduced
successfully in about 4.7 seconds. The before/after result is evidence for this
local arithmetic diagnosis; a Kira maintainer should review the architecture issue.
No issue or external message has been sent.

## Optional native reproduction

The original build lived under ignored `scratch/`; no libraries or tools were
installed globally and no third-party executable is bundled. These are the pinned
upstream sources used, with downloaded archive digests in `dependency-archives.json`:

- [Kira 3.0](https://gitlab.com/kira-pyred/kira/-/tree/3.0), commit above.
- [CLN 1.3.7](https://www.ginac.de/CLN/cln-1.3.7.tar.bz2).
- [GiNaC 1.8.10](https://www.ginac.de/ginac-1.8.10.tar.bz2).
- [yaml-cpp 0.7.0](https://github.com/jbeder/yaml-cpp/releases/tag/yaml-cpp-0.7.0).
- [Fermat 7.9b for Apple ARM](https://home.bway.net/lewis/fermat64/), acquired
  separately under its author's terms; not redistributed here.

The local Python environment supplied Meson 1.12.1, Ninja 1.13.2 and CMake. Existing
Homebrew GMP was used. CLN and GiNaC were configured with a local prefix; yaml-cpp
used shared libraries with tests/tools disabled. In a shell with those dependencies
available (adjust `prefix` to your own local installation):

```sh
prefix="$PWD/scratch/kira-prefix"
export PATH="$PWD/.venv/bin:$PATH"
export PKG_CONFIG_PATH="$prefix/lib/pkgconfig:$prefix/share/pkgconfig:/opt/homebrew/lib/pkgconfig"
export CMAKE_PREFIX_PATH="$prefix"
meson setup scratch/kira-3.0/build scratch/kira-3.0 --prefix="$prefix" \
  --buildtype=debugoptimized -Dfirefly=false -Dflint=false --wrap-mode=nodownload
ninja -C scratch/kira-3.0/build -j6
ninja -C scratch/kira-3.0/build install
python tools/probe_kira_arithmetic.py
```

Copy the `sunset/` input directory to a fresh working directory. Run the installed
Kira there with `--parallel=1 jobs.yaml`, `FERMATPATH` pointing to the separately
obtained Fermat executable, and on macOS `DYLD_LIBRARY_PATH` containing the local
prefix's `lib`. Compare its `results/sunset/kira_targets.kira` with:

```sh
python tools/check_kira.py --export /path/to/fresh/results/sunset/kira_targets.kira
```

The alternate arithmetic path is essential to this tested Apple Silicon setup.
Do not reuse the broken release build or accept an empty output. A different host
should report its compiler, architecture, mantissa width and probe result.
