FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    autoconf \
    automake \
    cmake \
    nasm \
    yasm \
    git \
    pkgconf \
    bash \
    perl \
    linux-headers \
    x264-dev \
    lame-dev \
    freetype-dev \
    freetype-static \
    zlib-dev \
    zlib-static \
    bzip2-dev \
    bzip2-static \
    libpng-dev \
    libpng-static \
    brotli-dev \
    brotli-static \
    diffutils \
    meson \
    ninja \
    xxd

# Build x265 from source (static) — Alpine package lacks .a
# Patch CMakeLists.txt for CMake 4.x compatibility
RUN git clone --depth 1 -b 4.1 https://bitbucket.org/multicoreware/x265_git.git /src/x265 && \
    cd /src/x265 && \
    sed -i '/CMP0025/,/endif/d' source/CMakeLists.txt && \
    sed -i '/CMP0054/,/endif/d' source/CMakeLists.txt && \
    sed -i 's/cmake_minimum_required (VERSION 2.8.8)/cmake_minimum_required(VERSION 3.10)/' source/CMakeLists.txt && \
    cd build/linux && \
    cmake ../../source \
      -DCMAKE_BUILD_TYPE=Release \
      -DENABLE_SHARED=OFF \
      -DENABLE_CLI=OFF \
      -DENABLE_LIBNUMA=OFF && \
    make -j$(nproc) && make install && \
    sed -i 's/Libs.private:.*/Libs.private: -lstdc++ -lm -ldl -lpthread/' /usr/local/lib/pkgconfig/x265.pc

# Build libvpx from source (static) — Alpine package lacks .a
RUN git clone --depth 1 --branch v1.15.0 https://chromium.googlesource.com/webm/libvpx.git /src/libvpx && \
    cd /src/libvpx && \
    ./configure --disable-shared --enable-static --disable-examples --disable-tools --disable-unit-tests && \
    make -j$(nproc) && make install

# Build opus from source (static) — Alpine package lacks .a
RUN git clone --depth 1 --branch v1.5.2 https://github.com/xiph/opus.git /src/opus && \
    cd /src/opus && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DOPUS_BUILD_PROGRAMS=OFF -DOPUS_BUILD_TESTING=OFF && \
    cmake --build build -j$(nproc) && cmake --install build

# Use the same pinned libwebp as cwebp/dwebp, linked into ffmpeg itself.
ARG LIBWEBP_VERSION
RUN git clone --depth 1 --branch ${LIBWEBP_VERSION} https://chromium.googlesource.com/webm/libwebp.git /src/libwebp && \
    cd /src/libwebp && \
    cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DWEBP_LINK_STATIC=ON \
      -DWEBP_BUILD_CWEBP=OFF \
      -DWEBP_BUILD_DWEBP=OFF \
      -DWEBP_BUILD_ANIM_UTILS=OFF \
      -DWEBP_BUILD_GIF2WEBP=OFF \
      -DWEBP_BUILD_IMG2WEBP=OFF \
      -DWEBP_BUILD_VWEBP=OFF \
      -DWEBP_BUILD_WEBPINFO=OFF \
      -DWEBP_BUILD_WEBPMUX=OFF \
      -DWEBP_BUILD_EXTRAS=OFF && \
    cmake --build build -j$(nproc) && cmake --install build

# Build libvmaf from source (static) for the libvmaf filter, at a verified commit.
# Floating-point extractors (float_ssim, float_ms_ssim) are off by default.
# Built-in models need no model files at runtime. libvmaf contains C++ (libsvm),
# so its static link needs libstdc++, as x265 does.
ARG LIBVMAF_VERSION
ARG LIBVMAF_COMMIT
RUN git clone --depth 1 --branch ${LIBVMAF_VERSION} https://github.com/Netflix/vmaf.git /src/vmaf && \
    test "$(git -C /src/vmaf rev-parse HEAD)" = "${LIBVMAF_COMMIT}" && \
    cd /src/vmaf/libvmaf && \
    meson setup build \
      --buildtype=release \
      --default-library=static \
      --prefix=/usr/local \
      --libdir=lib \
      -Denable_float=true \
      -Dbuilt_in_models=true \
      -Denable_tests=false \
      -Denable_docs=false \
      -Denable_tools=false && \
    ninja -C build && ninja -C build install && \
    sed -i 's/^Libs:.*/& -lstdc++/' /usr/local/lib/pkgconfig/libvmaf.pc && \
    grep -q '^Libs:.* -lstdc++$' /usr/local/lib/pkgconfig/libvmaf.pc

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/FFmpeg/FFmpeg.git /src/ffmpeg

WORKDIR /src/ffmpeg

RUN PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/usr/local/lib64/pkgconfig:$PKG_CONFIG_PATH" \
    ./configure \
      --enable-gpl \
      --enable-static \
      --disable-shared \
      --enable-libx264 \
      --enable-libx265 \
      --enable-libvpx \
      --enable-libopus \
      --enable-libmp3lame \
      --enable-libfreetype \
      --enable-libwebp \
      --enable-libvmaf \
      --extra-cflags="-I/usr/local/include" \
      --extra-ldflags="-static -L/usr/local/lib -L/usr/local/lib64" \
      --pkg-config-flags="--static" \
      --disable-doc \
      --disable-ffplay && \
    make -j$(nproc)

# Emit dependency provenance into the build log for artifact updates.
RUN cat /etc/alpine-release && \
    apk list --installed x264-dev lame-dev freetype-static zlib-static bzip2-static libpng-static brotli-static musl && \
    git -C /src/vmaf rev-parse HEAD && git -C /src/libwebp rev-parse HEAD

# Strip symbol tables -- these are shipped artifacts, not debugging targets
RUN strip /src/ffmpeg/ffmpeg /src/ffmpeg/ffprobe

# Verify static
RUN file /src/ffmpeg/ffmpeg && \
    file /src/ffmpeg/ffmpeg | grep -qv "dynamically linked" && \
    file /src/ffmpeg/ffprobe && \
    file /src/ffmpeg/ffprobe | grep -qv "dynamically linked" && \
    echo "Static binaries confirmed"

FROM scratch
COPY --from=builder /src/ffmpeg/ffmpeg /ffmpeg
COPY --from=builder /src/ffmpeg/ffprobe /ffprobe
