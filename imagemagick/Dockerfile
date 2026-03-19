FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    pkgconf \
    git \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    libpng-dev \
    libpng-static \
    libwebp-dev \
    libwebp-static \
    freetype-dev \
    freetype-static \
    zlib-dev \
    zlib-static \
    libxml2-dev \
    libxml2-static \
    xz-dev \
    xz-static \
    bzip2-dev \
    bzip2-static \
    brotli-dev \
    brotli-static

# Build libtiff from source (static) — Alpine package lacks tiff-static
RUN git clone --depth 1 --branch v4.7.0 https://gitlab.com/libtiff/libtiff.git /src/libtiff && \
    cd /src/libtiff && \
    cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -Dtiff-tools=OFF \
      -Dtiff-tests=OFF \
      -Dtiff-contrib=OFF \
      -Dtiff-docs=OFF && \
    cmake --build build -j$(nproc) && \
    cmake --install build

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/ImageMagick/ImageMagick.git /src/imagemagick

WORKDIR /src/imagemagick

RUN ./configure \
      --disable-shared \
      --enable-static \
      --with-jpeg \
      --with-png \
      --with-webp \
      --with-freetype \
      --with-tiff \
      --with-xml \
      --with-zlib \
      --without-x \
      --without-perl \
      --without-openexr \
      --without-heic \
      --without-jxl \
      --without-raw \
      --without-openjp2 \
      CFLAGS="-Os" CXXFLAGS="-Os" && \
    make -j$(nproc) LDFLAGS="-all-static" LIBS="-lsharpyuv -lbrotlidec -lbrotlicommon"

# Verify static
RUN file /src/imagemagick/utilities/magick && \
    file /src/imagemagick/utilities/magick | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/imagemagick/utilities/magick /magick
