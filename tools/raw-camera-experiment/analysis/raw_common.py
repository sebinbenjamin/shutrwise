#!/usr/bin/env python3
"""Shared RAW-plane helpers for the analysis pipeline.

verify_long_control.py deliberately re-implements its formulas instead of
importing from here: an independent check must not share code with the
pipeline it verifies.
"""
import numpy as np

# One geometric ROI table, fractional (x0, y0, x1, y1). The archived
# lighting-pair experiment used scene-specific names for the same
# coordinates: towel -> center_detail, bright_wall -> upper_left,
# right_metal -> right_edge.
ROIS = {
    "center_detail": (.42, .45, .63, .80),
    "dark_lower_left": (.025, .66, .175, .90),
    "upper_left": (.02, .05, .12, .22),
    "right_edge": (.93, .42, .98, .62),
}

# A control quartet: frames 0-2 are the fixed-ISO -2/0/+2 EV bracket,
# frame 3 is the longer/lower-ISO single. MainActivity.java is the
# behavioural source of truth for this layout.
BRACKET_INDICES = (0, 1, 2)
MIDDLE_INDEX = 1
LONG_SINGLE_INDEX = 3
CONSISTENCY_INDICES = (0, 2, 3)  # non-middle frames compared against the middle
AUDIT_PAIRS = ((0, 1), (2, 1), (3, 1), (2, 3))  # (candidate, reference) ratio/phase checks


def roi_slices(frac, shape):
    """Row/column slices for a fractional ROI; round() matches reported pixel_bounds."""
    h, w = shape[:2]
    x0, y0, x1, y1 = frac
    return slice(round(y0 * h), round(y1 * h)), slice(round(x0 * w), round(x1 * w))


def quartile_stats(v):
    return {'count': int(v.size),
            'p10_p50_p90': np.percentile(v, [10, 50, 90]).tolist()} if v.size else {'count': 0}


def bayer_green(signal, pattern):
    """Mean of the two green CFA planes, positions read from the sensor pattern."""
    planes = [signal[y::2, z::2] for y in range(2) for z in range(2)
              if int(pattern[y, z]) in (1, 3)]
    assert len(planes) == 2, 'Expected two green planes in the advertised Bayer mosaic'
    return (planes[0] + planes[1]) / 2


def phase_shift(a, b):
    # Green half-res Bayer-cell mean, common log floor, taper, phase-only peak.
    def prep(x):
        y = np.log(np.maximum(x, 8)).astype(np.float32)
        y -= y.mean()
        y *= np.outer(np.hanning(y.shape[0]), np.hanning(y.shape[1])).astype(np.float32)
        return np.fft.rfft2(y)
    aa, bb = prep(a), prep(b)
    cross = aa * np.conj(bb)
    cross /= np.maximum(np.abs(cross), 1e-12)
    cc = np.fft.irfft2(cross, s=a.shape).real
    peak = np.unravel_index(np.argmax(cc), cc.shape)
    offsets = []
    for axis, p in enumerate(peak):
        n = cc.shape[axis]
        left = list(peak)
        right = list(peak)
        left[axis] = (p - 1) % n
        right[axis] = (p + 1) % n
        l, c, r = cc[tuple(left)], cc[peak], cc[tuple(right)]
        den = l - 2 * c + r
        delta = float(.5 * (l - r) / den) if abs(den) > 1e-12 else 0
        offsets.append(float(p if p <= n // 2 else p - n) + delta)
    return {'dy_dx_raw_pixels': [x * 2 for x in offsets],
            'peak': float(cc[peak]),
            'meaning': 'Shift to align second image with middle, phase-only log-green '
                       'diagnostic; not registration applied or proof of local alignment.'}


def normalize_raw(mosaic, colors, black_levels, white):
    black = np.asarray(black_levels, dtype=np.float32)[colors]
    return (mosaic.astype(np.float32) - black) / (white - black)


def merge_bracket(samples, relative):
    radiance = [a / float(e) for a, e in zip(samples, relative)]
    weights = [np.where(np.isfinite(a), float(e) * np.clip((.98-a)/(.98-.80), 0, 1), 0)
               for a, e in zip(samples[:3], relative[:3])]
    sumw = sum(weights)
    fallback = sumw <= 0
    numerator = sum(w * np.nan_to_num(a, nan=0) for w, a in zip(weights, radiance))
    values = np.where(np.isfinite(radiance[0]), radiance[0], radiance[1])
    merged = np.divide(numerator, sumw, out=values.copy(), where=~fallback)
    assert np.isfinite(merged).all()
    return radiance, weights, sumw, fallback, merged


def safe_ratio(numerator, denominator):
    numerator, denominator = float(numerator), float(denominator)
    if denominator == 0 or not np.isfinite([numerator, denominator]).all():
        return None
    value = numerator / denominator
    return value if np.isfinite(value) else None
