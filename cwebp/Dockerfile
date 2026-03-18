FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    git \
    libpng-dev \
    libpng-static \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    giflib-dev \
    giflib-static \
    tiff-dev \
    zlib-dev \
    zlib-static

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://chromium.googlesource.com/webm/libwebp.git /src/libwebp

WORKDIR /src/libwebp

RUN mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_EXE_LINKER_FLAGS="-static" \
      -DWEBP_BUILD_CWEBP=ON \
      -DWEBP_BUILD_DWEBP=ON \
      -DWEBP_LINK_STATIC=ON \
      -DBUILD_SHARED_LIBS=OFF \
      -DWEBP_BUILD_ANIM_UTILS=OFF \
      -DWEBP_BUILD_GIF2WEBP=OFF \
      -DWEBP_BUILD_IMG2WEBP=OFF \
      -DWEBP_BUILD_VWEBP=OFF \
      -DWEBP_BUILD_WEBPINFO=OFF \
      -DWEBP_BUILD_WEBPMUX=OFF \
      -DWEBP_BUILD_EXTRAS=OFF && \
    make -j$(nproc)

# Verify static
RUN file /src/libwebp/build/cwebp && \
    file /src/libwebp/build/cwebp | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/libwebp/build/cwebp /cwebp
COPY --from=builder /src/libwebp/build/dwebp /dwebp
