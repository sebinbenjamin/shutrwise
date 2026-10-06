#!/usr/bin/env python3
"""Inspect original DNGs with LibRaw/rawpy; derived previews are for review only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import rawpy
import tifffile
from PIL import Image, ImageDraw


def inspect(path):
    metadata = json.loads(path.with_name(path.stem + '-result.json').read_text())
    result = metadata['result']
    with rawpy.imread(str(path)) as raw:
        pixels = raw.raw_image_visible
        stats = {
            'rawpy_visible_width': int(raw.sizes.width),
            'rawpy_visible_height': int(raw.sizes.height),
            'raw_width': int(raw.sizes.raw_width),
            'raw_height': int(raw.sizes.raw_height),
            'crop_width': int(raw.sizes.crop_width),
            'crop_height': int(raw.sizes.crop_height),
            'sample_dtype': str(pixels.dtype),
            'white_level': int(raw.white_level),
            'black_level_per_channel': raw.black_level_per_channel,
            'cfa_pattern': raw.raw_pattern.tolist() if raw.raw_pattern is not None else None,
            'color_description': raw.color_desc.decode('ascii'),
            'sample_min': int(pixels.min()),
            'sample_max': int(pixels.max()),
            'sample_median': float(np.median(pixels)),
            'sample_percentiles_1_50_99': np.percentile(pixels, [1, 50, 99]).tolist(),
            'sample_at_or_above_white_percent': float(np.mean(pixels >= raw.white_level) * 100),
            'libraw_decode_ok': True,
        }
        rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True,
                              output_bps=8, half_size=True)
        preview = Image.fromarray(rgb)
        preview.thumbnail((1000, 750))
        preview.save(path.with_name(path.stem + '-decoded-preview.jpg'), quality=90)
    with tifffile.TiffFile(path) as tiff:
        page = tiff.pages[0]
        def tag(name):
            return page.tags[name].value if name in page.tags else None
        exposure = tag('ExposureTime')
        tiff_seconds = exposure[0] / exposure[1] if exposure else None
        iso = tag('ISOSpeedRatings')
        orientation = int(tag('Orientation')) if tag('Orientation') is not None else None
        stats.update({
            'tiff_width': tag('ImageWidth'),
            'tiff_height': tag('ImageLength'),
            'tiff_bits_per_sample': tag('BitsPerSample'),
            'tiff_photometric': int(tag('PhotometricInterpretation')),
            'tiff_orientation': orientation,
            'tiff_orientation_valid': orientation in range(1, 9),
            'tiff_exposure_seconds': tiff_seconds,
            'tiff_iso': iso,
            'tiff_exposure_matches_camera_result': tiff_seconds is not None and math.isclose(tiff_seconds, result['android.sensor.exposureTime'] / 1e9, abs_tol=1e-12),
            'tiff_iso_matches_camera_result': iso == result['android.sensor.sensitivity'],
        })
    stats.update({
        'filename': str(path),
        'bytes': path.stat().st_size,
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'requested_exposure_time_ns': metadata['plan']['requested_exposure_time_ns'],
        'actual_exposure_time_ns': result['android.sensor.exposureTime'],
        'requested_iso': metadata['plan']['requested_iso'],
        'actual_iso': result['android.sensor.sensitivity'],
        'sensor_timestamp_ns': metadata['sensor_timestamp_ns'],
        'capture_started_timestamp_ns': metadata['capture_started_timestamp_ns'],
        'image_result_start_timestamps_match': metadata['sensor_timestamp_ns'] == metadata['capture_started_timestamp_ns'],
        'focus_distance': result.get('android.lens.focusDistance'),
        'awb_lock': result.get('android.control.awbLock'),
        'awb_state': result.get('android.control.awbState'),
        'color_gains': result.get('android.colorCorrection.gains'),
        'ois_mode': result.get('android.lens.opticalStabilizationMode'),
        'frame_duration_ns': result.get('android.sensor.frameDuration'),
        'rolling_shutter_skew_ns': result.get('android.sensor.rollingShutterSkew'),
        'dng_write_duration_ns': metadata['dng_write_duration_ns'],
    })
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contact-sheet-run', default='main-bracket-valid-orientation',
                        help='Run directory whose three derived previews form the contact sheet')
    args = parser.parse_args()
    report = {
        'software': {'rawpy': rawpy.__version__, 'libraw': list(rawpy.libraw_version),
                     'numpy': np.__version__, 'tifffile': tifffile.__version__},
        'preview_parameters': {'use_camera_wb': True, 'no_auto_bright': True,
                               'output_bps': 8, 'half_size': True,
                               'thumbnail_max_size': [1000, 750], 'jpeg_quality': 90},
        'limitations': ['Previews are deterministic demosaiced derivatives, not source captures.',
                        'Clipping percentages describe raw samples in this scene, not measured dynamic range.',
                        'No alignment, HDR merge or shadow SNR measurement was performed.'],
        'runs': [],
    }
    for folder in sorted(args.root.iterdir()):
        if not folder.is_dir() or not (folder / 'run.json').exists():
            continue
        run = json.loads((folder / 'run.json').read_text())
        frames = [inspect(p) for p in sorted(folder.glob('frame-*.dng'))]
        entry = {'directory': folder.name, 'camera_id': run['camera_id'], 'mode': run['mode'],
                 'state': run['state'], 'expected_frames': run['expected_frames'],
                 'saved_frames': len(frames), 'frames': frames}
        entry['source_frame_count_matches_expected'] = len(frames) == run['expected_frames']
        if len(frames) == 3:
            base = frames[1]['actual_exposure_time_ns']
            for f in frames:
                f['actual_ev_relative_to_middle'] = math.log2(f['actual_exposure_time_ns'] / base)
            entry['iso_constant'] = len({f['actual_iso'] for f in frames}) == 1
            entry['focus_constant'] = len({f['focus_distance'] for f in frames}) == 1
            entry['awb_gains_constant'] = len({json.dumps(f['color_gains'], sort_keys=True) for f in frames}) == 1
            entry['sensor_start_gaps_ns'] = [frames[i + 1]['sensor_timestamp_ns'] - frames[i]['sensor_timestamp_ns'] for i in range(2)]
        report['runs'].append(entry)
        print(folder.name, 'decoded', len(frames), 'DNGs', flush=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    bracket = args.root / args.contact_sheet_run
    previews = sorted(bracket.glob('frame-*-decoded-preview.jpg'))
    if len(previews) == 3:
        canvas = Image.new('RGB', (1800, 490), 'white')
        draw = ImageDraw.Draw(canvas)
        for i, p in enumerate(previews):
            im = Image.open(p)
            im.thumbnail((590, 450))
            canvas.paste(im, (600 * i, 35))
            draw.text((600 * i + 10, 10), ['-2 EV', '0 EV', '+2 EV'][i], fill='black')
        canvas.save(args.root / 'main-bracket-contact-sheet.jpg', quality=92)
    print('Saved inspection report:', args.output)


if __name__ == '__main__':
    main()
