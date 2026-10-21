#!/bin/bash
# Runs inside the build container: builds the RPMs and runs a smoke test against the installed tree.
set -euo pipefail
el="$1"
out="/work/dist/$el"
mkdir -p "$out" ~/rpmbuild/SOURCES ~/rpmbuild/SPECS
cp /work/sources/* ~/rpmbuild/SOURCES/
cp /work/php56.spec ~/rpmbuild/SPECS/
rpmbuild -ba ~/rpmbuild/SPECS/php56.spec > "$out/build.log" 2>&1 || { tail -40 "$out/build.log"; exit 1; }
cp ~/rpmbuild/RPMS/x86_64/*.rpm ~/rpmbuild/SRPMS/*.rpm "$out/"

# Smoke test: install everything, then every extension must load without warnings.
yum -y -q localinstall "$out"/php56-*.x86_64.rpm > /dev/null
php=/opt/php56/bin/php
"$php" -v | head -1
"$php" -m > "$out/modules.txt" 2> "$out/modules.err"
[ ! -s "$out/modules.err" ] || { echo "extension load warnings:"; cat "$out/modules.err"; exit 1; }
echo "modules: $(grep -cvE '^\[|^$' "$out/modules.txt")"
/opt/php56/bin/php-cgi -v | head -1
/opt/php56/sbin/php-fpm -v | head -1
"$php" -r 'echo idn_to_ascii("bücher.example"), " ", json_encode(["ok" => true]), PHP_EOL;'
