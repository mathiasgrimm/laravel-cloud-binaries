#!/usr/bin/env python3
"""Run the perceptual quality metrics the way the Glimpse quality reports do.

SSIMULACRA2 and Butteraugli come from libjxl. SSIM and MS-SSIM are libvmaf's
float_ssim and float_ms_ssim on BT.709 luma (yuv444p), through ffmpeg's libvmaf
filter. Images are prepared outside the metric tools: ICC conversion to sRGB,
first frame, 8-bit PNG24, and transparent images flattened on black and white.

Fixtures are generated with integer arithmetic, so their decoded pixels are the
same on every architecture. The JSON lines on stdout are for comparing builds.
Scores are floating point: compare them within a tolerance, not for equality.
"""

import atexit
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icc_profiles import srgb_profile  # noqa: E402
from png_files import color_type, write_png  # noqa: E402

BIN = os.environ.get("BIN_DIR", "/opt/bin")
SIZE = 256  # libvmaf float_ms_ssim needs at least 176 pixels per side
EXACT = 1e-6

tmp = tempfile.mkdtemp(prefix="quality-metrics-")
atexit.register(shutil.rmtree, tmp, ignore_errors=True)
SRGB = os.path.join(tmp, "srgb.icc")
with open(SRGB, "wb") as fh:
    fh.write(srgb_profile())


def tool(name):
    return os.path.join(BIN, name)


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def clamp(value):
    return min(max(value, 0), 255)


def lcg(seed):
    state = seed
    while True:
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        yield state >> 16


