#!/usr/bin/env python3
"""Check that ImageMagick converts pixels between ICC profiles with Little CMS.

Without the LCMS delegate, `-profile` only attaches the target profile and the
pixels keep their Display P3 values. Imagick::profileImage('icc', ...) calls the
same ProfileImage() code as the `-profile` option tested here.
"""

import atexit
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icc_profiles import DISPLAY_P3_PRIMARIES, SRGB_PRIMARIES, convert, display_p3_profile, srgb_profile  # noqa: E402
from png_files import write_png  # noqa: E402

BIN = os.environ.get("BIN_DIR", "/opt/bin")
MAGICK = os.path.join(BIN, "magick")
TOLERANCE = 1  # 8-bit levels, for fixed-point profile values and rounding


def magick(*args):
    return subprocess.run([MAGICK, *args], check=True, capture_output=True).stdout


def pixels(path, channels="rgb"):
    raw = magick(path, "-depth", "8", f"{channels}:-")
    n = len(channels)
    return [tuple(raw[i:i + n]) for i in range(0, len(raw), n)]


def check(label, actual, expected):
    worst = max(abs(a - e) for got, want in zip(actual, expected) for a, e in zip(got, want))
    if len(actual) != len(expected) or worst > TOLERANCE:
        for got, want in zip(actual, expected):
            print(f"  {label}: got {got}, expected {want}", file=sys.stderr)
        raise SystemExit(f"{label}: off by up to {worst} levels")
    print(f"{label}: OK (max difference {worst})")


version = magick("-version").decode()
delegates = next(line for line in version.splitlines() if line.startswith("Delegates"))
assert "lcms" in delegates.split(":", 1)[1].split(), delegates

tmp = tempfile.mkdtemp(prefix="magick-icc-")
atexit.register(shutil.rmtree, tmp, ignore_errors=True)
srgb_icc, p3_icc = os.path.join(tmp, "srgb.icc"), os.path.join(tmp, "p3.icc")
with open(srgb_icc, "wb") as fh:
    fh.write(srgb_profile())
with open(p3_icc, "wb") as fh:
    fh.write(display_p3_profile())

# Saturated sRGB colors expressed in Display P3, plus neutrals and one P3 primary
# outside the sRGB gamut, which is clipped.
targets = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
           (255, 0, 255), (255, 128, 0), (128, 128, 128), (255, 255, 255), (0, 0, 0)]
p3_pixels = [convert(c, SRGB_PRIMARIES, DISPLAY_P3_PRIMARIES) for c in targets] + [(255, 0, 0)]
expected = [convert(c, DISPLAY_P3_PRIMARIES, SRGB_PRIMARIES) for c in p3_pixels]
for p3, want in zip(p3_pixels, expected):
    print(f"Display P3 {p3} -> sRGB {want}")
assert p3_pixels[0] == (234, 51, 35), p3_pixels[0]

flat = bytes(v for p in p3_pixels for v in p)
p3_png = os.path.join(tmp, "p3.png")
write_png(p3_png, len(p3_pixels), 1, flat, 3, icc=display_p3_profile())

# The source profile is the embedded Display P3 profile.
out = os.path.join(tmp, "srgb.png")
magick(p3_png, "-profile", srgb_icc, out)
converted = pixels(out)
check("-profile converts Display P3 to sRGB", converted, expected)
assert max(abs(a - b) for p, q in zip(p3_pixels, converted) for a, b in zip(p, q)) >= 50
description = magick(out, "-format", "%[icc:description]", "info:").decode()
assert description == "Test sRGB (generated)", description

# The reference metric preparation: first frame, ICC conversion, 8-bit PNG24.
prepared = os.path.join(tmp, "prepared.png")
magick(p3_png + "[0]", "-profile", srgb_icc, "-alpha", "off", "-depth", "8", "PNG24:" + prepared)
check("metric preparation converts", pixels(prepared), expected)

# An explicit source profile followed by the target gives the same pixels.
untagged = os.path.join(tmp, "untagged.png")
write_png(untagged, len(p3_pixels), 1, flat, 3)
explicit = os.path.join(tmp, "explicit.png")
magick(untagged, "-profile", p3_icc, "-profile", srgb_icc, explicit)
check("explicit source and target profiles convert", pixels(explicit), expected)

# Without a source profile, -profile only assigns the target profile.
assigned = os.path.join(tmp, "assigned.png")
magick(untagged, "-profile", srgb_icc, assigned)
check("untagged input is assigned, not converted", pixels(assigned), p3_pixels)

# Alpha is kept unchanged while the colors are converted.
alphas = [255, 192, 128, 64, 1, 255, 200, 100, 50, 25, 255]
rgba = bytes(v for p, a in zip(p3_pixels, alphas) for v in (*p, a))
p3_rgba = os.path.join(tmp, "p3-rgba.png")
write_png(p3_rgba, len(p3_pixels), 1, rgba, 4, icc=display_p3_profile())
out_rgba = os.path.join(tmp, "srgb-rgba.png")
magick(p3_rgba, "-profile", srgb_icc, out_rgba)
got = pixels(out_rgba, "rgba")
assert [p[3] for p in got] == alphas, got
check("RGBA colors convert", [p[:3] for p in got], expected)

print("ImageMagick ICC profile conversion OK")
