FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    pkgconf \
    git \
    zlib-dev \
    zlib-static \
    libjpeg-turbo-dev \
    libjpeg-turbo-static

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/qpdf/qpdf.git /src/qpdf

WORKDIR /src/qpdf

# USE_IMPLICIT_CRYPTO=OFF + REQUIRE_CRYPTO_NATIVE=ON keeps encryption support
# without linking gnutls or openssl. Note that the native provider compiles in
# an RSA-MD licensed MD5 implementation, which carries an attribution
# requirement -- see THIRD-PARTY-NOTICES.md.
#
# MinSizeRel is -Os. Passing -Os via CMAKE_<LANG>_FLAGS would not work: cmake
# appends the per-config flags last, so Release's -O3 would win.
#
# strip is a deliberate deviation from the other Dockerfiles here -- none of
# them strip. It cuts ~40% (5.5 MB -> 3.3 MB) and qpdf has no plugin ABI that
# needs the symbols.
RUN cmake -B build \
      -DCMAKE_BUILD_TYPE=MinSizeRel \
      -DBUILD_SHARED_LIBS=OFF \
      -DUSE_IMPLICIT_CRYPTO=OFF \
      -DREQUIRE_CRYPTO_NATIVE=ON \
      -DCMAKE_EXE_LINKER_FLAGS="-static" && \
    cmake --build build --target qpdf -j$(nproc) && \
    strip build/qpdf/qpdf

# Verify static
RUN file /src/qpdf/build/qpdf/qpdf && \
    file /src/qpdf/build/qpdf/qpdf | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/qpdf/build/qpdf/qpdf /qpdf
