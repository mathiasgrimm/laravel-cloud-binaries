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

# Build Little CMS from source (static) at a verified commit, so ICC profile
# conversions (-profile) change pixels instead of only attaching the profile.
ARG LCMS2_VERSION
ARG LCMS2_COMMIT
RUN git clone --depth 1 --branch ${LCMS2_VERSION} https://github.com/mm2/Little-CMS.git /src/lcms2 && \
    test "$(git -C /src/lcms2 rev-parse HEAD)" = "${LCMS2_COMMIT}" && \
    cd /src/lcms2 && \
    ./configure --disable-shared --enable-static --prefix=/usr/local && \
    make -j$(nproc) && make install

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
      --with-lcms \
      --without-x \
      --without-perl \
      --without-openexr \
      --without-heic \
      --without-jxl \
      --without-raw \
      --without-openjp2 \
      CFLAGS="-Os" CXXFLAGS="-Os" && \
    make -j$(nproc) LDFLAGS="-all-static" LIBS="-lsharpyuv -lbrotlidec -lbrotlicommon"

# Fail the build if the LCMS delegate was not picked up.
RUN ./utilities/magick -version | grep -Eq '^Delegates.* lcms( |$)'

# Emit dependency provenance into the build log for artifact updates.
RUN cat /etc/alpine-release && \
    apk list --installed libjpeg-turbo-static libpng-static libwebp-static freetype-static libxml2-static xz-static bzip2-static brotli-static zlib-static musl && \
    git -C /src/lcms2 rev-parse HEAD && git -C /src/libtiff rev-parse HEAD

# Strip symbol tables -- these are shipped artifacts, not debugging targets
RUN strip /src/imagemagick/utilities/magick

# Verify static
RUN file /src/imagemagick/utilities/magick && \
    file /src/imagemagick/utilities/magick | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/imagemagick/utilities/magick /magick
