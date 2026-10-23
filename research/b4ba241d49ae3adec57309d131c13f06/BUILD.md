# Source build recipe used for the native replication

All paths below are inside one disposable task workspace. `ibp-reduction/` is
this checkout, and `predecessor/` is the clean pinned PR #7 checkout described in
the README. Screen downloaded sources before executing their build scripts.
Keep the inherited network/proxy configuration and TLS checks enabled.

Source pins and digests are in `BUILD.json`. CLN/GiNaC archives match the original
project's recorded archive hashes; git source commits were checked before builds.
Fermat was obtained directly from its author's site under its own terms and is
not redistributed. This recipe does not authorize changing the project's license.

The host supplied GCC 14.2.0, CMake 3.31.6, GNU make, GMP 6.3.0 and zlib 1.3.1
with development headers. Only workspace-local environments/prefixes were used.
The build occupied well under 1 GiB; no global installation was performed.

From the task workspace:

```sh
TASK_WORKSPACE="$PWD"
TASK_PREFIX="$TASK_WORKSPACE/kira-prefix"
TASK_PYTHON="$TASK_WORKSPACE/ibp-reduction/.venv/bin/python"
mkdir -p downloads build-tools kira-prefix
python3 -m venv ibp-reduction/.venv
"$TASK_PYTHON" -m pip install --no-cache-dir -r ibp-reduction/requirements.txt \
  meson==1.12.1 ninja==1.13.2

git clone --branch 3.0 --depth 1 https://gitlab.com/kira-pyred/kira.git kira-source
git -C kira-source rev-parse HEAD
# fb745431f97c8899a512e638da8598b0cfad7521
git clone --branch yaml-cpp-0.7.0 --depth 1 https://github.com/jbeder/yaml-cpp.git \
  build-tools/yaml-cpp-source
git -C build-tools/yaml-cpp-source rev-parse HEAD
# 0579ae3d976091d7d664aa9d2527e0d0cff25763
curl -fL -o downloads/cln-1.3.7.tar.bz2 https://www.ginac.de/CLN/cln-1.3.7.tar.bz2
curl -fL -o downloads/ginac-1.8.10.tar.bz2 https://www.ginac.de/ginac-1.8.10.tar.bz2
curl -fL -o downloads/Ferl7.tar.gz https://home.bway.net/lewis/fermat64/Ferl7.tar.gz
sha256sum downloads/*
# Compare every digest to BUILD.json before extracting.
tar --no-same-owner -xjf downloads/cln-1.3.7.tar.bz2 -C build-tools
tar --no-same-owner -xjf downloads/ginac-1.8.10.tar.bz2 -C build-tools
tar --no-same-owner -xzf downloads/Ferl7.tar.gz -C build-tools

cd "$TASK_WORKSPACE/build-tools/cln-1.3.7"
./configure --prefix="$TASK_PREFIX" --with-gmp --disable-static
make -j4
make install

cd "$TASK_WORKSPACE/build-tools/ginac-1.8.10"
PKG_CONFIG_PATH="$TASK_PREFIX/lib/pkgconfig" ./configure --prefix="$TASK_PREFIX" --disable-static
make -j4
make install

cd "$TASK_WORKSPACE"
cmake -S build-tools/yaml-cpp-source -B build-tools/yaml-cpp-build \
  -DCMAKE_INSTALL_PREFIX="$TASK_PREFIX" -DYAML_BUILD_SHARED_LIBS=ON \
  -DYAML_CPP_BUILD_TESTS=OFF -DYAML_CPP_BUILD_TOOLS=OFF -DYAML_CPP_INSTALL=ON
cmake --build build-tools/yaml-cpp-build -j4
cmake --install build-tools/yaml-cpp-build

export PATH="$TASK_WORKSPACE/ibp-reduction/.venv/bin:$PATH"
export PKG_CONFIG_PATH="$TASK_PREFIX/lib/pkgconfig"
export CMAKE_PREFIX_PATH="$TASK_PREFIX"
export LD_LIBRARY_PATH="$TASK_PREFIX/lib:$TASK_PREFIX/lib64"
meson setup kira-source/build kira-source --prefix="$TASK_PREFIX" \
  --buildtype=release -Dfirefly=false -Dflint=false --wrap-mode=nodownload
ninja -C kira-source/build -j4
ninja -C kira-source/build install
"$TASK_PREFIX/bin/kira" --version

TASK_PACKAGE="$TASK_WORKSPACE/ibp-reduction/research/b4ba241d49ae3adec57309d131c13f06"
"$TASK_PYTHON" "$TASK_PACKAGE/probe_arithmetic.py" \
  --predecessor predecessor --source kira-source --out arithmetic-replay.json
# Both paths: 100009 cases, mantissa_bits=64, failures=0 on this Linux host.

"$TASK_PYTHON" predecessor/tools/export_kira_one_loop.py --out native-replay
export FERMATPATH="$TASK_WORKSPACE/build-tools/Ferl7/fer64"
"$TASK_PYTHON" "$TASK_PACKAGE/run_native.py" --predecessor predecessor \
  --inputs native-replay --kira "$TASK_PREFIX/bin/kira"
"$TASK_PYTHON" "$TASK_PACKAGE/verify_saved.py" --predecessor predecessor \
  --data native-replay
```

The delivered run used the same default family order in two calls: `--families
tadpole`, then the other six families, so the first native control was inspected
before proceeding. `run_native.py` refuses duplicate trials; generate a fresh input
tree for each repeat. It writes complete logs and receipts before stopping on a
failure. The original exporter refuses to overwrite an existing output directory.

All configure/build/install outputs from the actual build are in `logs/`.
The downloaded sources and original build trees stay local; source hashes,
executable/library digests, native inputs/outputs and logs are the shared receipt.
The recipe's dependency build order is sequential for readability; yaml-cpp was
built alongside CLN during the delivered session. No source patch was applied.
