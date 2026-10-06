#!/usr/bin/env python3
"""Independent four-source control audit; no photon/noise calibration claims."""
import argparse,hashlib,json,platform
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from file_integrity import sha256_file  # noqa: E402
import numpy as np
import rawpy
import tifffile
from raw_common import AUDIT_PAIRS, ROIS, bayer_green, phase_shift, quartile_stats, roi_slices

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();out={'versions':{'python':platform.python_version(),'numpy':np.__version__,'rawpy':rawpy.__version__,'tifffile':tifffile.__version__},'protocol':'protocol.md','rois':ROIS,'runs':{}}
 for d in sorted(a.source.glob('control-*')):
  if not d.is_dir():continue
  arrays=[];signal=[];norm=[];colors=[];green=[];infos=[]
  for i in range(4):
   path=d/f'frame-{i}.dng';doc=json.loads((d/f'frame-{i}-result.json').read_text());r=doc['result'];plan=doc['plan']
   with rawpy.imread(str(path)) as raw:
    x=raw.raw_image_visible.copy();c=raw.raw_colors_visible.copy();b=np.asarray(raw.black_level_per_channel,dtype=np.float32)[c];s=x.astype(np.float32)-b;n=s/(raw.white_level-b)
    info={'frame':i,'sha256':sha256_file(path),'bytes':path.stat().st_size,'shape':list(x.shape),'cfa':raw.raw_pattern.tolist(),'black_per_channel':raw.black_level_per_channel,'white':raw.white_level,'actual_exposure_ns':r['android.sensor.exposureTime'],'actual_iso':r['android.sensor.sensitivity'],'requested_exposure_ns':plan['requested_exposure_time_ns'],'requested_iso':plan['requested_iso'],'dynamic_black':r.get('android.sensor.dynamicBlackLevel'),'dynamic_white':r.get('android.sensor.dynamicWhiteLevel'),'focus_diopters':r.get('android.lens.focusDistance'),'awb_lock':r.get('android.control.awbLock'),'wb_gains':r.get('android.colorCorrection.gains'),'ois':r.get('android.lens.opticalStabilizationMode'),'timestamp_image':doc['sensor_timestamp_ns'],'timestamp_result':r['android.sensor.timestamp'],'timestamp_start':doc['capture_started_timestamp_ns'],'frame_number':doc['frame_number'],'white_clip_pct':float(np.mean(x>=raw.white_level)*100),'per_cfa_signal_codes':{str(k):quartile_stats(s[c==k]) for k in range(4)}}
    green.append(bayer_green(s, raw.raw_pattern))
    arrays.append(x);signal.append(s);norm.append(n);colors.append(c)
   with tifffile.TiffFile(path) as tf:
    tags=tf.pages[0].tags;exp=tags['ExposureTime'].value;iso=tags['ISOSpeedRatings'].value
    info['tiff_exposure_seconds']=exp[0]/exp[1];info['tiff_iso']=iso;info['orientation']=tags['Orientation'].value
    info['tiff_exposure_matches_actual']=abs(info['tiff_exposure_seconds']-r['android.sensor.exposureTime']/1e9)<1e-12
    info['tiff_iso_matches_actual']=iso==r['android.sensor.sensitivity']
   info['timestamps_match']=info['timestamp_image']==info['timestamp_result']==info['timestamp_start'];infos.append(info)
  product=np.array([f['actual_exposure_ns']*f['actual_iso'] for f in infos],dtype=float);rel=product/product[1];h,w=arrays[1].shape
  pairmetrics={}
  for idx,ref in AUDIT_PAIRS:
   expected=product[idx]/product[ref];rs=signal[ref];si=signal[idx];mask=(rs>=16)&(rs<=150)&(si>=8)&(norm[idx]<.8)&(norm[ref]<.8);ratio=si/(np.maximum(rs,1)*expected)
   key=f'{idx}_to_{ref}'
   pairmetrics[key]={'expected_shutter_iso_ratio':float(expected),'gated_nominal_normalized_ratio':quartile_stats(ratio[mask]),'per_cfa_gated_ratios':{str(k):quartile_stats(ratio[mask&(colors[ref]==k)]) for k in range(4)},'phase':phase_shift(green[ref],green[idx]/expected),'rois':{}}
   for name,(x0,y0,x1,y1) in ROIS.items():
    sl=roi_slices((x0,y0,x1,y1),(h,w))
    pairmetrics[key]['rois'][name]={'gated_ratio':quartile_stats(ratio[sl][mask[sl]]),'reference_signal_codes':quartile_stats(rs[sl].ravel()),'candidate_signal_codes':quartile_stats(si[sl].ravel())}
  item={'frames':infos,'relative_shutter_iso_product':rel.tolist(),'pairs':pairmetrics,'rois':{},'actual_shutter_ns':[f['actual_exposure_ns'] for f in infos],'actual_iso':[f['actual_iso'] for f in infos]}
  for name,(x0,y0,x1,y1) in ROIS.items():
   sl=roi_slices((x0,y0,x1,y1),(h,w))
   item['rois'][name]={'pixel_bounds':[round(x0*w),round(y0*h),round(x1*w),round(y1*h)],'signal_code_distributions':[quartile_stats(s[sl].ravel()) for s in signal],'normalized_code_distributions':[quartile_stats(n[sl].ravel()) for n in norm],'white_clip_pct':[float(np.mean(x[sl]>=f['white'])*100) for x,f in zip(arrays,infos)]}
  item['controls']={'same_long_shutter_2_3':infos[2]['actual_exposure_ns']==infos[3]['actual_exposure_ns'],'bracket_iso_constant':len({f['actual_iso'] for f in infos[:3]})==1,'focus_constant':len({f['focus_diopters'] for f in infos})==1,'awb_locked_all':all(f['awb_lock'] for f in infos),'wb_constant':len({json.dumps(f['wb_gains'],sort_keys=True) for f in infos})==1,'unique_timestamps':len({f['timestamp_result'] for f in infos})==4,'unique_frame_numbers':len({f['frame_number'] for f in infos})==4,'all_timestamp_matches':all(f['timestamps_match'] for f in infos),'all_tiff_exposure_matches':all(f['tiff_exposure_matches_actual'] for f in infos),'all_tiff_iso_matches':all(f['tiff_iso_matches_actual'] for f in infos),'all_actual_shutter_equals_requested':all(f['actual_exposure_ns']==f['requested_exposure_ns'] for f in infos),'same_shape_cfa':all(f['shape']==infos[1]['shape'] and f['cfa']==infos[1]['cfa'] for f in infos)}
  item['integration_ms']={'baseline':infos[1]['actual_exposure_ns']/1e6,'long_lower_iso':infos[3]['actual_exposure_ns']/1e6,'bracket_sum':sum(f['actual_exposure_ns'] for f in infos[:3])/1e6}
  assert all(item['controls'].values()),item['controls']
  out['runs'][d.name]=item;print(d.name,'clips',[f['white_clip_pct'] for f in infos],'long_vs_middle_nominal',rel[3], 'ratio',pairmetrics['3_to_1']['gated_nominal_normalized_ratio'],flush=True)
 a.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