def reference_rgb(size):
    """Gradients, a checkerboard, a disc, thin lines and fixed pseudo-random noise."""
    noise = lcg(353)
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            r, g, b = x * 255 // (size - 1), y * 255 // (size - 1), 255 - (x + y) * 255 // (2 * size - 2)
            if size // 8 <= x < size * 7 // 16 and size // 8 <= y < size * 7 // 16 and (x // 8 + y // 8) % 2:
                r, g, b = 240, 240, 240
            if (x - size * 11 // 16) ** 2 + (y - size * 11 // 16) ** 2 < (size * 3 // 16) ** 2:
                r, g, b = 200, 40, 60
            if y % 32 == 0 and x > size // 2:
                r = g = b = 20
            n = next(noise) % 17 - 8
            pixels += bytes(clamp(c + n) for c in (r, g, b))
    return pixels


def radial_alpha(size):
    centre = size // 2
    return bytes(max(0, 255 - 2 * math.isqrt((x - centre) ** 2 + (y - centre) ** 2))
                 for y in range(size) for x in range(size))


def add_noise(pixels, amplitude, seed):
    noise = lcg(seed)
    return bytes(clamp(c + next(noise) % (2 * amplitude + 1) - amplitude) for c in pixels)


def box_blur(pixels, size, radius):
    """Separable box blur of RGB pixels with edge clamping."""
    out = bytearray(pixels)
    for horizontal in (True, False):
        src = bytes(out)
        for y in range(size):
            for x in range(size):
                for c in range(3):
                    total = 0
                    for d in range(-radius, radius + 1):
                        xx, yy = (min(max(x + d, 0), size - 1), y) if horizontal else (x, min(max(y + d, 0), size - 1))
                        total += src[(yy * size + xx) * 3 + c]
                    out[(y * size + x) * 3 + c] = total // (2 * radius + 1)
    return bytes(out)


def posterize(pixels, step):
    return bytes(c // step * step + step // 2 for c in pixels)


def with_alpha(rgb, alpha):
    return bytes(v for i, a in enumerate(alpha) for v in (*rgb[i * 3:i * 3 + 3], a))


def save(name, pixels, size, channels):
    path = os.path.join(tmp, name + ".png")
    write_png(path, size, size, pixels, channels)
    return path


def prepare(src, dest, background):
    flatten = ["-alpha", "off"] if background is None else ["-background", background, "-alpha", "remove", "-alpha", "off"]
    proc = run(tool("magick"), src + "[0]", "-profile", SRGB, *flatten, "-depth", "8", "PNG24:" + dest)
    assert proc.returncode == 0, proc.stderr
    assert color_type(dest) == (8, 2), (dest, color_type(dest))


def butteraugli(ref, dist):
    proc = run(tool("butteraugli_main"), ref, dist, "--pnorm", "3")
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.strip().splitlines()
    assert lines[1].startswith("3-norm:"), proc.stdout
    return {"butteraugli_max": float(lines[0]), "butteraugli_3norm": float(lines[1].split(":")[1])}


def ssimulacra2(ref, dist):
    proc = run(tool("ssimulacra2"), ref, dist)
    assert proc.returncode == 0, proc.stderr
    return {"ssimulacra2": float(proc.stdout.strip().splitlines()[-1])}


def vmaf_metrics(ref, dist):
    log = os.path.join(tmp, "vmaf.json")
    if os.path.exists(log):
        os.unlink(log)
    graph = ("[0:v]scale=out_color_matrix=bt709,format=yuv444p[d];[1:v]scale=out_color_matrix=bt709,format=yuv444p[r];"
             f"[d][r]libvmaf=feature=name=float_ssim|name=float_ms_ssim:log_fmt=json:log_path={log}:n_threads=1")
    proc = run(tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-i", dist, "-i", ref, "-lavfi", graph, "-f", "null", "-")
    assert proc.returncode == 0, proc.stderr
    with open(log) as fh:
        return json.load(fh)["frames"][0]["metrics"], proc.stdout + proc.stderr


def vmaf(ref, dist):
    metrics, _ = vmaf_metrics(ref, dist)
    # The default built-in vmaf_v0.6.1 model runs too; no model file is needed.
    return {"ssim": metrics["float_ssim"], "ms_ssim": metrics["float_ms_ssim"], "vmaf": metrics["vmaf"]}


def measure(ref, dist):
    return {**ssimulacra2(ref, dist), **butteraugli(ref, dist), **vmaf(ref, dist)}


def digest(pixels):
    return hashlib.sha256(pixels).hexdigest()


def report(case, background, ref_pixels, dist_pixels, scores):
    print(json.dumps({"case": case, "background": background, "reference_pixels_sha256": digest(ref_pixels),
                      "distorted_pixels_sha256": digest(dist_pixels), **scores}, sort_keys=True))


for name in ("ssimulacra2", "butteraugli_main"):
    proc = run(tool(name))
    assert proc.returncode != 0 and "Usage:" in proc.stderr, (name, proc.returncode, proc.stderr)
filters = run(tool("ffmpeg"), "-hide_banner", "-filters").stdout
assert any(line.split()[1:2] == ["libvmaf"] for line in filters.splitlines()), "ffmpeg has no libvmaf filter"
for name in ("ssimulacra2", "butteraugli_main", "ffmpeg", "magick"):
    with open(tool(name), "rb") as fh:
        print(json.dumps({"binary": name, "sha256": hashlib.sha256(fh.read()).hexdigest()}))

ref_rgb = reference_rgb(SIZE)
light_rgb = add_noise(ref_rgb, 2, 7)
heavy_rgb = posterize(box_blur(ref_rgb, SIZE, 2), 16)
alpha = radial_alpha(SIZE)

# Opaque fixtures.
results = {}
ref_png = save("reference", ref_rgb, SIZE, 3)
prepared_ref = os.path.join(tmp, "prepared-reference.png")
prepare(ref_png, prepared_ref, None)
for case, pixels in (("identical", ref_rgb), ("light", light_rgb), ("heavy", heavy_rgb)):
    prepared = os.path.join(tmp, f"prepared-{case}.png")
    prepare(save(case, pixels, SIZE, 3), prepared, None)
    results[case] = measure(prepared_ref, prepared)
    report(case, "opaque", ref_rgb, pixels, results[case])

identical = results["identical"]
assert abs(identical["ssimulacra2"] - 100) < EXACT, identical
assert identical["butteraugli_max"] == 0 and identical["butteraugli_3norm"] == 0, identical
assert abs(identical["ssim"] - 1) < EXACT and abs(identical["ms_ssim"] - 1) < EXACT, identical
light, heavy = results["light"], results["heavy"]
assert 100 > light["ssimulacra2"] > heavy["ssimulacra2"], (light, heavy)
assert 0 < light["butteraugli_max"] < heavy["butteraugli_max"], (light, heavy)
assert 0 < light["butteraugli_3norm"] < heavy["butteraugli_3norm"], (light, heavy)
assert 1 > light["ssim"] > heavy["ssim"] > 0, (light, heavy)
assert 1 > light["ms_ssim"] > heavy["ms_ssim"] > 0, (light, heavy)
assert light["vmaf"] > heavy["vmaf"], (light, heavy)

# Transparent fixtures are flattened on black and on white; the worse score counts.
ref_rgba = with_alpha(ref_rgb, alpha)
ref_rgba_png = save("reference-rgba", ref_rgba, SIZE, 4)
worse = {"ssimulacra2": min, "ssim": min, "ms_ssim": min, "vmaf": min, "butteraugli_max": max, "butteraugli_3norm": max}
for case, rgb in (("identical-alpha", ref_rgb), ("heavy-alpha", heavy_rgb)):
    rgba = with_alpha(rgb, alpha)
    dist_png = save(case, rgba, SIZE, 4)
    variants = {}
    for background in ("black", "white"):
        prepared_ref = os.path.join(tmp, f"prepared-reference-{background}.png")
        prepared = os.path.join(tmp, f"prepared-{case}-{background}.png")
        prepare(ref_rgba_png, prepared_ref, background)
        prepare(dist_png, prepared, background)
        variants[background] = measure(prepared_ref, prepared)
        report(case, background, ref_rgba, rgba, variants[background])
    combined = {key: pick(v[key] for v in variants.values()) for key, pick in worse.items()}
    if case == "identical-alpha":
        assert abs(combined["ssimulacra2"] - 100) < EXACT and combined["butteraugli_max"] == 0, combined
        assert abs(combined["ssim"] - 1) < EXACT and abs(combined["ms_ssim"] - 1) < EXACT, combined
    else:
        assert variants["black"] != variants["white"], variants
        assert combined["ssimulacra2"] < 100 and combined["butteraugli_max"] > 0 and combined["ssim"] < 1, combined

# float_ms_ssim needs five scales. Below 176 pixels per side libvmaf skips it and
# prints "scale below 1x1", but ffmpeg still succeeds with float_ssim.
for size, has_ms_ssim in ((175, False), (176, True)):
    small = reference_rgb(size)
    metrics, output = vmaf_metrics(save(f"small-{size}", small, size, 3), save(f"small-{size}-light", add_noise(small, 2, 7), size, 3))
    assert 0 < metrics["float_ssim"] < 1, (size, metrics)
    assert ("float_ms_ssim" in metrics) == has_ms_ssim, (size, metrics)
    assert ("scale below 1x1" in output) != has_ms_ssim, (size, output)

# The libjxl tools also read JPEG directly. The JPEG bytes depend on the encoder
# version, so this case checks decoding only and is not a cross-build fixture.
jpeg = os.path.join(tmp, "reference.jpg")
decoded = os.path.join(tmp, "decoded.png")
assert run(tool("magick"), ref_png, "-quality", "60", "-sampling-factor", "1x1", jpeg).returncode == 0
assert run(tool("magick"), jpeg, "PNG24:" + decoded).returncode == 0
direct, via_png = ssimulacra2(ref_png, jpeg), ssimulacra2(ref_png, decoded)
assert abs(direct["ssimulacra2"] - via_png["ssimulacra2"]) < 1e-3, (direct, via_png)
assert direct["ssimulacra2"] < 100

# PNM input: a lossless copy of the reference is identical.
ppm = os.path.join(tmp, "reference.ppm")
assert run(tool("magick"), ref_png, ppm).returncode == 0
assert abs(ssimulacra2(ref_png, ppm)["ssimulacra2"] - 100) < EXACT
assert butteraugli(ref_png, ppm)["butteraugli_max"] == 0

print("Quality metric tools OK", file=sys.stderr)
