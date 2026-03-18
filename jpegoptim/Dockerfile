FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    git \
    libjpeg-turbo-dev \
    libjpeg-turbo-static

ARG VERSION
RUN git clone --depth 1 --branch ${VERSION} https://github.com/tjko/jpegoptim.git /src/jpegoptim

WORKDIR /src/jpegoptim

ENV CMAKE_POLICY_VERSION_MINIMUM=3.5
RUN mkdir build && cd build && \
    cmake .. -DCMAKE_EXE_LINKER_FLAGS="-static" -DCMAKE_BUILD_TYPE=Release && \
    (make -j$(nproc) || true) && \
    ln -snf lib64 mozjpeg/lib && \
    make -j$(nproc)

# Verify static
RUN file /src/jpegoptim/build/jpegoptim && \
    file /src/jpegoptim/build/jpegoptim | grep -qv "dynamically linked" && \
    echo "Static binary confirmed"

FROM scratch
COPY --from=builder /src/jpegoptim/build/jpegoptim /jpegoptim
