FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cargo \
    rust \
    git \
    libpng-dev \
    libpng-static \
    lcms2-dev \
    lcms2-static \
    zlib-dev \
    zlib-static

ARG VERSION
RUN git clone --recursive --depth 1 --branch ${VERSION} https://github.com/kornelski/pngquant.git /src/pngquant

WORKDIR /src/pngquant

ENV RUSTFLAGS="-C target-feature=+crt-static"
RUN cargo build --release

# Verify static
RUN file /src/pngquant/target/release/pngquant && \
    file /src/pngquant/target/release/pngquant | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/pngquant/target/release/pngquant /pngquant
