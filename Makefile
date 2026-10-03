# ── Versions ────────────────────────────────────────────────
JPEGOPTIM_VERSION := v1.5.6
OPTIPNG_VERSION   := 0.7.8
PNGQUANT_VERSION  := 3.0.3
LIBWEBP_VERSION   := v1.5.0
LIBAVIF_VERSION   := v1.2.1
DAV1D_VERSION     := 1.5.1
DAV1D_COMMIT      := 42b2b24fb8819f1ed3643aa9cf2a62f03868e3aa
GIFSICLE_VERSION     := v1.96
FFMPEG_VERSION       := n7.1.1
IMAGEMAGICK_VERSION  := 7.1.1-43
ZSTD_VERSION         := v1.5.7
QPDF_VERSION         := v12.4.0
LIBJXL_VERSION       := v0.12.0
LIBJXL_COMMIT        := a7a9c787341cf703dede03c2009fa460cae5e5df
LIBVMAF_VERSION      := v3.2.1
LIBVMAF_COMMIT       := f85a853692a8c730d0270cd733c8bb30b5b93b7c
LCMS2_VERSION        := lcms2.19.1
LCMS2_COMMIT         := 21c582a594fe5279f90c0b93437c398f93bf62b0
# ────────────────────────────────────────────────────────────

BINARIES := bin/jpegoptim bin/optipng bin/pngquant bin/cwebp bin/dwebp bin/avifenc bin/avifdec bin/gifsicle bin/ffmpeg bin/ffprobe bin/magick bin/zstd bin/qpdf bin/ssimulacra2 bin/butteraugli_main

.PHONY: all test test-only test-avif test-icc test-metrics release check-version clean clean-images clean-all

all: $(BINARIES)

# --- jpegoptim ---
bin/jpegoptim: jpegoptim/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(JPEGOPTIM_VERSION) -t jpegoptim ./jpegoptim
	docker rm -f tmp-jpegoptim 2>/dev/null || true
	docker create --name tmp-jpegoptim jpegoptim /true
	docker cp tmp-jpegoptim:/jpegoptim bin/jpegoptim
	docker rm tmp-jpegoptim

# --- optipng ---
bin/optipng: optipng/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(OPTIPNG_VERSION) -t optipng ./optipng
	docker rm -f tmp-optipng 2>/dev/null || true
	docker create --name tmp-optipng optipng /true
	docker cp tmp-optipng:/optipng bin/optipng
	docker rm tmp-optipng

# --- pngquant ---
bin/pngquant: pngquant/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(PNGQUANT_VERSION) -t pngquant ./pngquant
	docker rm -f tmp-pngquant 2>/dev/null || true
	docker create --name tmp-pngquant pngquant /true
	docker cp tmp-pngquant:/pngquant bin/pngquant
	docker rm tmp-pngquant

# --- cwebp + dwebp (single image, two binaries) ---
bin/cwebp bin/dwebp: cwebp/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(LIBWEBP_VERSION) -t cwebp ./cwebp
	docker rm -f tmp-cwebp 2>/dev/null || true
	docker create --name tmp-cwebp cwebp /true
	docker cp tmp-cwebp:/cwebp bin/cwebp
	docker cp tmp-cwebp:/dwebp bin/dwebp
	docker rm tmp-cwebp

# --- avifenc + avifdec (single image, two binaries) ---
bin/avifenc bin/avifdec: avifenc/Dockerfile avifenc/patches/grid-metadata.patch Makefile
	mkdir -p bin
	docker build --platform linux/arm64 --build-arg VERSION=$(LIBAVIF_VERSION) --build-arg DAV1D_VERSION=$(DAV1D_VERSION) --build-arg DAV1D_COMMIT=$(DAV1D_COMMIT) -t avifenc ./avifenc
	docker rm -f tmp-avifenc 2>/dev/null || true
	docker create --name tmp-avifenc avifenc /true
	docker cp tmp-avifenc:/avifenc bin/avifenc
	docker cp tmp-avifenc:/avifdec bin/avifdec
	docker rm tmp-avifenc

# --- gifsicle ---
bin/gifsicle: gifsicle/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(GIFSICLE_VERSION) -t gifsicle ./gifsicle
	docker rm -f tmp-gifsicle 2>/dev/null || true
	docker create --name tmp-gifsicle gifsicle /true
	docker cp tmp-gifsicle:/gifsicle bin/gifsicle
	docker rm tmp-gifsicle

# --- ffmpeg + ffprobe (single image, two binaries) ---
bin/ffmpeg bin/ffprobe: ffmpeg/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(FFMPEG_VERSION) --build-arg LIBWEBP_VERSION=$(LIBWEBP_VERSION) --build-arg LIBVMAF_VERSION=$(LIBVMAF_VERSION) --build-arg LIBVMAF_COMMIT=$(LIBVMAF_COMMIT) -t ffmpeg ./ffmpeg
	docker rm -f tmp-ffmpeg 2>/dev/null || true
	docker create --name tmp-ffmpeg ffmpeg /true
	docker cp tmp-ffmpeg:/ffmpeg bin/ffmpeg
	docker cp tmp-ffmpeg:/ffprobe bin/ffprobe
	docker rm tmp-ffmpeg

# --- magick ---
bin/magick: imagemagick/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(IMAGEMAGICK_VERSION) --build-arg LCMS2_VERSION=$(LCMS2_VERSION) --build-arg LCMS2_COMMIT=$(LCMS2_COMMIT) -t imagemagick ./imagemagick
	docker rm -f tmp-imagemagick 2>/dev/null || true
	docker create --name tmp-imagemagick imagemagick /true
	docker cp tmp-imagemagick:/magick bin/magick
	docker rm tmp-imagemagick

