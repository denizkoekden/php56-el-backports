#!/bin/bash
# Usage: ./build.sh [el6] [el7]   (default: both). Needs Docker; RPMs end up in dist/<el>/.
set -euo pipefail
cd "$(dirname "$0")"
. ./sources.env

sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | awk '{print $1}'; }

fetch() {
    local file="$1" want="$2"
    if [ ! -f "sources/$file" ]; then
        local url="$SURY_BASE/$(printf '%s' "$file" | sed 's/+/%2B/g; s/~/%7E/g')"
        curl -fsSL -o "sources/$file" "$url"
    fi
    [ "$(sha256 "sources/$file")" = "$want" ] || { echo "checksum mismatch: $file"; exit 1; }
}

mkdir -p sources dist
fetch "$ORIG_TAR" "$ORIG_SHA256"
fetch "$DEBIAN_TAR" "$DEBIAN_SHA256"

for el in "${@:-el6 el7}"; do
    for t in $el; do
        docker build --platform linux/amd64 -t "php56-build-$t" "docker/$t"
        docker run --rm --platform linux/amd64 -v "$PWD:/work" "php56-build-$t" /work/scripts/rpmbuild.sh "$t"
    done
done
