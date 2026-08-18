# Third-party notices

This package distributes pre-compiled binaries built from third-party open source
projects. The MIT license in [`LICENSE`](LICENSE) covers **only this repository's own
build scripts** (the Makefile and the Dockerfiles). It does **not** cover the binaries
in `bin/` — each of those is governed by its upstream project's license, listed below.

**Several of the binaries are copyleft (GPL).** If you redistribute this package, or
redistribute an application that bundles these binaries, those licenses impose
obligations on you — most notably passing along the license text and making the
corresponding source available. See [Source code](#source-code) below.

## Binaries

| Binary | Upstream project | Version | License | Full text |
|--------|------------------|---------|---------|-----------|
| `jpegoptim` | [tjko/jpegoptim](https://github.com/tjko/jpegoptim) | `v1.5.6` | `GPL-3.0-or-later` | [GPL-3.0.txt](licenses/GPL-3.0.txt) |
| `optipng` | [OptiPNG](https://optipng.sourceforge.net/) | `0.7.8` | `Zlib` | [optipng.txt](licenses/optipng.txt) |
| `pngquant` | [kornelski/pngquant](https://github.com/kornelski/pngquant) | `3.0.3` | `GPL-3.0-or-later` | [pngquant.txt](licenses/pngquant.txt) |
| `cwebp`, `dwebp` | [libwebp](https://chromium.googlesource.com/webm/libwebp) | `v1.5.0` | `BSD-3-Clause` | [libwebp.txt](licenses/libwebp.txt) |
| `avifenc`, `avifdec` | [AOMediaCodec/libavif](https://github.com/AOMediaCodec/libavif) | `v1.2.1` | `BSD-2-Clause` | [libavif.txt](licenses/libavif.txt) |
| `gifsicle` | [kohler/gifsicle](https://github.com/kohler/gifsicle) | `v1.96` | `GPL-2.0-only` | [GPL-2.0.txt](licenses/GPL-2.0.txt) |
| `ffmpeg`, `ffprobe` | [FFmpeg](https://github.com/FFmpeg/FFmpeg) | `n7.1.1` | `GPL-2.0-or-later` | [GPL-2.0.txt](licenses/GPL-2.0.txt) |
| `magick` | [ImageMagick](https://github.com/ImageMagick/ImageMagick) | `7.1.1-43` | `ImageMagick` | [imagemagick.txt](licenses/imagemagick.txt) |
| `zstd` | [facebook/zstd](https://github.com/facebook/zstd) | `v1.5.7` | `BSD-3-Clause` | [zstd.txt](licenses/zstd.txt) |
| `vips`, `vipsthumbnail` | [libvips](https://github.com/libvips/libvips) | `v8.18.5` | `LGPL-2.1-or-later` | [LGPL-2.1.txt](licenses/LGPL-2.1.txt) |

### Why ffmpeg and ffprobe are GPL, not LGPL

FFmpeg is LGPL-2.1-or-later by default. This package builds it with `--enable-gpl`
plus `--enable-libx264` and `--enable-libx265`. Per FFmpeg's own
[`LICENSE.md`](https://github.com/FFmpeg/FFmpeg/blob/n7.1.1/LICENSE.md):

> Some optional parts of FFmpeg are licensed under the GNU General Public License
> version 2 or later (GPL v2+). […] None of these parts are used by default, you have
> to explicitly pass `--enable-gpl` to configure to activate them. In this case,
> FFmpeg's license changes to GPL v2+.

Additionally, x264 is `GPL-2.0-or-later` and x265 is `GPL-2.0`. Because x265 does not
offer the "or later" option, the practical effect for the combined `ffmpeg` and
`ffprobe` binaries shipped here is GPL-2.0. Commercial licenses for x264 and x265 are
available from their respective vendors if you need to avoid the GPL.

### Why vips and vipsthumbnail are LGPL, not GPL

libvips is `LGPL-2.1-or-later`. This package builds it **without** FFTW, which is
`GPL-2.0-or-later` and would have upgraded the binaries to GPL. Every other component
linked into them is LGPL-2.1 or permissive, so the `vips` and `vipsthumbnail` binaries
stay `LGPL-2.1-or-later`.

Note that these are statically linked. Section 6 of the LGPL sets out what you must
provide when you distribute a work linked against an LGPL library; the pinned upstream
version, the build scripts in this repository, and the written offer below are intended
to cover it. If you are combining these binaries into a larger product, read that
section rather than relying on this summary.

## Statically linked components

All binaries are statically linked, so each one also contains code from its
dependencies. The notable ones, by binary:

| Binary | Statically linked components |
|--------|------------------------------|
| `jpegoptim` | libjpeg-turbo (`IJG AND BSD-3-Clause AND Zlib`) |
| `optipng` | libpng (`Libpng`), zlib (`Zlib`) |
| `pngquant` | libpng, zlib, Little CMS (`MIT`) |
| `cwebp`, `dwebp` | libpng, libjpeg-turbo, giflib (`MIT`), libtiff (`libtiff`), zlib |
| `avifenc`, `avifdec` | libaom (`BSD-2-Clause` + AOM patent license), libpng, libjpeg-turbo, zlib |
| `gifsicle` | — |
| `ffmpeg`, `ffprobe` | x264 (`GPL-2.0-or-later`), x265 `4.1` (`GPL-2.0`), libvpx `v1.15.0` (`BSD-3-Clause`), Opus `v1.5.2` (`BSD-3-Clause`), LAME (`LGPL-2.1-or-later`), FreeType (`FTL OR GPL-2.0-or-later`), libpng, zlib, bzip2 (`bzip2-1.0.6`), Brotli (`MIT`) |
| `magick` | libjpeg-turbo, libpng, libwebp, FreeType, libxml2 (`MIT`), libtiff `v4.7.0`, zlib, xz/liblzma (`0BSD`), bzip2, Brotli |
| `zstd` | zlib, xz/liblzma, LZ4 (`BSD-2-Clause`) |
| `vips`, `vipsthumbnail` | GLib (`LGPL-2.1-or-later`), libexif `v0.6.26` (`LGPL-2.1-or-later`), Highway `1.3.0` (`Apache-2.0`), libtiff `v4.7.0` (`libtiff`), libeconf `v0.8.4` (`MIT`), libjpeg-turbo, libpng, libspng (`BSD-2-Clause`), libwebp, Little CMS, Orc (`BSD-2-Clause AND BSD-3-Clause`), PCRE2 (`BSD-3-Clause`), libffi (`MIT`), gettext/libintl (`LGPL-2.1-or-later`), util-linux libmount and libblkid (`LGPL-2.1-or-later`), zlib, bzip2, xz/liblzma, Brotli, Zstandard |

Unversioned components above are the Alpine Linux packages current at build time; the
`alpine:latest` base image and its `apk` packages are not pinned, so exact versions
vary by build date. Only the primary upstream tool versions are pinned, in the
`Makefile`.

## Source code

The complete corresponding source for every binary is the upstream project at the
version pinned in the table above, combined with the build scripts in this repository
(`Makefile` and `<tool>/Dockerfile`), which are included in the distributed package.
Each Dockerfile clones its upstream source at an exact tag and records the full
configure and build flags used.

**Written offer.** For a period of three years from the date you received this
package, the copyright holder of this repository will, on request, provide a complete
machine-readable copy of the corresponding source code for the copyleft binaries it
distributes (`jpegoptim`, `pngquant`, `gifsicle`, `ffmpeg`, `ffprobe`, `vips`,
`vipsthumbnail`), on a medium
customarily used for software interchange, for no more than the cost of physically
performing the distribution. Send requests to <mathiasgrimm@gmail.com>, naming the
package version you received.

## Disclaimer

This summary is provided in good faith and is not legal advice. It reflects the
licenses of the pinned upstream versions at the time of writing. If you redistribute
these binaries — particularly in a commercial product — review the obligations
yourself, and re-check this file after any version bump in the `Makefile`.
