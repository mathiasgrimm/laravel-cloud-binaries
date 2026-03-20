FROM alpine:latest AS builder

RUN apk add --no-cache \
    build-base \
    cmake \
    pkgconf \
    git \
    libjpeg-turbo-dev \
    libjpeg-turbo-static \
    libpng-dev \
    libpng-static \
    freetype-dev \
    freetype-static \
    zlib-dev \
    zlib-static \
    fontconfig-dev \
    fontconfig-static \
    lcms2-dev \
    lcms2-static \
    expat-dev \
    expat-static \
    brotli-dev \
    brotli-static \
    bzip2-dev \
    bzip2-static \
    xz-dev \
    xz-static

# Build libtiff from source (static) — Alpine package lacks tiff-static
# Disable optional codecs to avoid CMake target resolution issues downstream
RUN git clone --depth 1 --branch v4.7.0 https://gitlab.com/libtiff/libtiff.git /src/libtiff && \
    cd /src/libtiff && \
    cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -Dtiff-tools=OFF \
      -Dtiff-tests=OFF \
      -Dtiff-contrib=OFF \
      -Dtiff-docs=OFF \
      -Dlzma=OFF \
      -Dzstd=OFF \
      -Dwebp=OFF \
      -Djbig=OFF \
      -Dlerc=OFF \
      -Djpeg12=OFF && \
    cmake --build build -j$(nproc) && \
    cmake --install build && \
    rm -rf /usr/local/lib/cmake/tiff

# Build openjpeg from source (static) — for JPEG2000 support in PDFs
RUN git clone --depth 1 --branch v2.5.3 https://github.com/uclouvain/openjpeg.git /src/openjpeg && \
    cd /src/openjpeg && \
    cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DBUILD_CODEC=OFF \
      -DBUILD_TESTING=OFF && \
    cmake --build build -j$(nproc) && \
    cmake --install build

ARG VERSION
RUN git clone --depth 1 --branch poppler-${VERSION} https://gitlab.freedesktop.org/poppler/poppler.git /src/poppler

# Poppler requires its test data to be present for configuration
RUN git clone --depth 1 https://gitlab.freedesktop.org/poppler/test.git /src/poppler/testdata

WORKDIR /src/poppler

# Step 1: Configure without -static (so cmake try_compile tests pass)
RUN cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=OFF \
      -DENABLE_GLIB=OFF \
      -DENABLE_QT5=OFF \
      -DENABLE_QT6=OFF \
      -DENABLE_CPP=OFF \
      -DENABLE_BOOST=OFF \
      -DENABLE_NSS3=OFF \
      -DENABLE_GPGME=OFF \
      -DENABLE_LIBCURL=OFF \
      -DENABLE_SPLASH=ON \
      -DENABLE_UTILS=ON \
      -DENABLE_ZLIB=ON \
      -DENABLE_LIBTIFF=ON \
      -DENABLE_LIBOPENJPEG=openjpeg2 \
      -DENABLE_CMS=lcms2 \
      -DFONT_CONFIGURATION=fontconfig \
      -DTESTDATADIR=/src/poppler/testdata

# Step 2: Patch generated link commands — replace all .so paths with -l flags
#         and inject -static so the linker resolves to .a files
# Only patch link.txt files for executables (in utils/), not for libpoppler.a
RUN find build/utils -name 'link.txt' -exec sed -i \
      -e 's|/usr/lib/lib\([a-zA-Z0-9_+-]*\)\.so[.0-9]*|-l\1|g' \
      -e 's|/usr/local/lib/lib\([a-zA-Z0-9_+-]*\)\.so[.0-9]*|-l\1|g' \
      {} + && \
    find build/utils -name 'link.txt' -exec sed -i \
      's|/usr/bin/c++|/usr/bin/c++ -static|' {} + && \
    find build/utils -name 'link.txt' -exec sed -i \
      's|$| -lfontconfig -lfreetype -lexpat -lbrotlidec -lbrotlicommon -lbz2 -lpng16 -lz -ljpeg -ltiff -lopenjp2 -llcms2 -lm -lpthread -lstdc++|' {} +

# Step 3: Build
RUN make -C build -j$(nproc)

# Verify all 7 binaries are static
RUN for bin in pdftotext pdftoppm pdftohtml pdfimages pdfinfo pdfunite pdfseparate; do \
      file /src/poppler/build/utils/$bin && \
      file /src/poppler/build/utils/$bin | grep -qv "dynamically linked" && \
      echo "$bin: static binary confirmed"; \
    done

FROM scratch
COPY --from=builder /src/poppler/build/utils/pdftotext /pdftotext
COPY --from=builder /src/poppler/build/utils/pdftoppm /pdftoppm
COPY --from=builder /src/poppler/build/utils/pdftohtml /pdftohtml
COPY --from=builder /src/poppler/build/utils/pdfimages /pdfimages
COPY --from=builder /src/poppler/build/utils/pdfinfo /pdfinfo
COPY --from=builder /src/poppler/build/utils/pdfunite /pdfunite
COPY --from=builder /src/poppler/build/utils/pdfseparate /pdfseparate
