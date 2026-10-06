#!/usr/bin/env python3
"""Independent numerical/master/render verification; no scene-quality scores."""
# Deliberately self-contained: an independent check must not share helpers
# with the analysis pipeline it verifies.
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
import rawpy,tifffile

def cells(x,p):
 planes={int(p[y,z]):x[y::2,z::2] for y in range(2) for z in range(2)}
 return np.stack([planes[0],(planes[1]+planes[3])/2,planes[2]],axis=-1)
def display(x,gain=2):
 x=np.maximum(x*gain,0);x=x/(1+x);x=np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)
 return np.uint8(np.rint(np.clip(x,0,1)*255))
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('processing',type=Path);p.add_argument('output',type=Path);a=p.parse_args();out={}
for d in sorted(a.source.glob('control-*')):
 if not d.is_dir():continue
 norm=[];iso=[];times=[];clipped=[];source_hashes=[]
 for i in range(4):
  path=d/f'frame-{i}.dng';meta=json.loads((d/f'frame-{i}-result.json').read_text())['result'];iso.append(meta['android.sensor.sensitivity']);times.append(meta['android.sensor.exposureTime']);source_hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
  with rawpy.imread(str(path)) as raw:
   x=raw.raw_image_visible.copy();black=np.asarray(raw.black_level_per_channel,dtype=np.float32)[raw.raw_colors_visible];norm.append((x.astype(np.float32)-black)/(raw.white_level-black));clipped.append(x>=raw.white_level);pattern=raw.raw_pattern.copy()
 relative=np.asarray(times,dtype=float)*np.asarray(iso)/(times[1]*iso[1]);weights=[float(e)*np.clip((.98-x)/.18,0,1) for x,e in zip(norm[:3],relative[:3])];total=sum(weights)
 expected_merge=np.divide(sum(w*x/e for w,x,e in zip(weights,norm,relative)),total,out=(norm[0]/relative[0]).copy(),where=total>0)
 wb=meta['android.colorCorrection.gains'];g=np.array([wb['red'],(wb['green_even']+wb['green_odd'])/2,wb['blue']],dtype=np.float32)
 result={'source_sha256':source_hashes,'pipeline_formula_checks':{},'rejected_saturated_positive_weight_count':[int(np.count_nonzero(c&(w>0))) for c,w in zip(clipped[:3],weights)],'all_zero_weights_count':int(np.count_nonzero(total<=0)),'relative_product_to_middle':relative.tolist()}
 for name,expected in [('single',norm[1]),('long-single',norm[3]/relative[3]),('merge',expected_merge)]:
  q=a.processing/d.name;master=np.load(q/f'{name}-linear-mosaic.npy');rgb=tifffile.imread(q/f'{name}-linear-sensor-rgb-float32.tif');check={'all_master_finite':bool(np.isfinite(master).all()),'master_max_abs_formula_error':float(np.max(np.abs(master-expected))),'rgb_max_abs_formula_error':float(np.max(np.abs(rgb-cells(master,pattern)*g))),'preview_exact_same_transform':bool(np.array_equal(np.asarray(Image.open(q/f'{name}-preview.png')),display(rgb)))}
  assert check['all_master_finite'] and check['master_max_abs_formula_error']<1e-6 and check['rgb_max_abs_formula_error']==0 and check['preview_exact_same_transform'],check
  result['pipeline_formula_checks'][name]=check
 assert all(v==0 for v in result['rejected_saturated_positive_weight_count'])
 result['all_zero_weights_handling']='Shortest-source fallback checked by full formula reconstruction; these pixels cannot recover highlights clipped in every source.'
 out[d.name]=result
print(json.dumps(out,indent=2));a.output.write_text(json.dumps(out,indent=2)+'\n')
