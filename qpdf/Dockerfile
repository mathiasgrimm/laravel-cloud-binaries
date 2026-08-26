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
# without linking gnutls or openssl.
RUN cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DBUILD_STATIC_LIBS=ON \
      -DUSE_IMPLICIT_CRYPTO=OFF \
      -DREQUIRE_CRYPTO_NATIVE=ON \
      -DBUILD_DOC=OFF \
      -DINSTALL_EXAMPLES=OFF \
      -DINSTALL_MANUAL=OFF \
      -DCMAKE_EXE_LINKER_FLAGS="-static" \
      -DCMAKE_C_FLAGS="-Os" \
      -DCMAKE_CXX_FLAGS="-Os" && \
    cmake --build build --target qpdf -j$(nproc) && \
    strip build/qpdf/qpdf

# Verify static
RUN file /src/qpdf/build/qpdf/qpdf && \
    file /src/qpdf/build/qpdf/qpdf | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/qpdf/build/qpdf/qpdf /qpdf
