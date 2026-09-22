#!/usr/bin/env python3
"""Exercise shipped CLI artifacts using generated fixtures and independent ExifTool reads."""
import os
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageCms, PngImagePlugin

BIN = Path(os.environ.get('BIN_DIR', '/opt/bin'))


def run(*args):
    return subprocess.check_output([str(a) for a in args], stderr=subprocess.PIPE)


def metadata(path):
    return tuple(run('exiftool', '-b', '-' + tag, path) for tag in ('ICC_Profile', 'XMP', 'EXIF'))


with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    # A distinct, valid override: change the profile header's manufacturer only.
    override = icc[:48] + b'TEST' + icc[52:]
    (tmp / 'override.icc').write_bytes(override)
    xmp = b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/" dc:description="grid metadata regression"/></rdf:RDF></x:xmpmeta>'
    exif = Image.Exif()
    exif[274] = 6  # Clockwise rotation, deliberately conflicts with CLI overrides.
    exif[270] = 'Exact Exif grid regression'
    exif_bytes = exif.tobytes()[6:]  # PNG eXIf and ExifTool use the TIFF payload.
    (tmp / 'source.exif').write_bytes(exif_bytes)
    # libavif 1.2.1 PNG reader resets Exif orientation to 1; JPEG and --exif retain it.
    exif[274] = 1
    stored_exif = exif.tobytes()[6:]
    exif[274] = 6
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_itxt('XML:com.adobe.xmp', xmp.decode())

    for alpha in (False, True):
        image = Image.new('RGBA' if alpha else 'RGB', (128, 192))
        image.putdata([
            ((x * 3 + y) % 256, (x + y * 2) % 256, (x * 7 + y * 3) % 256)
            + (((x * 5 + y) % 256,) if alpha else ())
            for y in range(192) for x in range(128)
        ])
        source = tmp / 'source.png'
        image.save(source, icc_profile=icc, exif=exif, pnginfo=pnginfo)
        assert metadata(source) == (icc, xmp, exif_bytes)
        cells = []
        for y in range(2):
            for x in range(2):
                cell = tmp / f'cell-{x}-{y}.png'
                image.crop((64*x, 96*y, 64*(x+1), 96*(y+1))).save(
                    cell, icc_profile=icc, exif=exif, pnginfo=pnginfo)
                cells.append(cell)
        for mode in ('embedded', 'override', 'ignore'):
            options = []
            expected = (icc, xmp, stored_exif)
            if mode == 'override':
                options = ['--icc', tmp / 'override.icc']
                expected = (override, xmp, stored_exif)
            elif mode == 'ignore':
                options = ['--ignore-icc', '--ignore-xmp', '--ignore-exif']
                expected = (b'', b'', b'')
            for orientation in ('embedded', 'exif', 'cli'):
                transforms = ['--exif', tmp / 'source.exif'] if orientation != 'embedded' and mode != 'ignore' else []
                if orientation == 'cli':
                    transforms += ['--irot', '2', '--imir', '1']
                case_expected = (*expected[:2], exif_bytes) if orientation != 'embedded' and mode != 'ignore' else expected
                infos = []
                for layout in ('ordinary', 'single-grid', 'explicit-cells'):
                    output = tmp / f'{layout}.avif'
                    inputs = cells if layout == 'explicit-cells' else [source]
                    grid = [] if layout == 'ordinary' else ['--grid', '2x2']
                    log = run(BIN / 'avifenc', '-j', '1', '-s', '10', '--lossless',
                              *options, *transforms, *grid, *inputs, output)
                    assert b"codec 'aom'" in log, log
                    assert metadata(output) == case_expected, (alpha, mode, orientation, layout, 'metadata')
                    info = run(BIN / 'avifdec', '--info', output).decode()
                    # Compare actual transform and color properties, not merely pixel size.
                    properties = [line.strip() for line in info.splitlines()
                                  if any(key in line for key in ('irot', 'imir', 'Primaries', 'Transfer', 'Matrix', 'Range'))]
                    assert properties, info
                    infos.append(properties)
                    decoded = tmp / f'{layout}.png'
                    run(BIN / 'avifdec', '-j', '1', output, decoded)
                    with Image.open(decoded) as result:
                        assert result.size == image.size
                        assert result.convert(image.mode).tobytes() == image.tobytes(), (alpha, mode, orientation, layout, 'pixels')
                assert infos[0] == infos[1] == infos[2], infos
                if orientation == 'cli':
                    assert any('irot' in p and '2' in p for p in infos[0]), infos
                    assert any('imir' in p and '1' in p for p in infos[0]), infos
                print(f'Grid metadata/pixels OK: alpha={alpha} {mode} {orientation}', flush=True)

    # JPEG readers extract embedded Exif orientation, unlike the PNG reader.
    jpeg = tmp / 'source.jpg'
    image.convert('RGB').save(jpeg, quality=95, icc_profile=icc, exif=exif)
    packet = b'http://ns.adobe.com/xap/1.0/\0' + xmp
    data = jpeg.read_bytes()
    jpeg.write_bytes(data[:2] + b'\xff\xe1' + (len(packet) + 2).to_bytes(2, 'big') + packet + data[2:])
    for cli in (False, True):
        properties = []
        pixels = []
        for grid in (False, True):
            output = tmp / 'jpeg.avif'
            run(BIN / 'avifenc', '-j', '1', '-s', '10', '--lossless',
                '--icc', tmp / 'override.icc',
                *(['--irot', '2', '--imir', '1'] if cli else []),
                *(['--grid', '2x2'] if grid else []), jpeg, output)
            assert metadata(output) == (override, xmp, exif_bytes)
            info = run(BIN / 'avifdec', '--info', output).decode()
            properties.append([line.strip() for line in info.splitlines()
                               if any(key in line for key in ('irot', 'imir', 'Primaries', 'Transfer', 'Matrix', 'Range'))])
            decoded = tmp / 'jpeg-decoded.png'
            run(BIN / 'avifdec', '-j', '1', output, decoded)
            with Image.open(decoded) as result:
                assert result.size == (128, 192)
                pixels.append(result.convert('RGB').tobytes())
        assert properties[0] == properties[1], properties
        assert any('irot' in p and ('2' if cli else '3') in p for p in properties[0]), properties
        assert pixels[0] == pixels[1]
        print(f'JPEG embedded orientation/explicit ICC OK: cli_override={cli}', flush=True)
