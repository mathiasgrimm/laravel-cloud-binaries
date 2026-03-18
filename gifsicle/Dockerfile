FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    autoconf \
    automake \
    git

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/kohler/gifsicle.git /src/gifsicle

WORKDIR /src/gifsicle

RUN autoreconf -i && \
    ./configure --disable-gifview && \
    make LDFLAGS="-static" -j$(nproc)

# Verify static
RUN file /src/gifsicle/src/gifsicle && \
    file /src/gifsicle/src/gifsicle | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/gifsicle/src/gifsicle /gifsicle
