# libavif 1.2.1 grid metadata backport

`grid-metadata.patch` backports the 26-line application fix from
[AOMediaCodec/libavif commit 42d89dc530695ecf8952f1d35a36a5dd7c41a2c0](https://github.com/AOMediaCodec/libavif/commit/42d89dc530695ecf8952f1d35a36a5dd7c41a2c0)
(PR #2940, fixes #2934). `avifImageSetViewRect()` copies pixel views and scalar
properties, but not allocated ICC, XMP or Exif blobs. The encoder takes grid
metadata from its first cell, so splitting a single input discarded those blobs,
including an explicit `--icc` override.

One line uses `avifRWDataSet()` for Exif, as in upstream
[commit d3ec9d45116880609b6c0ff38de61a5ab7274836](https://github.com/AOMediaCodec/libavif/commit/d3ec9d45116880609b6c0ff38de61a5ab7274836).
This copies the blob without recalculating the already copied rotation/mirror
properties. In 1.2.1, calling `avifImageSetMetadataExif()` here would overwrite
explicit `--irot`/`--imir` choices with embedded Exif orientation. The broader
Exif normalization changes from that later commit are deliberately not included.
Libavif's version, CLI, pixel encoding and decoder selection remain unchanged.

`make test-avif` runs both the existing codec/static checks and the generated
metadata regression. The latter independently extracts exact payloads with
ExifTool and checks ordinary encoding, single-input grids, explicit cell grids,
embedded and overridden ICC/Exif, ignore flags, JPEG orientation, CLI transform
precedence, color properties and lossless RGB/RGBA samples. PNG's existing Exif
orientation normalization to 1 is accounted for; JPEG and explicit Exif payloads
are checked unchanged. Pillow generates fixtures and an sRGB profile locally;
no application fixtures or external test downloads are required.

## Artifact build, 2026-09-22

Built with Docker `--platform linux/arm64`, the repository Dockerfile, and args
`VERSION=v1.2.1`, `DAV1D_VERSION=1.5.1`,
`DAV1D_COMMIT=42b2b24fb8819f1ed3643aa9cf2a62f03868e3aa`.

- libavif: `fcb084c9387e367750f5375e462005ce298f57cc` plus this patch
- dav1d: `42b2b24fb8819f1ed3643aa9cf2a62f03868e3aa`
- Alpine 3.23.3, musl 1.2.5-r23
- aom-static 3.14.1-r0, libpng-static 1.6.58-r1
- libjpeg-turbo-static 3.1.2-r0, zlib-static 1.3.2-r0
- `avifenc` SHA-256: `97e87bc41a8f221ba5563bf4f95dcc4968ed17a117f55a7bc10c90035ae42c7c`
- `avifdec` SHA-256: `9b65c24ef3e4dce60519ff97b10c0dc103e56c827dd843a380660ce34fa7802f`

Both outputs are stripped static ARM64 executables without ELF INTERP or
DT_NEEDED. The rebuilt decoder is byte-identical to the existing artifact.
The Alpine base and APK repositories retain the package's existing floating
pins, so future builds are not promised to be byte-for-byte reproducible.
