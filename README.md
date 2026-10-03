<p align="center">
    <img src="https://raw.githubusercontent.com/mathiasgrimm/laravel-cloud-binaries/main/art/banner.avif" alt="Laravel Cloud Binaries" width="100%">
</p>

# Laravel Cloud Binaries

> Pre-built static binaries for Laravel Cloud. Ready in `vendor/bin`, no system packages required.

<p align="left">
    <a href="https://packagist.org/packages/mathiasgrimm/laravel-cloud-binaries"><img src="https://img.shields.io/packagist/v/mathiasgrimm/laravel-cloud-binaries.svg?style=flat-square" alt="Latest Version on Packagist"></a>
    <a href="https://github.com/mathiasgrimm/laravel-cloud-binaries/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/mathiasgrimm/laravel-cloud-binaries/test.yml?branch=main&label=tests&style=flat-square" alt="Tests"></a>
    <a href="https://packagist.org/packages/mathiasgrimm/laravel-cloud-binaries"><img src="https://img.shields.io/packagist/dt/mathiasgrimm/laravel-cloud-binaries.svg?style=flat-square" alt="Total Downloads"></a>
    <a href="THIRD-PARTY-NOTICES.md"><img src="https://img.shields.io/badge/license-MIT%20%2B%20GPL%20%2B%20others-blue.svg?style=flat-square" alt="License"></a>
</p>

> [!NOTE]
> This is an independent, community package. It is not an official or
> first-party Laravel package, and is not affiliated with, endorsed by, or
> sponsored by Laravel or Laravel Cloud. "Laravel" is a trademark of its
> respective owner.

Pre-built, statically compiled binaries for Linux (arm64/musl). Designed to be installed as a Composer package so that `vendor/bin/` contains ready-to-use tools on Laravel Cloud (or any Linux arm64 environment).

