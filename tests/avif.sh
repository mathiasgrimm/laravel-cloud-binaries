#!/bin/sh
set -eu

BIN_DIR=${BIN_DIR:-/opt/bin}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

# Check the committed artifacts, not only the Docker builder's outputs.
for binary in avifenc avifdec; do
    file "$BIN_DIR/$binary" | grep -Eq 'ARM aarch64.*(statically linked|static-pie linked).*stripped$'
    readelf -h "$BIN_DIR/$binary" | grep -q 'Machine:.*AArch64'
    if readelf -l "$BIN_DIR/$binary" | grep -q INTERP ||
       readelf -d "$BIN_DIR/$binary" | grep -q NEEDED; then
        echo "ERROR: $binary requires a dynamic loader or library" >&2
        exit 1
    fi
    "$BIN_DIR/$binary" --version > "$tmp/version"
    grep -q 'Version: 1.2.1' "$tmp/version"
    grep -q 'dav1d \[dec\]:1.5.1' "$tmp/version"
    grep -q 'aom \[enc/dec\]' "$tmp/version"
done

# Generated fixtures avoid external downloads. Include nonconstant color and alpha.
"$BIN_DIR/magick" -size 128x128 gradient:'#143879-#efc521' -depth 16 "$tmp/rgb.png"
"$BIN_DIR/magick" "$tmp/rgb.png" \( -size 128x128 gradient:black-white \) \
    -alpha off -compose CopyOpacity -composite -depth 16 "$tmp/rgba.png"

for depth in 8 10 12; do
    for format in 420 444; do
        for channels in rgb rgba; do
            for layout in still grid; do
                name="$depth-$format-$channels-$layout"
                set --
                if [ "$layout" = grid ]; then set -- --grid 2x2; fi
                # Omitting --codec must still select AOM for encoding.
                "$BIN_DIR/avifenc" -j 1 -s 10 -d "$depth" -y "$format" "$@" \
                    "$tmp/$channels.png" "$tmp/$name.avif" > "$tmp/encode.log"
                grep -q 'codec.*aom' "$tmp/encode.log"
                for codec in auto dav1d aom; do
                    set --
                    if [ "$codec" != auto ]; then set -- --codec "$codec"; fi
                    "$BIN_DIR/avifdec" -j 1 -d 16 "$@" "$tmp/$name.avif" \
                        "$tmp/$codec.png" > "$tmp/$codec.log"
                    expected=$codec
                    if [ "$codec" = auto ]; then expected=dav1d; fi
                    grep -q "Decoding with codec '$expected'" "$tmp/$codec.log"
                    grep -q "Bit Depth.*$depth" "$tmp/$codec.log"
                    # Compare all RGBA samples, including alpha at 16-bit output depth.
                    "$BIN_DIR/magick" "$tmp/$codec.png" -depth 16 "rgba:$tmp/$codec.rgba"
                done
                cmp "$tmp/auto.rgba" "$tmp/dav1d.rgba"
                cmp "$tmp/auto.rgba" "$tmp/aom.rgba"
                test "$("$BIN_DIR/magick" "$tmp/auto.png" -format '%wx%h' info:)" = 128x128
                if [ "$channels" = rgba ]; then
                    test "$("$BIN_DIR/magick" "$tmp/auto.png" -format '%[opaque]' info:)" = False
                fi
                echo "AVIF parity OK: $name"
            done
        done
    done
done

# Explicit AOM encoding remains available, and lossless RGBA survives the round trip.
"$BIN_DIR/magick" "$tmp/rgba.png" -depth 8 "$tmp/lossless.png"
"$BIN_DIR/avifenc" --codec aom -j 1 -s 10 --lossless \
    "$tmp/lossless.png" "$tmp/lossless.avif" > "$tmp/encode.log"
"$BIN_DIR/avifdec" -j 1 "$tmp/lossless.avif" "$tmp/roundtrip.png" > "$tmp/decode.log"
"$BIN_DIR/magick" "$tmp/lossless.png" -depth 8 "rgba:$tmp/input.rgba"
"$BIN_DIR/magick" "$tmp/roundtrip.png" -depth 8 "rgba:$tmp/output.rgba"
cmp "$tmp/input.rgba" "$tmp/output.rgba"
echo 'Static ARM64 AVIF, default dav1d, AOM encoding/fallback and pixel parity OK'
