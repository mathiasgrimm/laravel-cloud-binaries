# AVIF build provenance

The AVIF pair uses libavif v1.2.1 and static musl dependencies. dav1d is the
preferred decoder; AOM remains both the encoder and an explicit decoder fallback.
No libavif source or CLI patches are applied.

## Sources and selection

- libavif `v1.2.1`, commit `fcb084c9387e367750f5375e462005ce298f57cc`,
  [upstream](https://github.com/AOMediaCodec/libavif/tree/v1.2.1).
- dav1d `1.5.1`, commit `42b2b24fb8819f1ed3643aa9cf2a62f03868e3aa`,
  [VideoLAN source](https://code.videolan.org/videolan/dav1d/-/tree/1.5.1).
  The Dockerfile checks the tag resolves to this commit before building.
  This is libavif v1.2.1's own tested dependency version, not a latest-version claim.
  Its BSD-2-Clause [COPYING text](../licenses/dav1d.txt) is included verbatim.
- [`LocalDav1d.cmake`](https://github.com/AOMediaCodec/libavif/blob/v1.2.1/cmake/Modules/LocalDav1d.cmake)
  builds the supplied source with Meson `--default-library=static`, assembly enabled,
  and tools, examples and tests disabled. `AVIF_CODEC_DAV1D=LOCAL` imports that archive.
- [`src/avif.c`](https://github.com/AOMediaCodec/libavif/blob/v1.2.1/src/avif.c#L1162)
  orders AUTO codecs by preference, with dav1d before AOM. dav1d has decoding
  capability only; AOM has encoding and decoding capabilities. The CLI's default
  AUTO choice therefore selects dav1d for decoding and AOM for encoding.

## Recorded artifact build, 2026-09-22

`make -B bin/avifenc` builds and extracts **both** binaries on `linux/arm64`.
The builder and `make test-avif` verify AArch64, static linkage, no ELF interpreter
and no `DT_NEEDED` entries. The artifacts are stripped static PIE executables.
They need neither an installed musl loader nor shared codec libraries.

| Dependency | Recorded version |
|------------|------------------|
| Alpine | 3.23.3 |
| musl | 1.2.5-r23 |
| aom-static | 3.14.1-r0 |
| libpng-static | 1.6.58-r1 |
| libjpeg-turbo-static | 3.1.2-r0 |
| zlib-static | 1.3.2-r0 |

The local Alpine image resolved to
`alpine@sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659`.
The build still uses `alpine:latest` and unpinned APK dependencies, so these are
recorded provenance, not a promise of byte-for-byte reproducibility. In particular,
AOM changed from the prior artifacts' 3.13.1 to 3.14.1 during this rebuild.
Both default and explicit AOM encoding are covered by the focused regression suite.

| Artifact | Previous bytes | Current bytes | SHA-256 |
|----------|---------------:|--------------:|---------|
| `bin/avifenc` | 7,091,328 | 8,008,880 | `00837998e067671aae0b823d6e2f29dec45904bc491d8f5998218d921bcf3f2b` |
| `bin/avifdec` | 7,025,792 | 8,008,880 | `9b65c24ef3e4dce60519ff97b10c0dc103e56c827dd843a380660ce34fa7802f` |

The combined increase is 1,900,640 bytes (about 1.81 MiB). This includes all
rebuild dependency changes, not just dav1d. The intended benefit is reduced
AVIF decoding memory; no speed improvement is promised.

## Focused validation

Run `make test-avif` against the checked-in artifacts. This is also part of
`make test-only` and the existing ARM64 CI job. The 24 generated cases combine
8/10/12-bit depth, 4:2:0/4:4:4 chroma, RGB/alpha and still/2x2-grid images.
Each confirms default AOM encoding, default dav1d decoding, explicit dav1d and
AOM decoding, image dimensions, retained alpha, and identical full 16-bit RGBA
samples across decoders. An explicit AOM lossless case also compares decoded
8-bit RGBA samples to the input. These are small correctness fixtures, not
memory or performance benchmarks.
