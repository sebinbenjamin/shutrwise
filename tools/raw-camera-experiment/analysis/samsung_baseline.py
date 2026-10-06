#!/usr/bin/env python3
"""Research-only Samsung delivered-photo/RAW comparison, not a camera pipeline."""
import argparse,json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import rawpy,tifffile
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from file_integrity import manifest,write_json


def render(rgb,gain):
    x=np.maximum(rgb*gain,0);x=x/(1+x)
    x=np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)
    return Image.fromarray(np.uint8(np.rint(np.clip(x,0,1)*255)))


def resize_linear(rgb,size):
    return np.stack([np.asarray(Image.fromarray(rgb[...,c]).resize(size,Image.Resampling.BOX)) for c in range(3)],axis=-1)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    camera=a.source/'custom/normal/camera-0';runs=sorted((camera/'captures').glob('control-*'))
    assert len(runs)==3
    roles=json.loads((a.source/'samsung-captures.json').read_text())
    pros=sorted((a.source/'samsung').glob('*.dng'));assert len(pros)==3
    first=json.loads((runs[0]/'frame-1-result.json').read_text())['result']
    g=first['android.colorCorrection.gains'];wb=[g['red'],g['green_even'],g['blue'],g['green_odd']]
    records=[]
    for n,(run,pro,photo_name) in enumerate(zip(runs,pros,roles['photo']),1):
        row=[];names=['Samsung Photo delivered','Samsung Pro delivered','Samsung Pro DNG','Custom metered RAW','Custom longer RAW','Custom bracket merge']
        for path in [a.source/'samsung'/photo_name,pro.with_suffix('.jpg')]:
            with Image.open(path) as im:row.append(im.convert('RGB').resize((2000,1500),Image.Resampling.LANCZOS))
        linear=[]
        for name,path in [('pro',pro),('middle',run/'frame-1.dng'),('long',run/'frame-3.dng')]:
            with rawpy.imread(str(path)) as raw:
                rgb=raw.postprocess(output_bps=16,gamma=(1,1),no_auto_bright=True,user_wb=wb,
                                    output_color=rawpy.ColorSpace.sRGB,half_size=True,user_flip=0).astype(np.float32)/65535
                rgb=resize_linear(rgb,(2000,1500));linear.append(rgb)
                channels=raw.raw_image_visible
                # LibRaw pads three-channel linear DNGs to four; exclude the unused plane.
                encoded=channels[...,:raw.num_colors] if channels.ndim==3 else channels
                records.append({'repeat':n,'role':name,'file':str(path.relative_to(a.source)),
                                'raw_type':str(raw.raw_type),'raw_shape':list(channels.shape),
                                'encoded_channels':raw.num_colors if channels.ndim==3 else 1,
                                'white':raw.white_level,'encoded_white_clip_pct':float((encoded>=raw.white_level).mean()*100)})
        measured=json.loads((run/'frame-1-result.json').read_text())['result']
        text=measured['android.colorCorrection.transform']['string_value']
        numbers=re.findall(r'(-?\d+)/(\d+)',text);assert len(numbers)==9
        matrix=np.array([int(x)/int(y) for x,y in numbers],dtype=np.float32).reshape(3,3)
        # Names of scientific masters are maintained by compare.py.
        master=camera/'comparison'/run.name/'merge-linear-sensor-rgb-float32.tif'
        merge=tifffile.imread(master)@matrix.T;linear.append(merge)
        reference=linear[1];mask=(reference[...,1]>.03)&(reference[...,1]<.3)
        assert mask.sum()>1000
        target=float(np.median(reference[...,1][mask]));scales=[]
        for name,rgb in zip(['pro','middle','long','merge'],linear):
            med=float(np.median(rgb[...,1][mask]));assert med>0
            scale=target/med;scales.append(scale)
            tifffile.imwrite(a.output/f'repeat-{n:02d}-{name}-linear.tif',rgb,photometric='rgb')
            render(rgb*scale,2).save(a.output/f'repeat-{n:02d}-{name}.png')
            render(rgb*scale,16).save(a.output/f'repeat-{n:02d}-{name}-lift.png')
            row.append(render(rgb*scale,2))
        for lifted in [False,True]:
            panels=row if not lifted else [*row[:2],*[render(rgb*s,16) for rgb,s in zip(linear,scales)]]
            # All sources have native landscape axes; apply the same clockwise display rotation.
            rotated=[im.transpose(Image.Transpose.ROTATE_270) for im in panels]
            canvas=Image.new('RGB',(6*450,640),(25,25,25));draw=ImageDraw.Draw(canvas)
            for i,(im,label) in enumerate(zip(rotated,names)):
                canvas.paste(im.resize((450,600),Image.Resampling.LANCZOS),(i*450,40));draw.text((i*450+8,12),label,fill='white')
            canvas.save(a.output/(f'repeat-{n:02d}-'+('lifted.png' if lifted else 'overview.png')))
        records.append({'repeat':n,'display_scales_pro_middle_long_merge':scales,'mask_pixels':int(mask.sum()),'camera2_merge_color_transform':matrix.tolist()})
    write_json(a.output/'method.json',{'records':records,'fixed_raw_white_balance':wb,
        'raw_development':'LibRaw linear sRGB, no auto brightness, 16-bit, half size; linear Pro DNG resized by area average. Merge uses recorded Camera2 color transform on native float camera-RGB cells.',
        'display':'All RAW variants brightness matched to custom middle green median in its 0.03–0.3 signal mask. Common x/(1+x) tone curve and sRGB encoding, gain 2 or 16. JPEGs delivered unchanged except resize/rotation.',
        'limits':'No alignment, deghosting, calibrated SNR or objective quality scores. Processed Pro RGB clipping and Bayer clipping measure different domains. LibRaw output is bounded; this display test is not maximum highlight recovery. Sequential modes and unmatched metering may confound scene changes. Samsung JPEG EXIF is not multi-frame integration or latency.'})
    write_json(a.output/'manifest.json',manifest(a.output,sorted(a.output.iterdir())))
    print('Saved three six-path comparison boards and method records')


if __name__=='__main__':main()
