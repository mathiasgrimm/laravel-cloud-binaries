FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    git \
    zlib-dev \
    zlib-static \
    xz-dev \
    xz-static \
    lz4-dev \
    lz4-static

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/facebook/zstd.git /src/zstd

WORKDIR /src/zstd

RUN make -C programs -j$(nproc) zstd \
      HAVE_ZLIB=1 HAVE_LZMA=1 HAVE_LZ4=1 \
      LDFLAGS="-static"

# Verify static
RUN file /src/zstd/programs/zstd && \
    file /src/zstd/programs/zstd | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/zstd/programs/zstd /zstd
