FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    meson \
    ninja \
    file \
    git \
    aom-dev \
    aom-static \
    libpng-dev \
    libpng-static \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    zlib-dev \
    zlib-static

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/AOMediaCodec/libavif.git /src/libavif

# Match libavif v1.2.1's tested dav1d pin and verify the tag's commit.
# AVIF_CODEC_DAV1D=LOCAL builds this source as a static archive via Meson.
ARG DAV1D_VERSION
ARG DAV1D_COMMIT
RUN git clone --depth 1 --branch ${DAV1D_VERSION} https://code.videolan.org/videolan/dav1d.git /src/libavif/ext/dav1d && \
    test "$(git -C /src/libavif/ext/dav1d rev-parse HEAD)" = "${DAV1D_COMMIT}"

WORKDIR /src/libavif

COPY patches/grid-metadata.patch /tmp/grid-metadata.patch
RUN git apply --check /tmp/grid-metadata.patch && git apply /tmp/grid-metadata.patch

# Remove dynamic libs (except libz which cmake needs) to force static linking
RUN rm -f /usr/lib/libaom.so* /usr/lib/libpng*.so* /usr/lib/libjpeg*.so* /usr/lib/libturbojpeg*.so* && \
    mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_EXE_LINKER_FLAGS="-static" \
      -DBUILD_SHARED_LIBS=OFF \
      -DAVIF_CODEC_AOM=SYSTEM \
      -DAVIF_CODEC_DAV1D=LOCAL \
      -DAVIF_BUILD_APPS=ON \
      -DAVIF_LIBYUV=OFF \
      -DZLIB_LIBRARY=/usr/lib/libz.a \
      -DZLIB_INCLUDE_DIR=/usr/include && \
    make -j$(nproc)

# Emit dependency provenance into the build log for artifact updates.
RUN cat /etc/alpine-release && \
    apk list --installed aom-static libpng-static libjpeg-turbo-static zlib-static musl && \
    git rev-parse HEAD && git -C ext/dav1d rev-parse HEAD

# Strip symbol tables -- these are shipped artifacts, not debugging targets
RUN strip /src/libavif/build/avifenc /src/libavif/build/avifdec

# Both shipped artifacts must be static and have no ELF interpreter or dependencies.
RUN for binary in /src/libavif/build/avifenc /src/libavif/build/avifdec; do \
      file "$binary" && \
      file "$binary" | grep -Eq 'statically linked|static-pie linked' && \
      readelf -h "$binary" | grep -q 'Machine:.*AArch64' && \
      ! readelf -l "$binary" | grep -q INTERP && \
      ! readelf -d "$binary" | grep -q NEEDED || exit 1; \
    done

FROM scratch
COPY --from=builder /src/libavif/build/avifenc /avifenc
COPY --from=builder /src/libavif/build/avifdec /avifdec
