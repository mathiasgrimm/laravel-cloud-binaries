FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
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

WORKDIR /src/libavif

# Remove dynamic libs (except libz which cmake needs) to force static linking
RUN rm -f /usr/lib/libaom.so* /usr/lib/libpng*.so* /usr/lib/libjpeg*.so* /usr/lib/libturbojpeg*.so* && \
    mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_EXE_LINKER_FLAGS="-static" \
      -DBUILD_SHARED_LIBS=OFF \
      -DAVIF_CODEC_AOM=SYSTEM \
      -DAVIF_BUILD_APPS=ON \
      -DAVIF_LIBYUV=OFF \
      -DZLIB_LIBRARY=/usr/lib/libz.a \
      -DZLIB_INCLUDE_DIR=/usr/include && \
    make -j$(nproc)

# Verify static
RUN file /src/libavif/build/avifenc && \
    file /src/libavif/build/avifdec && \
    file /src/libavif/build/avifenc | grep -qv "dynamically linked" && \
    echo "Static binaries confirmed"

FROM scratch
COPY --from=builder /src/libavif/build/avifenc /avifenc
COPY --from=builder /src/libavif/build/avifdec /avifdec