This package includes all the binaries required by [spatie/image-optimizer](https://github.com/spatie/image-optimizer), making it a drop-in solution for image optimization on environments where system packages are not available. Note that [svgo](https://github.com/svg/svgo) is not included as it is a regular npm package and can be installed via `npm install -g svgo`.

Beyond image optimization, it also ships `ffmpeg`/`ffprobe` for media, `zstd` for compression, `qpdf` for PDF manipulation, and `ssimulacra2`/`butteraugli_main` for perceptual image quality metrics.

## Binaries included

| Binary | Purpose |
|--------|---------|
| `jpegoptim` | JPEG optimization |
| `optipng` | PNG optimization |
| `pngquant` | PNG lossy compression |
| `cwebp` | WebP encoding |
| `dwebp` | WebP decoding |
| `avifenc` | AVIF encoding |
| `avifdec` | AVIF decoding |
| `gifsicle` | GIF optimization |
| `ffmpeg` | Audio/video transcoding |
| `ffprobe` | Media stream analysis |
| `magick` | ImageMagick 7 (replaces convert/identify/mogrify) |
| `zstd` | Zstandard compression/decompression |
| `qpdf` | PDF transformation (merge, split, encrypt, linearize) |
| `ssimulacra2` | SSIMULACRA 2 perceptual image quality score |
| `butteraugli_main` | Butteraugli perceptual image distance |

All binaries are statically linked against musl libc (Alpine Linux) and built for **arm64** (aarch64). They will **not** run on macOS, nor on x86-64 (amd64) Linux hosts — this is expected.

## Pinned versions

Primary upstream versions are defined at the top of the `Makefile` and passed to each Dockerfile via `--build-arg`. To bump a version, change its variable in the Makefile. The dav1d, libjxl, libvmaf and Little CMS sources also have verified commit pins.

| Binary | Variable | Current version | Size |
|--------|----------|-----------------|------|
| jpegoptim | `JPEGOPTIM_VERSION` | `v1.5.6` | 642 KB |
| optipng | `OPTIPNG_VERSION` | `0.7.8` | 386 KB |
| pngquant | `PNGQUANT_VERSION` | `3.0.3` | 1.1 MB |
| cwebp | `LIBWEBP_VERSION` | `v1.5.0` | 1.1 MB |
| dwebp | `LIBWEBP_VERSION` | `v1.5.0` | 834 KB |
| avifenc | `LIBAVIF_VERSION` | `v1.2.1` | 7.6 MB |
| avifdec | `LIBAVIF_VERSION` | `v1.2.1` | 7.6 MB |
| gifsicle | `GIFSICLE_VERSION` | `v1.96` | 323 KB |
| ffmpeg | `FFMPEG_VERSION` | `n7.1.1` | 32 MB |
| ffprobe | `FFMPEG_VERSION` | `n7.1.1` | 32 MB |
| magick | `IMAGEMAGICK_VERSION` | `7.1.1-43` | 8.1 MB |
| zstd | `ZSTD_VERSION` | `v1.5.7` | 1.5 MB |
| qpdf | `QPDF_VERSION` | `v12.4.0` | 3.3 MB |
| ssimulacra2 | `LIBJXL_VERSION` | `v0.12.0` | 3.3 MB |
| butteraugli_main | `LIBJXL_VERSION` | `v0.12.0` | 4.1 MB |
| **Total** | | | **103 MB** |

### AVIF decoder

`avifdec input.avif output.png` uses statically linked dav1d 1.5.1 by default.
`avifenc` continues to use AOM, and `avifdec --codec aom` retains the explicit
AOM decoder fallback. Executable paths and CLI options are unchanged. Portable
applications can omit `--codec`, including on hosts with AOM-only libavif tools.

The purpose is lower decoding memory use, not a speed guarantee. Both AVIF
binaries remain libavif v1.2.1 and require no shared codec libraries. See
[AVIF build provenance](avifenc/BUILD.md) for dependency versions, upstream
selection logic, artifact hashes and the approximately 1.8 MiB combined size increase.

### Quality metrics and ICC profiles

`ssimulacra2` and `butteraugli_main` are built from the same libjxl v0.12.0
source. They read PNG, JPEG and PNM files. GIF and OpenEXR input are not
enabled. Both tools compare color images, so flatten transparent
images on a background first, for example on black and on white:

```bash
vendor/bin/magick original.png -background white -alpha remove -alpha off PNG24:original-white.png
```

`ffmpeg` includes libvmaf v3.2.1 with its floating-point features, so you can
compute `float_ssim` and `float_ms_ssim`. The default VMAF models are built into
the binary, so no model files are needed. `float_ms_ssim` needs an image of at
least 176 pixels on each side.

`magick` includes Little CMS 2.19.1. `-profile` converts the pixels when the
image has an embedded ICC profile, or when you give the source profile first.
Without a source profile, `-profile` only attaches the profile. This changes only
the `magick` command line tool. The PHP Imagick extension uses the ImageMagick
library it was built with.

## Installation

```bash
composer require mathiasgrimm/laravel-cloud-binaries
```

Composer will symlink all 15 binaries into `vendor/bin/`.

## Selective installation (faster deploys)

If you only need a few binaries, you can install the package as a dev dependency, copy just the ones you need into your repository, and avoid downloading the full ~103 MB on every deploy:

```bash
composer require --dev mathiasgrimm/laravel-cloud-binaries

# Copy only the binaries you need into your project
mkdir -p bin
cp vendor/bin/jpegoptim bin/
cp vendor/bin/optipng bin/
cp vendor/bin/pngquant bin/

# Commit them
git add bin/
git commit -m "Add image optimization binaries"
```

Then reference them from your application using `base_path('bin/jpegoptim')` (or whichever path you chose). Since the binaries are committed to your repository, they are available immediately during deployment with no Composer overhead.

To keep your committed binaries in sync automatically when the package is updated, add a `post-update-cmd` script to your `composer.json`:

```json
{
    "scripts": {
        "post-update-cmd": [
            "@php -r \"@mkdir('bin', 0755, true);\"",
            "@php -r \"copy('vendor/mathiasgrimm/laravel-cloud-binaries/bin/jpegoptim', 'bin/jpegoptim');\"",
            "@php -r \"copy('vendor/mathiasgrimm/laravel-cloud-binaries/bin/optipng', 'bin/optipng');\"",
            "@php -r \"copy('vendor/mathiasgrimm/laravel-cloud-binaries/bin/pngquant', 'bin/pngquant');\""
        ]
    }
}
```

After every `composer update`, the selected binaries are copied into `bin/` automatically. Adjust the list to include only the binaries you need. The `@php -r` syntax ensures the commands work on all platforms (Linux, macOS, and Windows).

## Prefer not to ship binaries at all?

This package runs optimization on your own infrastructure, which is the right
trade-off when you want no external dependency and no per-image cost.

If you would rather not ship ~103 MB of executables, [Glimpse](https://glimpseimg.com)
does the same kind of work — optimize, convert, resize, thumbnail — over an HTTP
API, with a CLI and a PHP SDK and nothing to compile:

```bash
composer require mathiasgrimm/glimpse-cli

glimpse optimize public/images/hero.png --in-place
glimpse convert public/images/hero.png --format=avif --optimize -i
```

The trade-off is the obvious one: images are processed by a third-party service
rather than locally, so it needs network access, and anything beyond the
`analyze`/`check` endpoints requires an API token. Pick whichever fits — locally
executed binaries, or a managed API.

This repository uses Glimpse itself, in CI, to keep its own banner optimized.

## Usage

After installation, the binaries are available in `vendor/bin/`:

```bash
vendor/bin/jpegoptim --strip-all image.jpg
vendor/bin/optipng -o2 image.png
vendor/bin/pngquant --quality=65-80 image.png
vendor/bin/cwebp -q 80 image.png -o image.webp
vendor/bin/dwebp image.webp -o image.png
vendor/bin/avifenc image.png image.avif
vendor/bin/avifdec image.avif image.png
vendor/bin/gifsicle -O3 animation.gif -o optimized.gif
vendor/bin/ffmpeg -i input.mp4 -c:v libx264 output.mp4
vendor/bin/ffmpeg -i input.png -frames:v 1 -c:v libwebp output.webp
vendor/bin/ffprobe -v quiet -print_format json -show_format input.mp4
vendor/bin/magick input.png -resize 50% output.png
vendor/bin/zstd -19 backup.sql -o backup.sql.zst
vendor/bin/zstd -d backup.sql.zst
vendor/bin/qpdf --linearize input.pdf output.pdf
vendor/bin/qpdf --empty --pages a.pdf b.pdf -- merged.pdf
vendor/bin/magick input.png -profile sRGB.icc output.png
vendor/bin/ssimulacra2 original.png distorted.png
vendor/bin/butteraugli_main original.png distorted.png --pnorm 3
vendor/bin/ffmpeg -i distorted.png -i original.png -lavfi "[0:v]scale=out_color_matrix=bt709,format=yuv444p[d];[1:v]scale=out_color_matrix=bt709,format=yuv444p[r];[d][r]libvmaf=feature=name=float_ssim|name=float_ms_ssim:log_fmt=json:log_path=vmaf.json" -f null -
```

> **Note:** These are statically compiled Linux arm64 (musl) binaries. They will work on Laravel Cloud and other Linux arm64 environments but **not** on macOS, Windows, or x86-64 Linux.

## Building from source

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- `make`

### Build all binaries

```bash
make
```

Binaries are output to the `bin/` directory.

The AVIF and libjxl Makefile targets explicitly build for `linux/arm64` and check the ELF machine type of both binaries. Other Dockerfiles build for the host architecture, so run the build on an arm64 machine (Apple Silicon, or any aarch64 Linux host) to match the architecture of the committed binaries. Builds are not byte-for-byte reproducible; the Dockerfiles track `alpine:latest` and unpinned apk packages, so builds are not fully pinned. AVIF additionally pins the dav1d source version and commit, and the libjxl, libvmaf and Little CMS sources are pinned to verified commits. For tools without an ARM64 build check, select a different architecture with Docker's `--platform` option, for example `docker build --platform linux/amd64 ...`. Emulated builds are considerably slower.

### Build a single binary

```bash
make bin/jpegoptim
make bin/optipng
make bin/pngquant
make bin/cwebp
make bin/dwebp
make bin/avifenc
make bin/avifdec
make bin/gifsicle
make bin/ffmpeg
make bin/ffprobe
make bin/magick
make bin/zstd
make bin/qpdf
make bin/ssimulacra2
make bin/butteraugli_main
```

### Parallel builds

```bash
make -j4
```

### Testing

Verify that all binaries work correctly by running them inside an Alpine Docker container:

```bash
make test          # build (if needed) + test
make test-only     # test without rebuilding
make test-avif     # focused AVIF regression checks
make test-icc      # ImageMagick ICC profile conversion checks
make test-metrics  # quality metric checks
```

The AVIF tests verify both committed binaries are stripped static ARM64 ELF files
without a dynamic interpreter or shared dependencies. Generated fixtures cover
8/10/12-bit, RGB/alpha, 4:2:0/4:4:4 and 2x2 grids. They assert dav1d is selected
when `--codec` is omitted, compare every decoded RGBA sample against explicit
dav1d and AOM, and check default/explicit AOM encoding and a lossless RGBA round trip.

The other tests encode and decode a real WebP image, then generate a three-frame APNG
and run ImageMagick 7.1.2-31's ffmpeg delegate command with WebP intermediates.
They also exercise the bundled ImageMagick's APNG delegate and check PAM
intermediates for older ImageMagick delegates. FFmpeg links
libwebp statically; the separate `cwebp` and `dwebp` executables are not needed
for its WebP encoder. No `video:intermediate-format=pam` override is required
for decoding. ImageMagick 7.1.2-31's default WebP intermediate is lossy; use
`-define video:intermediate-format=pam` when you need pixel-exact frames.

The metric tests check that `ssimulacra2`, `butteraugli_main`, `ffmpeg`, `ffprobe`
and `magick` are stripped static ARM64 files. They generate identical, lightly
distorted and heavily distorted images, plus transparent images flattened on black
and on white. Then they run SSIMULACRA 2, Butteraugli with `--pnorm 3`, and the
libvmaf `float_ssim` and `float_ms_ssim` features on BT.709 `yuv444p`. Identical
images must get perfect scores, and stronger distortion must get worse scores.
The fixtures are generated with integer arithmetic, so they decode to the same
pixels on every architecture. The scores are printed as JSON lines. Compare scores
from different builds within a tolerance, because they are floating point values.

The ICC test converts saturated Display P3 colors to sRGB with generated ICC
profiles and compares every pixel with the expected value. It also checks that an
image without a profile is not changed, and that alpha is kept.

To rebuild both ffmpeg artifacts after changing their build configuration:

```bash
make -B bin/ffmpeg
make test-only
```

The ffmpeg build extracts both `bin/ffmpeg` and `bin/ffprobe` and uses the same
`LIBWEBP_VERSION` pin as the standalone WebP tools.

### Clean up

```bash
make clean          # remove bin/ contents
make clean-images   # remove Docker images
make clean-all      # both
```

## Licensing

The MIT license in `LICENSE` covers only this repository's build scripts and
documentation. The binaries in `bin/` are built from third-party projects and keep
their own licenses — **`jpegoptim`, `pngquant`, `gifsicle`, `ffmpeg`, and `ffprobe` are
GPL**. `ffmpeg`/`ffprobe` are built with `--enable-gpl`, `--enable-libx264`, and
`--enable-libx265`, which per FFmpeg's own `LICENSE.md` changes its license from
LGPL-2.1+ to GPL-2.0+.

`qpdf` is Apache-2.0. It carries an upstream `NOTICE` file, reproduced in
[`licenses/qpdf-NOTICE.txt`](licenses/qpdf-NOTICE.txt), which redistributors must pass
along. It also contains code derived from the RSA Data Security, Inc. MD5 Message-Digest
Algorithm, whose license requires exactly that identification wherever the derived work is
referenced — see [`licenses/RSA-MD.txt`](licenses/RSA-MD.txt).

`ssimulacra2` and `butteraugli_main` are BSD-3-Clause (libjxl). libjxl also has a
separate patent grant, reproduced in [`licenses/libjxl-PATENTS.txt`](licenses/libjxl-PATENTS.txt).
The libvmaf code in `ffmpeg` is BSD-2-Clause-Patent, and the Little CMS code in
`magick` is MIT. Neither changes the license of those binaries.

If you are only *using* these binaries in your own application, the GPL imposes no
obligations on you — running a program is not distribution. If you **redistribute**
them, whether directly or bundled into a product you ship, read
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) first. It lists the license for
every binary and its statically linked components, and includes the
corresponding-source offer.

Full license texts are in [`licenses/`](licenses/).

## How it works

Each tool has its own Dockerfile under `<tool>/Dockerfile`. The Dockerfiles use multi-stage Alpine builds:

1. **Builder stage** — installs dependencies, clones source, compiles with static linking flags, then strips symbol tables (these are shipped artifacts, not debugging targets)
2. **Final stage** — `FROM scratch`, copies only the static binary

The Makefile orchestrates building the Docker images and extracting the binaries into `bin/`.
