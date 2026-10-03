FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    file \
    git \
    pkgconf \
    libpng-dev \
    libpng-static \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    zlib-dev \
    zlib-static

ARG VERSION
ARG COMMIT
RUN git clone --depth 1 --branch ${VERSION} https://github.com/libjxl/libjxl.git /src/libjxl && \
    test "$(git -C /src/libjxl rev-parse HEAD)" = "${COMMIT}"

WORKDIR /src/libjxl

# Highway, Brotli and skcms come from the submodule commits pinned by this
# libjxl commit. A leading '-' or '+' in the status means a missing or
# different checkout. skcms is the color management system; lcms2 is not used.
RUN git submodule update --init --depth 1 --recommend-shallow \
      third_party/highway third_party/brotli third_party/skcms && \
    git submodule status third_party/highway third_party/brotli third_party/skcms | tee /tmp/submodules && \
    ! grep -q '^[-+U]' /tmp/submodules

# Build only the two metric tools. PNG and JPEG inputs use the static Alpine
# libraries; GIF and OpenEXR inputs are not enabled. Section garbage collection
# drops the unused parts of the static libjxl libraries (about 9 MB to 4 MB per
# tool) without changing the code that runs.
RUN cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_C_FLAGS="-ffunction-sections -fdata-sections" \
      -DCMAKE_CXX_FLAGS="-ffunction-sections -fdata-sections" \
      -DCMAKE_EXE_LINKER_FLAGS="-Wl,--gc-sections" \
      -DBUILD_TESTING=OFF \
      -DJPEGXL_STATIC=ON \
      -DJPEGXL_ENABLE_TOOLS=ON \
      -DJPEGXL_ENABLE_DEVTOOLS=ON \
      -DJPEGXL_ENABLE_SKCMS=ON \
      -DJPEGXL_ENABLE_BENCHMARK=OFF \
      -DJPEGXL_ENABLE_EXAMPLES=OFF \
      -DJPEGXL_ENABLE_JNI=OFF \
      -DJPEGXL_ENABLE_SJPEG=OFF \
      -DJPEGXL_ENABLE_OPENEXR=OFF \
      -DJPEGXL_ENABLE_DOXYGEN=OFF \
      -DJPEGXL_ENABLE_MANPAGES=OFF \
      -DJPEGXL_ENABLE_TCMALLOC=OFF \
      -DJPEGXL_ENABLE_PLUGINS=OFF \
      -DJPEGXL_ENABLE_VIEWERS=OFF \
      -DCMAKE_DISABLE_FIND_PACKAGE_GIF=ON && \
    cmake --build build --target ssimulacra2 butteraugli_main -j$(nproc)

# Emit dependency provenance into the build log for artifact updates.
RUN cat /etc/alpine-release && \
    apk list --installed libpng-static libjpeg-turbo-static zlib-static musl && \
    git rev-parse HEAD && cat /tmp/submodules

# Strip symbol tables -- these are shipped artifacts, not debugging targets
RUN strip /src/libjxl/build/tools/ssimulacra2 /src/libjxl/build/tools/butteraugli_main

# Both shipped artifacts must be static and have no ELF interpreter or dependencies.
RUN for binary in /src/libjxl/build/tools/ssimulacra2 /src/libjxl/build/tools/butteraugli_main; do \
      file "$binary" && \
      file "$binary" | grep -Eq 'statically linked|static-pie linked' && \
      readelf -h "$binary" | grep -q 'Machine:.*AArch64' && \
      ! readelf -l "$binary" | grep -q INTERP && \
      ! readelf -d "$binary" | grep -q NEEDED || exit 1; \
    done

FROM scratch
COPY --from=builder /src/libjxl/build/tools/ssimulacra2 /ssimulacra2
COPY --from=builder /src/libjxl/build/tools/butteraugli_main /butteraugli_main
