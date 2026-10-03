#!/bin/sh
# Check that committed binaries are stripped static ARM64 executables without a
# dynamic interpreter or shared library dependencies.
set -eu

BIN_DIR=${BIN_DIR:-/opt/bin}

for binary in "$@"; do
    file "$BIN_DIR/$binary" | grep -Eq 'ARM aarch64.*(statically linked|static-pie linked).*stripped$'
    readelf -h "$BIN_DIR/$binary" | grep -q 'Machine:.*AArch64'
    if readelf -l "$BIN_DIR/$binary" | grep -q INTERP ||
       readelf -d "$BIN_DIR/$binary" | grep -q NEEDED; then
        echo "ERROR: $binary requires a dynamic loader or library" >&2
        exit 1
    fi
    echo "Static ARM64 OK: $binary"
done
