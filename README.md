# Laravel Cloud Binaries

Pre-built, statically compiled binaries for Linux (amd64/musl). Designed to be installed as a Composer package so that `vendor/bin/` contains ready-to-use tools on Laravel Cloud (or any Linux environment).

This package includes all the binaries required by [spatie/image-optimizer](https://github.com/spatie/image-optimizer), making it a drop-in solution for image optimization on environments where system packages are not available. Note that [svgo](https://github.com/svg/svgo) is not included as it is a regular npm package and can be installed via `npm install -g svgo`.

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

All binaries are statically linked against musl libc (Alpine Linux). They will **not** run on macOS — this is expected.

## Pinned versions

All upstream versions are defined at the top of the `Makefile` and passed to each Dockerfile via `--build-arg`. To bump a version, change the single variable in the Makefile.

| Binary | Variable | Current version | Size |
|--------|----------|-----------------|------|
| jpegoptim | `JPEGOPTIM_VERSION` | `v1.5.6` | 1.0 MB |
| optipng | `OPTIPNG_VERSION` | `0.7.8` | 797 KB |
| pngquant | `PNGQUANT_VERSION` | `3.0.3` | 1.3 MB |
| cwebp | `LIBWEBP_VERSION` | `v1.5.0` | 1.6 MB |
| dwebp | `LIBWEBP_VERSION` | `v1.5.0` | 1.3 MB |
| avifenc | `LIBAVIF_VERSION` | `v1.2.1` | 7.8 MB |
| avifdec | `LIBAVIF_VERSION` | `v1.2.1` | 7.7 MB |
| gifsicle | `GIFSICLE_VERSION` | `v1.96` | 1.3 MB |
| ffmpeg | `FFMPEG_VERSION` | `n7.1.1` | 29 MB |
| ffprobe | `FFMPEG_VERSION` | `n7.1.1` | 29 MB |
| magick | `IMAGEMAGICK_VERSION` | `7.1.1-43` | 12 MB |
| **Total** | | | **93 MB** |

## Installation

```bash
composer require mathiasgrimm/laravel-cloud-binaries
```

Composer will symlink all 11 binaries into `vendor/bin/`.

## Selective installation (faster deploys)

If you only need a few binaries, you can install the package as a dev dependency, copy just the ones you need into your repository, and avoid downloading the full ~93 MB on every deploy:

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
vendor/bin/ffprobe -v quiet -print_format json -show_format input.mp4
vendor/bin/magick input.png -resize 50% output.png
```

> **Note:** These are statically compiled Linux (musl) binaries. They will work on Laravel Cloud and other Linux environments but **not** on macOS or Windows.

## Building from source

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- `make`

### Build all binaries

```bash
make
```

Binaries are output to the `bin/` directory.

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
```

### Clean up

```bash
make clean          # remove bin/ contents
make clean-images   # remove Docker images
make clean-all      # both
```

## How it works

Each tool has its own Dockerfile under `<tool>/Dockerfile`. The Dockerfiles use multi-stage Alpine builds:

1. **Builder stage** — installs dependencies, clones source, compiles with static linking flags
2. **Final stage** — `FROM scratch`, copies only the static binary

The Makefile orchestrates building the Docker images and extracting the binaries into `bin/`.

## Project structure

```
.
├── jpegoptim/Dockerfile
├── optipng/Dockerfile
├── pngquant/Dockerfile
├── cwebp/Dockerfile        # builds cwebp + dwebp
├── avifenc/Dockerfile      # builds avifenc + avifdec
├── gifsicle/Dockerfile
├── ffmpeg/Dockerfile       # builds ffmpeg + ffprobe
├── imagemagick/Dockerfile  # builds magick
├── bin/                    # build output (committed)
├── Makefile
├── composer.json
└── README.md
```
