# Laravel Cloud Binaries

Pre-built, statically compiled binaries for Linux (amd64/musl). Designed to be installed as a Composer package so that `vendor/bin/` contains ready-to-use tools on Laravel Cloud (or any Linux environment).

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
| **Total** | | | **22.7 MB** |

## Installation

```bash
composer require mathiasgrimm/laravel-cloud-binaries
```

Composer will symlink all 8 binaries into `vendor/bin/`.

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
```

### Parallel builds

```bash
make -j4
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
├── bin/                    # build output (committed)
├── Makefile
├── composer.json
└── README.md
```
