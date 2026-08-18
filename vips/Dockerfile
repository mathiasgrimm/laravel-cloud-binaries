FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    meson \
    ninja \
    cmake \
    pkgconf \
    git \
    glib-dev \
    glib-static \
    libffi-dev \
    pcre2-dev \
    pcre2-static \
    gettext-dev \
    gettext-static \
    util-linux-dev \
    util-linux-static \
    expat-dev \
    expat-static \
    zlib-dev \
    zlib-static \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    libpng-dev \
    libpng-static \
    libwebp-dev \
    libwebp-static \
    lcms2-dev \
    lcms2-static \
    libexif-dev \
    libspng-dev \
    highway-dev \
    orc-dev \
    brotli-dev \
    brotli-static \
    bzip2-dev \
    bzip2-static \
    xz-dev \
    xz-static \
    zstd-dev \
    zstd-static \
    autoconf \
    automake \
    libtool \
    gettext-dev

# Build libeconf from source (static) — Alpine ships no libeconf-static, and
# the static link pulls it in via glib's gio -> libmount -> libblkid chain
RUN git clone --depth 1 --branch v0.8.4 https://github.com/openSUSE/libeconf.git /src/libeconf && \
    cd /src/libeconf && \
    meson setup build --prefix=/usr --libdir=lib --buildtype=release --default-library=static && \
    meson compile -C build && \
    meson install -C build

# Build libexif from source (static) — Alpine ships no libexif-static, and
# without it vips loses EXIF orientation handling
RUN git clone --depth 1 --branch v0.6.26 https://github.com/libexif/libexif.git /src/libexif && \
    cd /src/libexif && \
    autoreconf -i && \
    ./configure --disable-shared --enable-static --disable-docs --disable-nls && \
    make -j$(nproc) && make install

# Build Highway from source (static) — Alpine ships no highway-static. This is
# libvips's SIMD backend; without it resize and convolution fall back to scalar.
RUN git clone --depth 1 --branch 1.3.0 https://github.com/google/highway.git /src/highway && \
    cd /src/highway && \
    cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DHWY_ENABLE_TESTS=OFF \
      -DHWY_ENABLE_EXAMPLES=OFF \
      -DHWY_ENABLE_CONTRIB=OFF && \
    cmake --build build -j$(nproc) && \
    cmake --install build

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
RUN git clone --depth 1 --branch ${VERSION} https://github.com/libvips/libvips.git /src/libvips

WORKDIR /src/libvips

# modules=disabled is required: libvips loads optional format support via
# dlopen, which cannot work in a statically linked binary.
#
# fftw is disabled deliberately. FFTW is GPL-2.0-or-later, so linking it would
# upgrade these binaries from libvips's own LGPL-2.1-or-later to GPL. The FFT
# operations it enables (fwfft, invfft, freqfilt) are not what this package is
# for. Set -Dfftw=enabled if you need them and accept the licence change.
#
# cgif is disabled because libvips gates GIF *save* behind a quantisation
# package, and both options are unattractive here: libimagequant is GPL-3.0,
# and quantizr needs a full cargo-c toolchain. GIF *load* still works; use the
# gifsicle or magick binaries in this package to write GIFs.
RUN meson setup build \
      --buildtype=release \
      --default-library=static \
      --prefer-static \
      -Dc_link_args="-static -leconf" \
      -Dcpp_link_args="-static -leconf" \
      -Dmodules=disabled \
      -Dintrospection=disabled \
      -Dvapi=false \
      -Dcplusplus=false \
      -Ddeprecated=false \
      -Dexamples=false \
      -Ddocs=false \
      -Djpeg=enabled \
      -Dpng=enabled \
      -Dspng=enabled \
      -Dwebp=enabled \
      -Dtiff=enabled \
      -Dlcms=enabled \
      -Dexif=enabled \
      -Dzlib=enabled \
      -Dfftw=disabled \
      -Dhighway=enabled \
      -Dcgif=disabled \
      -Dorc=enabled \
      -Dheif=disabled \
      -Djpeg-xl=disabled \
      -Dmagick=disabled \
      -Dpoppler=disabled \
      -Dpdfium=disabled \
      -Dopenslide=disabled \
      -Dopenexr=disabled \
      -Dopenjpeg=disabled \
      -Dmatio=disabled \
      -Dnifti=disabled \
      -Dcfitsio=disabled \
      -Darchive=disabled \
      -Drsvg=disabled \
      -Dpangocairo=disabled \
      -Dfontconfig=disabled \
      -Dimagequant=disabled \
      -Dquantizr=disabled \
      -Draw=disabled \
      -Duhdr=disabled && \
    meson compile -C build

# Verify static
RUN for b in vips vipsthumbnail; do \
      file /src/libvips/build/tools/$b && \
      file /src/libvips/build/tools/$b | grep -qv "dynamically linked" || exit 1; \
    done && \
    echo "Static binaries confirmed"

FROM scratch
COPY --from=builder /src/libvips/build/tools/vips /vips
COPY --from=builder /src/libvips/build/tools/vipsthumbnail /vipsthumbnail
