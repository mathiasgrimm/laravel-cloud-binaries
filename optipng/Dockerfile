FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    libpng-dev \
    libpng-static \
    zlib-dev \
    zlib-static

ARG VERSION
RUN wget -O optipng.tar.gz "https://sourceforge.net/projects/optipng/files/OptiPNG/optipng-${VERSION}/optipng-${VERSION}.tar.gz/download" && \
    tar xzf optipng.tar.gz && \
    cd optipng-${VERSION} && \
    ./configure --with-system-libpng --with-system-zlib && \
    make LDFLAGS="-static" -j$(nproc)

# Verify static
RUN file /optipng-${VERSION}/src/optipng/optipng && \
    file /optipng-${VERSION}/src/optipng/optipng | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

RUN cp /optipng-${VERSION}/src/optipng/optipng /optipng

FROM scratch
COPY --from=builder /optipng /optipng
