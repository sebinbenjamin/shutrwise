#!/usr/bin/env python3
"""Independent source support/consistency checks; no noise or DR estimates."""
import argparse, hashlib, json, platform
from pathlib import Path
import numpy as np
import rawpy
ROIS = {'towel':(.42,.45,.63,.80),'dark_lower_left':(.025,.66,.175,.90),'bright_wall':(.02,.05,.12,.22),'right_metal':(.93,.42,.98,.62)}
def stats(v):
    return {'count':int(v.size), 'p10_p50_p90':np.percentile(v,[10,50,90]).tolist()} if v.size else {'count':0}
def phase_shift(a,b):
    # Green half-res Bayer-cell mean, common log floor, taper, phase-only peak.
    def prep(x):
        y=np.log(np.maximum(x,8)).astype(np.float32)
        y-=y.mean(); y*=np.outer(np.hanning(y.shape[0]),np.hanning(y.shape[1])).astype(np.float32)
        return np.fft.rfft2(y)
    aa,bb=prep(a),prep(b); cross=aa*np.conj(bb); cross/=np.maximum(np.abs(cross),1e-12)
    cc=np.fft.irfft2(cross,s=a.shape).real
    peak=np.unravel_index(np.argmax(cc),cc.shape); offsets=[]
    for axis,p in enumerate(peak):
        n=cc.shape[axis]; left=list(peak); right=list(peak); left[axis]=(p-1)%n;right[axis]=(p+1)%n
        l,c,r=cc[tuple(left)],cc[peak],cc[tuple(right)];den=l-2*c+r
        delta=float(.5*(l-r)/den) if abs(den)>1e-12 else 0
        offsets.append(float(p if p<=n//2 else p-n)+delta)
    return {'dy_dx_raw_pixels':[x*2 for x in offsets], 'peak':float(cc[peak]),'meaning':'Shift to align second image with middle, phase-only log-green diagnostic; not registration applied or proof of local alignment.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
    out={'protocol':'protocol.md','versions':{'python':platform.python_version(),'numpy':np.__version__,'rawpy':rawpy.__version__},'rois_fractional':ROIS,'runs':{}}
    for folder in sorted(args.source.glob('main-bracket-*')):
        if not folder.is_dir():continue
        raw,signals,infos,greens=[],[],[],[]
        for i in range(3):
            p=folder/f'frame-{i}.dng';meta=json.loads((folder/f'frame-{i}-result.json').read_text())['result']
            with rawpy.imread(str(p)) as r:
                x=r.raw_image.copy();colors=r.raw_colors.copy();black=np.asarray(r.black_level_per_channel)[colors]; s=x.astype(np.float32)-black
                white=int(r.white_level);pattern=r.raw_pattern.tolist();h,w=x.shape
                green=(s[0::2,0::2]+s[1::2,1::2])/2
                # Explicit full sensor axes for ROI mapping and agreement with probe's original whole-frame stats.
                infos.append({'filename':str(p.relative_to(args.source)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'exposure_ns':meta['android.sensor.exposureTime'],'iso':meta['android.sensor.sensitivity'],'white':white,'black':r.black_level_per_channel,'cfa':pattern,'shape':[h,w],'raw_crop':str(r.sizes),'clip_percent':float(np.mean(x>=white)*100),'signal_codes':stats(s.ravel()),'ois':meta.get('android.lens.opticalStabilizationMode'),'black_lock':meta.get('android.blackLevel.lock')})
                raw.append(x);signals.append(s);greens.append(green)
        exposures=np.asarray([f['exposure_ns']*f['iso'] for f in infos],dtype=np.float64); rel=exposures/exposures[1]
        masks=[];ratios=[]
        for i in [0,2]:
            ref=signals[1]; si=signals[i];white=infos[i]['white']-infos[i]['black'][0]
            low,high=(64,600) if i==0 else (16,150)
            mask=(ref>=low)&(ref<=high)&(si>=8)&(si<white*.80)
            ratio=si/(np.maximum(ref,1)*rel[i]);masks.append(mask);ratios.append(ratio)
        item={'frames':infos,'integration_budget_ratio_to_middle':float(sum(rel)),'relative_exposure':rel.tolist(),'pair_checks':{},'rois':{}}
        for k,i in enumerate([0,2]):
            tiles=[]
            for yy in range(6):
                for xx in range(8):
                    sl=(slice(yy*h//6,(yy+1)*h//6),slice(xx*w//8,(xx+1)*w//8));v=ratios[k][sl][masks[k][sl]]
                    if v.size>=100:tiles.append({'tile_yx':[yy,xx],**stats(v)})
            item['pair_checks'][str(i)]={'same_coordinate_ratio':stats(ratios[k][masks[k]]),'tile_ratios':tiles,'tile_median_range':stats(np.array([t['p10_p50_p90'][1] for t in tiles])),'phase':phase_shift(greens[1],greens[i]/rel[i])}
        for name,(x0,y0,x1,y1) in ROIS.items():
            sl=(slice(round(y0*h),round(y1*h)),slice(round(x0*w),round(x1*w)))
            clip=raw[1][sl]>=infos[1]['white']; short_good=raw[0][sl]<infos[0]['white'];long_good=raw[2][sl]<(infos[2]['black'][0]+.98*(infos[2]['white']-infos[2]['black'][0]))
            item['rois'][name]={'pixel_bounds':[round(x0*w),round(y0*h),round(x1*w),round(y1*h)],'source_signal_codes':[stats(s[sl].ravel()) for s in signals],'source_clip_percent':[float(np.mean(x[sl]>=inf['white'])*100) for x,inf in zip(raw,infos)],'middle_clip_count':int(clip.sum()),'middle_clip_short_unsaturated_count':int((clip&short_good).sum()),'long_below98pct_percent':float(np.mean(long_good)*100),'normalized_ratios':{str(i):stats(ratios[k][sl][masks[k][sl]]) for k,i in enumerate([0,2])}}
        clip=raw[1]>=infos[1]['white'];shortgood=raw[0]<infos[0]['white']
        item['whole_frame_potential_highlight_support']={'middle_clip_count':int(clip.sum()),'short_unsaturated_at_middle_clip_count':int((clip&shortgood).sum()),'important_subject_selection':False,'alignment_assumption':'same sensor coordinates'}
        out['runs'][folder.name]=item
        print(folder.name, item['pair_checks']['0']['same_coordinate_ratio'],item['pair_checks']['2']['same_coordinate_ratio'],flush=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
