"""Deterministic ICC v4 matrix/TRC display profiles for the tests.

The profiles are generated from the published primaries, so the tests need no
downloaded or system profiles. Both use the sRGB transfer curve and a D65 white
point, adapted to the D50 profile connection space with Bradford.
"""

import struct

D65_XY = (0.3127, 0.3290)
D50_PCS = (0.9642, 1.0, 0.8249)
SRGB_PRIMARIES = ((0.640, 0.330), (0.300, 0.600), (0.150, 0.060))
DISPLAY_P3_PRIMARIES = ((0.680, 0.320), (0.265, 0.690), (0.150, 0.060))
BRADFORD = ((0.8951, 0.2664, -0.1614), (-0.7502, 1.7135, 0.0367), (0.0389, -0.0685, 1.0296))


def mat_mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def mat_vec(a, v):
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))


def mat_inv(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return (
        ((e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det),
        ((f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det),
        ((d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det),
    )


def xy_to_xyz(xy):
    x, y = xy
    return (x / y, 1.0, (1.0 - x - y) / y)


def rgb_to_xyz(primaries, white=D65_XY):
    """Linear RGB to XYZ matrix for the given primaries and white point."""
    columns = [xy_to_xyz(p) for p in primaries]
    p = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
    s = mat_vec(mat_inv(p), xy_to_xyz(white))
    return tuple(tuple(p[i][j] * s[j] for j in range(3)) for i in range(3))


def bradford(src_white, dst_white):
    src = mat_vec(BRADFORD, src_white)
    dst = mat_vec(BRADFORD, dst_white)
    scale = tuple(tuple((dst[i] / src[i]) if i == j else 0.0 for j in range(3)) for i in range(3))
    return mat_mul(mat_inv(BRADFORD), mat_mul(scale, BRADFORD))


def srgb_decode(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def srgb_encode(value):
    value = min(max(value, 0.0), 1.0)
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def convert(pixel, source_primaries, target_primaries):
    """Colorimetric conversion of one 8-bit pixel, clipped to the target gamut."""
    linear = [srgb_decode(c / 255) for c in pixel]
    xyz = mat_vec(rgb_to_xyz(source_primaries), linear)
    target = mat_vec(mat_inv(rgb_to_xyz(target_primaries)), xyz)
    return tuple(round(srgb_encode(c) * 255) for c in target)


def s15f16(value):
    return struct.pack(">i", round(value * 65536))


def xyz_type(xyz):
    return b"XYZ " + bytes(4) + b"".join(s15f16(v) for v in xyz)


def mluc(text):
    encoded = text.encode("utf-16-be")
    return b"mluc" + bytes(4) + struct.pack(">II2s2sII", 1, 12, b"en", b"US", len(encoded), 28) + encoded


def para_srgb():
    params = (2.4, 1 / 1.055, 0.055 / 1.055, 1 / 12.92, 0.04045)
    return b"para" + bytes(4) + struct.pack(">HH", 3, 0) + b"".join(s15f16(v) for v in params)


def profile(description, primaries):
    """Return an ICC v4.3 display profile as bytes."""
    chad = bradford(xy_to_xyz(D65_XY), D50_PCS)
    colorants = mat_mul(chad, rgb_to_xyz(primaries))
    trc = para_srgb()
    tags = [
        (b"desc", mluc(description)),
        (b"cprt", mluc("No copyright, use freely")),
        (b"wtpt", xyz_type(D50_PCS)),
        (b"chad", b"sf32" + bytes(4) + b"".join(s15f16(v) for row in chad for v in row)),
        (b"rXYZ", xyz_type(tuple(colorants[i][0] for i in range(3)))),
        (b"gXYZ", xyz_type(tuple(colorants[i][1] for i in range(3)))),
        (b"bXYZ", xyz_type(tuple(colorants[i][2] for i in range(3)))),
        (b"rTRC", trc),
        (b"gTRC", trc),
        (b"bTRC", trc),
    ]
    offset = 128 + 4 + 12 * len(tags)
    table, data = b"", b""
    for signature, payload in tags:
        table += signature + struct.pack(">II", offset + len(data), len(payload))
        data += payload + bytes(-len(payload) % 4)
    size = offset + len(data)
    header = (
        struct.pack(">I4sI4s4s4s", size, bytes(4), 0x04300000, b"mntr", b"RGB ", b"XYZ ")
        + struct.pack(">6H", 2026, 1, 1, 0, 0, 0)
        + b"acsp" + bytes(4) + bytes(4) + bytes(4) + bytes(4) + bytes(8)
        + struct.pack(">I", 0)
        + b"".join(s15f16(v) for v in D50_PCS)
        + bytes(4) + bytes(16) + bytes(28)
    )
    assert len(header) == 128
    return header + struct.pack(">I", len(tags)) + table + data


def srgb_profile():
    return profile("Test sRGB (generated)", SRGB_PRIMARIES)


def display_p3_profile():
    return profile("Test Display P3 (generated)", DISPLAY_P3_PRIMARIES)
