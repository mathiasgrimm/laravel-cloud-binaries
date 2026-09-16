#!/bin/sh
set -eu

BIN_DIR=${BIN_DIR:-/opt/bin}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

# Exercise codec-name lookup used by ImageMagick, not just libwebp listing.
"$BIN_DIR/ffmpeg" -nostdin -v error -f lavfi -i 'testsrc=size=16x16:rate=2' \
    -frames:v 1 -vcodec webp "$tmp/still.webp"
test "$("$BIN_DIR/ffprobe" -v error -select_streams v:0 \
    -show_entries stream=codec_name,width,height -of csv=p=0 "$tmp/still.webp")" = 'webp,16,16'
"$BIN_DIR/ffmpeg" -nostdin -v error -i "$tmp/still.webp" -f null -

# Generate three frames so ffmpeg can infer the APNG frame rate.
# Two frames leave r_frame_rate at 100000/1 and cause delegate duplication.
"$BIN_DIR/ffmpeg" -nostdin -v error -f lavfi -i 'testsrc=size=16x16:rate=2' \
    -frames:v 3 -plays 1 -f apng "$tmp/input.png"

# ImageMagick 7.1.2-31's video:decode delegate plus APNG options from coders/video.c.
# It writes extensionless output through the rawvideo muxer.
"$BIN_DIR/ffmpeg" -nostdin -loglevel error -i "$tmp/input.png" \
    -an -f rawvideo -y -pix_fmt rgba -vcodec webp "$tmp/decoded"
test -s "$tmp/decoded"
# Animated WebP may store changed rectangles; coalesce before checking dimensions.
test "$("$BIN_DIR/magick" "webp:$tmp/decoded" -coalesce -format '%w,%h\n' info:)" = "$(printf '16,16\n16,16\n16,16')"

# Exercise the bundled ImageMagick too; 7.1.1-43 also passes -lossless 1.
test "$(PATH="$BIN_DIR:$PATH" "$BIN_DIR/magick" "APNG:$tmp/input.png" \
    -coalesce -format '%w,%h\n' info:)" = "$(printf '16,16\n16,16\n16,16')"

# Keep the PAM codec used by older ImageMagick delegates working too.
"$BIN_DIR/ffmpeg" -nostdin -loglevel error -i "$tmp/input.png" \
    -an -f rawvideo -y -pix_fmt rgba -vcodec pam "$tmp/decoded.pam"
test "$("$BIN_DIR/magick" "$tmp/decoded.pam" -format '%w,%h\n' info:)" = "$(printf '16,16\n16,16\n16,16')"

echo 'FFmpeg WebP encoding and APNG delegates OK'
