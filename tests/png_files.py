"""Minimal PNG writing and inspection for test fixtures.

Fixtures are generated with integer arithmetic and written without an imaging
library, so they decode to the same pixels on every architecture.
"""

import struct
import zlib


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def write_png(path, width, height, pixels, channels, icc=None):
    """Write 8-bit RGB (3 channels) or RGBA (4 channels) pixels, optionally with an ICC profile."""
    assert len(pixels) == width * height * channels
    color_type = {3: 2, 4: 6}[channels]
    stride = width * channels
    rows = b"".join(b"\x00" + bytes(pixels[y * stride:(y + 1) * stride]) for y in range(height))
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0))
    if icc is not None:
        data += chunk(b"iCCP", b"icc\x00\x00" + zlib.compress(icc))
    data += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


def color_type(path):
    """Return the IHDR (bit depth, color type) of a PNG file."""
    with open(path, "rb") as fh:
        head = fh.read(29)
    assert head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR"
    return head[24], head[25]
