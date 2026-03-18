# ── Versions ────────────────────────────────────────────────
JPEGOPTIM_VERSION := v1.5.6
OPTIPNG_VERSION   := 0.7.8
PNGQUANT_VERSION  := 3.0.3
LIBWEBP_VERSION   := v1.5.0
LIBAVIF_VERSION   := v1.2.1
GIFSICLE_VERSION  := v1.96
# ────────────────────────────────────────────────────────────

BINARIES := bin/jpegoptim bin/optipng bin/pngquant bin/cwebp bin/dwebp bin/avifenc bin/avifdec bin/gifsicle

.PHONY: all test clean clean-images clean-all

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
bin/avifenc bin/avifdec: avifenc/Dockerfile
	mkdir -p bin
	docker build --build-arg VERSION=$(LIBAVIF_VERSION) -t avifenc ./avifenc
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

# --- Test ---
test: $(BINARIES)
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
		echo "All binaries OK" \
	'

# --- Cleanup ---
clean:
	find bin -mindepth 1 ! -name .gitkeep -delete

clean-images:
	docker rmi -f jpegoptim optipng pngquant cwebp avifenc gifsicle 2>/dev/null || true

clean-all: clean clean-images
