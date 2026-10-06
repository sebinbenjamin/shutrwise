#!/usr/bin/env python3
"""THROWAWAY: fixed-exposure RAW bracket experiment, not a production HDR engine."""
import argparse
import json
import platform
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from file_integrity import sha256_file  # noqa: E402

import numpy as np
import PIL
from PIL import Image, ImageDraw
import rawpy
import tifffile

from raw_common import safe_ratio, normalize_raw, merge_bracket, CONSISTENCY_INDICES, ROIS, roi_slices

LIMITS = [
    "S22 only; no Samsung baseline or S25 measurements.",
    "All alternatives come from the same quartet; independent strategy capture latency is not measured.",
    "Nominal shutter times ISO normalization does not calibrate actual analogue gain across ISO values.",
    "No calibrated scene irradiance, chart, independent noise estimate, SNR or sensor dynamic-range measurement.",
    "Merges are unaligned: no global-translation or local-motion deghosting; OIS, flicker, movement and processing may produce disagreement.",
    "Half-resolution white-balanced sensor RGB is not a calibrated sRGB color conversion or a Lightroom rendering.",
    "RAW is HAL-delivered data; an unprocessed ADC signal is not established.",
]


def sha(path):
    return sha256_file(path)


def rgb_cells(mosaic, pattern):
    planes = {int(pattern[y, x]): mosaic[y::2, x::2] for y in range(2) for x in range(2)}
    return np.stack([planes[0], (planes[1] + planes[3]) / 2, planes[2]], axis=-1)