# --- zstd ---
bin/zstd: zstd/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(ZSTD_VERSION) -t zstd ./zstd
	docker rm -f tmp-zstd 2>/dev/null || true
	docker create --name tmp-zstd zstd /true
	docker cp tmp-zstd:/zstd bin/zstd
	docker rm tmp-zstd

# --- qpdf ---
bin/qpdf: qpdf/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(QPDF_VERSION) -t qpdf ./qpdf
	docker rm -f tmp-qpdf 2>/dev/null || true
	docker create --name tmp-qpdf qpdf /true
	docker cp tmp-qpdf:/qpdf bin/qpdf
	docker rm tmp-qpdf

# --- ssimulacra2 + butteraugli_main (single image, two binaries) ---
bin/ssimulacra2 bin/butteraugli_main: libjxl/Dockerfile Makefile
	mkdir -p bin
	docker build --platform linux/arm64 --build-arg VERSION=$(LIBJXL_VERSION) --build-arg COMMIT=$(LIBJXL_COMMIT) -t libjxl ./libjxl
	docker rm -f tmp-libjxl 2>/dev/null || true
	docker create --name tmp-libjxl libjxl /true
	docker cp tmp-libjxl:/ssimulacra2 bin/ssimulacra2
	docker cp tmp-libjxl:/butteraugli_main bin/butteraugli_main
	docker rm tmp-libjxl

# --- Test ---
test: $(BINARIES) test-only

test-avif:
	docker run --rm --platform linux/arm64 -v "$(CURDIR)/bin:/opt/bin:ro" -v "$(CURDIR)/tests:/opt/tests:ro" alpine sh -c 'apk add --no-cache file binutils python3 py3-pillow exiftool >/dev/null && sh /opt/tests/avif.sh && python3 /opt/tests/avif-grid-metadata.py'

test-icc:
	docker run --rm --platform linux/arm64 -e PYTHONDONTWRITEBYTECODE=1 -v "$(CURDIR)/bin:/opt/bin:ro" -v "$(CURDIR)/tests:/opt/tests:ro" alpine sh -c 'apk add --no-cache python3 >/dev/null && python3 /opt/tests/magick-icc.py'

test-metrics:
	docker run --rm --platform linux/arm64 -e PYTHONDONTWRITEBYTECODE=1 -v "$(CURDIR)/bin:/opt/bin:ro" -v "$(CURDIR)/tests:/opt/tests:ro" alpine sh -c 'apk add --no-cache file binutils python3 >/dev/null && sh /opt/tests/static-elf.sh ssimulacra2 butteraugli_main ffmpeg ffprobe magick && python3 /opt/tests/quality-metrics.py'

test-only: test-avif test-icc test-metrics
	docker run --rm -v "$(CURDIR)/bin:/opt/bin:ro" -v "$(CURDIR)/tests:/opt/tests:ro" alpine sh /opt/tests/ffmpeg-webp.sh
	docker run --rm -v $(CURDIR)/bin:/opt/bin alpine sh -c ' \
		set -e && \
		/opt/bin/jpegoptim --version && \
		/opt/bin/optipng -v && \
		/opt/bin/pngquant --version && \
		/opt/bin/cwebp -version && \
		/opt/bin/dwebp -version && \
		/opt/bin/avifenc --version && \
		/opt/bin/avifdec --version && \
		/opt/bin/gifsicle --version && \
		/opt/bin/ffmpeg -version && \
		/opt/bin/ffprobe -version && \
		/opt/bin/magick -version && \
		/opt/bin/zstd --version && \
		/opt/bin/qpdf --version && \
		apk add --no-cache file >/dev/null 2>&1 && \
		if file /opt/bin/* | grep "not stripped"; then \
			echo "ERROR: the binaries listed above are not stripped"; exit 1; \
		fi && \
		echo "All binaries stripped" && \
		echo "All binaries OK" \
	'

# --- Release ---
# make release VERSION=vX.Y.Z [NOTES=notes.md]
# Tests the committed binaries (no rebuild), tags the current main commit with an
# annotated tag, pushes the tag and creates the GitHub release. Without NOTES, the
# release notes are generated by GitHub. Packagist picks up the tag by itself.
release: check-version
	@[ "$$(git branch --show-current)" = "main" ] || { echo "Releases are cut from main."; exit 1; }
	@[ -z "$$(git status --porcelain)" ] || { echo "The working tree is not clean."; exit 1; }
	git fetch origin main --tags
	@[ "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" ] || { echo "Local main is not origin/main."; exit 1; }
	@! git rev-parse -q --verify "refs/tags/$(VERSION)" >/dev/null || { echo "Tag $(VERSION) already exists."; exit 1; }
	$(MAKE) test-only
	git tag -a $(VERSION) -m $(VERSION)
	git push origin $(VERSION)
	gh release create $(VERSION) --verify-tag --title $(VERSION) $(if $(NOTES),--notes-file "$(NOTES)",--generate-notes)

check-version:
	@[ -n "$(VERSION)" ] || { echo "VERSION is required, e.g. make release VERSION=v1.5.0"; exit 1; }
	@printf '%s\n' "$(VERSION)" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$$' || { echo "VERSION must look like v1.5.0"; exit 1; }

# --- Cleanup ---
clean:
	find bin -mindepth 1 ! -name .gitkeep -delete

clean-images:
	docker rmi -f jpegoptim optipng pngquant cwebp avifenc gifsicle ffmpeg imagemagick zstd qpdf libjxl 2>/dev/null || true

clean-all: clean clean-images