def box8(a):
    h, w = (np.array(a.shape[:2]) // 8) * 8
    return a[:h, :w].reshape(h//8, 8, w//8, 8).mean(axis=(1, 3))


def phase(a, b):
    # Integer phase-correlation diagnostic at 8 Bayer cells / 16 sensor pixels.
    aa, bb = box8(a), box8(b)
    window = np.hanning(aa.shape[0])[:, None] * np.hanning(aa.shape[1])[None, :]
    fa, fb = np.fft.fft2((aa-aa.mean())*window), np.fft.fft2((bb-bb.mean())*window)
    cross = fa*np.conj(fb)
    corr = np.fft.ifft2(cross/np.maximum(abs(cross), 1e-12)).real
    peak = np.unravel_index(np.argmax(corr), corr.shape)
    shift = [int(v if v <= n//2 else v-n)*16 for v,n in zip(peak,corr.shape)]
    return {"integer_shift_to_reference_raw_pixels_yx": shift,
            "diagnostic_resolution_raw_pixels": 16, "peak": float(corr[peak]),
            "note": "Coarse diagnostic only; zero does not rule out subpixel shift or local motion."}


def display(rgb, gain=2.0):
    # Fixed channelwise global Reinhard, then standard sRGB transfer function.
    x = np.maximum(rgb*gain, 0)
    x = x/(1+x)
    x = np.where(x <= .0031308, 12.92*x, 1.055*x**(1/2.4)-.055)
    return np.uint8(np.rint(np.clip(x,0,1)*255))


def stats(a):
    return {"min": float(a.min()), "median": float(np.median(a)),
            "p95": float(np.quantile(a,.95)), "max": float(a.max())}


def pair_image(a,b,path,label_a="Middle RAW, bounded settings",label_b="Three-RAW merge",third=None):
    image = Image.new("RGB",(a.width+b.width+third.width,a.height+38),(24,24,24))
    image.paste(a,(0,38)); image.paste(b,(a.width,38))
    draw=ImageDraw.Draw(image); draw.text((12,12),label_a,fill="white");draw.text((a.width+12,12),label_b,fill="white")
    image.paste(third,(a.width+b.width,38));draw.text((a.width+b.width+12,12),"Longer / lower ISO single",fill="white")
    image.save(path)


def run_sequence(source, output):
    begin=time.perf_counter(); output.mkdir()
    x=[]; results=[]; refs=[]; clipped=[]; near=[]; raw_metadata=[]
    for i in range(4):
        path=source/f"frame-{i}.dng"
        result_path=source/f"frame-{i}-result.json"
        result=json.loads(result_path.read_text())["result"];results.append(result)
        with rawpy.imread(str(path)) as r:
            mosaic=r.raw_image_visible.copy()
            pattern=r.raw_pattern.copy()
            colors=r.raw_colors_visible.copy()
            white=float(r.white_level)
            normalized=normalize_raw(mosaic,colors,r.black_level_per_channel,white)
            x.append(normalized);clipped.append(mosaic>=white);near.append(normalized>=.98)
            raw_metadata.append({"dimensions_yx":list(mosaic.shape),"white_level":white,
                                 "black_per_channel":r.black_level_per_channel,
                                 "pattern":pattern.tolist(),"color_description":r.color_desc.decode()})
        refs.append({"dng":str(path),"sha256":sha(path),"bytes":path.stat().st_size,
                     "result_sha256":sha(result_path)})
    decoded_seconds=time.perf_counter()-begin
    # Structural RAW layout must match across the quartet; per-frame black-level
    # calibration may legitimately differ (measured: dark-condition front and
    # ultrawide singles carry black 64 while their bracket frames carry 65).
    # Each frame is normalized by its own black level, so the math stays per-frame.
    structural=[{k:m[k] for k in ("dimensions_yx","white_level","pattern","color_description")} for m in raw_metadata]
    assert all(m==structural[1] for m in structural), \
        "Quartet must share dimensions, white level, CFA pattern and color description"
    uniform_black=all(m["black_per_channel"]==raw_metadata[0]["black_per_channel"] for m in raw_metadata)
    times=np.array([r["android.sensor.exposureTime"] for r in results],dtype=float)
    isos=np.array([r["android.sensor.sensitivity"] for r in results],dtype=float)
    assert max(isos[:3])==min(isos[:3]), "This prototype assumes fixed actual ISO within the three-frame bracket"
    relative=times*isos/(times[1]*isos[1])
    radiance, weights, sumw, fallback, merged = merge_bracket(x,relative)
    original_radiance=[a.copy() for a in radiance]
    wb=results[1]["android.colorCorrection.gains"]
    gains=np.array([wb["red"],(wb["green_even"]+wb["green_odd"])/2,wb["blue"]],dtype=np.float32)
    # Exposure-weighted average; rolloff protects near-white samples before RGB conversion.
    fractions=[np.divide(w,sumw,out=np.zeros_like(w),where=~fallback) for w in weights]
    baseline=radiance[1]
    baseline_rgb=rgb_cells(baseline,pattern)*gains
    merge_rgb=rgb_cells(merged,pattern)*gains
    long_rgb=rgb_cells(radiance[3],pattern)*gains
    np.save(output/"single-linear-mosaic.npy",baseline)
    np.save(output/"merge-linear-mosaic.npy",merged)
    np.save(output/"long-single-linear-mosaic.npy",radiance[3])
    tifffile.imwrite(output/"single-linear-sensor-rgb-float32.tif",baseline_rgb,photometric="rgb")
    tifffile.imwrite(output/"merge-linear-sensor-rgb-float32.tif",merge_rgb,photometric="rgb")
    tifffile.imwrite(output/"long-single-linear-sensor-rgb-float32.tif",long_rgb,photometric="rgb")
    mask=np.uint8(clipped[1])+np.uint8(fallback)*2+np.uint8(near[1]&(weights[0]>0))*4
    Image.fromarray(mask).save(output/"raw-mask-bits.png")
    midpoint=baseline_rgb[...,1]
    consistency=[]
    for i in CONSISTENCY_INDICES:
        cells=rgb_cells(original_radiance[i],pattern)[...,1]
        # Smooth fixed8x8 cell boxes, select jointly usable channels, not noise statistics.
        b,c=box8(midpoint),box8(cells)
        max_signal=box8(rgb_cells(x[i],pattern)[...,1])
        valid=(b>.03)&(b<.20)&(max_signal<.75)&(c>0)
        ratios=c[valid]/b[valid]
        residuals={}
        for tag,array in [("before",original_radiance[i]),("after",radiance[i])]:
            green=rgb_cells(array,pattern)[::4,::4,1]
            ref=midpoint[::4,::4]
            good=(ref>.05)&(ref<.20)&np.isfinite(green)&(green>0)
            residuals[tag]={"median_abs_exposure_normalized_green_difference":float(np.median(abs(green[good]-ref[good]))),
                            "sample_count":int(good.sum()),"note":"Radiometric/geometry residual, not an independent noise or SNR measure"}
        consistency.append({"source_frame":i,"green_box_ratio_to_middle_p10_p50_p90":np.quantile(ratios,[.1,.5,.9]).tolist(),
                            "valid_box_count":int(valid.sum()),"alignment":phase(midpoint,cells),"residuals":residuals})
    previews=[]
    for name,rgb in [("single",baseline_rgb),("merge",merge_rgb),("long-single",long_rgb)]:
        rendered=Image.fromarray(display(rgb))
        rendered.save(output/f"{name}-preview.png")
        small=rendered.copy();small.thumbnail((1000,750));previews.append(small)
    pair_image(previews[0],previews[1],output/"comparison.png",third=previews[2])
    roi_metrics={}
    for name,frac in ROIS.items():
        sl=roi_slices(frac,baseline_rgb.shape); raw_sl=roi_slices(frac,baseline.shape)
        a,b,c=baseline_rgb[sl],merge_rgb[sl],long_rgb[sl]
        a_img,b_img=Image.fromarray(display(a)),Image.fromarray(display(b))
        # Explicit shadow lift, fixed gain16 to BOTH; no per-image normalization.
        if name=="dark_lower_left":
            a_img,b_img=Image.fromarray(display(a,16)),Image.fromarray(display(b,16))
        c_img=Image.fromarray(display(c,16 if name=="dark_lower_left" else 2))
        pair_image(a_img,b_img,output/f"crop-{name}.png",third=c_img)
        roi_metrics[name]={"normalized_rectangle_xyxy":frac,"display_gain":16 if name=="dark_lower_left" else 2,
                           "single_green_radiance":stats(a[...,1]),"merge_green_radiance":stats(b[...,1]),
                           "long_single_green_radiance":stats(c[...,1]),
                           "long_single_to_middle_green_median_ratio":safe_ratio(np.median(c[...,1]),np.median(a[...,1])),
                           "sensor_rgb_absolute_difference_median":float(np.median(abs(a-b))),
                           "middle_raw_clipped_fraction":float(clipped[1][raw_sl].mean()),
                           "shortest_raw_clipped_fraction":float(clipped[0][raw_sl].mean()),
                           "mean_merge_weight_fractions": [float(w[raw_sl].mean()) for w in fractions]}
    elapsed=time.perf_counter()-begin
    metrics={"run":source.name,"inputs":refs,"raw_metadata":raw_metadata[1],
             "quartet_black_level_per_frame":[m["black_per_channel"] for m in raw_metadata],
             "uniform_black_level_across_quartet":uniform_black,
             "actual_exposure_ns":times.astype(int).tolist(),"actual_iso":isos.astype(int).tolist(),
             "relative_exposure":relative.tolist(),"summed_bracket_integration_ms":float(sum(times[:3])/1e6),
             "quartet_integration_ms":float(sum(times)/1e6),"long_single_integration_ms":float(times[3]/1e6),
             "middle_integration_ms":float(times[1]/1e6),"bracket_to_long_single_integration_ratio":float(sum(times[:3])/times[3]),
             "source_bracket_bytes":sum(i["bytes"] for i in refs[:3]),"source_middle_bytes":refs[1]["bytes"],
             "source_long_single_bytes":refs[3]["bytes"],"long_single_nominal_product_ratio_to_middle":float(relative[3]),
             "processing_seconds_decode_merge_render_save":elapsed,"decode_seconds":decoded_seconds,
             "source_raw_clipped_fraction": [float(a.mean()) for a in clipped],
             "source_raw_near_white_fraction": [float(a.mean()) for a in near],
             "all_frames_near_white_fallback_fraction":float(fallback.mean()),
             "middle_near_white_short_usable_fraction":float((near[1]&~near[0]).mean()),
             "middle_clipped_short_usable_sample_count":int((clipped[1]&~near[0]).sum()),
             "weighted_middle_clipped_short_usable_sample_count":int((clipped[1]&(weights[0]>0)).sum()),
             "alignment":{"method":"none"},
             "mean_merge_weight_fractions": [float(a.mean()) for a in fractions],
             "radiometric_consistency":consistency,"roi_metrics":roi_metrics,
             "white_balance_rgb_gains":gains.tolist(),"focus_diopters":[r["android.lens.focusDistance"] for r in results],
             "ois_modes":[r["android.lens.opticalStabilizationMode"] for r in results],"limits":LIMITS}
    (output/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    return metrics


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True,type=Path);p.add_argument("--output",required=True,type=Path)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    metrics=[run_sequence(d,args.output/d.name) for d in sorted(args.source.glob("control-*")) if d.is_dir()]
    assert len(metrics)==3
    summary={"software":{"python":platform.python_version(),"numpy":np.__version__,"rawpy":rawpy.__version__,"LibRaw":rawpy.libraw_version,"Pillow":PIL.__version__,"tifffile":tifffile.__version__},
             "source_script_sha256":sha(Path(__file__)),"method":"Native CFA exposure-weighted radiance with near-white rolloff; no alignment",
             "method_parameters":{"near_white_signal":.98,"rolloff_start_signal":.80,"default_display_gain":2,"shadow_display_gain":16,"same_bayer_cell_green":"mean of two greens"},
             "raw_mask_bits":{"1":"middle at raw white level","2":"all frames at or above .98 signal; shortest fallback","4":"middle >=.98 and shortest <.98"},
             "limits":LIMITS,"elapsed_seconds":time.perf_counter()-start,"runs":metrics}
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    manifest=[{"path":str(d.relative_to(args.output)),"bytes":d.stat().st_size,"sha256":sha(d)} for d in sorted(args.output.rglob("*")) if d.is_file()]
    (args.output/"artifact-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"output":str(args.output),"seconds":summary["elapsed_seconds"],"runs":[{"run":m["run"],"clip":m["source_raw_clipped_fraction"],"ratios":m["radiometric_consistency"],"seconds":m["processing_seconds_decode_merge_render_save"]} for m in metrics]},indent=2))


if __name__=="__main__":main()
