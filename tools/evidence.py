#!/usr/bin/env python3
"""Export compact Git evidence indexes, generate report facts, and show offline status."""
import argparse
import json
import math
import shlex
from pathlib import Path
from file_integrity import write_json, verify_manifest

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- BEGIN GENERATED CAMERA FACTS -->'
END = '<!-- END GENERATED CAMERA FACTS -->'


def read(path):
    return json.loads(Path(path).read_text())


def cfa_label(pattern, description):
    if len(pattern)!=2 or any(len(row)!=2 for row in pattern):
        raise ValueError('Expected a 2 by 2 CFA pattern')
    label = ''.join(description[int(i)] for row in pattern for i in row)
    if sorted(label)!=['B','G','G','R']:
        raise ValueError('Expected RGB Bayer letters')
    return label


def export_index(source, device):
    source = Path(source).resolve()
    document = {'version':1,'experiment':source.name,'device':device,
                'source_root':str(source.relative_to(ROOT)),
                'backup':'Large originals and derived files remain local and are covered by owner-managed VM backups.',
                'conditions':{}}
    for folder in sorted(source.iterdir()):
        if not folder.is_dir() or not (folder/'capture-status.json').exists():continue
        capture=read(folder/'capture-status.json')
        analysis={c['camera_id']:c for c in read(folder/'analysis-status.json')['cameras']} if (folder/'analysis-status.json').exists() else {}
        condition={'setup':read(folder/'conditions.json'), 'cameras':[], 'physical':[], 'source_files':[],
                   'cleanup':read(folder/'cleanup.json') if (folder/'cleanup.json').exists() else {'status':'not_recorded'}}
        for camera in capture['cameras']:
            item=dict(camera)
            base_name=('camera-' if camera['directly_listed'] else 'physical-')+camera['camera_id']
            item['log_paths']=[str(p.relative_to(source)) for p in sorted((folder/base_name).glob('*.log'))]
            if camera['camera_id'] in analysis:
                item['analysis_error']=analysis[camera['camera_id']].get('error')
            if not camera['directly_listed']:
                condition['physical'].append(item);continue
            item['analysis_status']=analysis.get(camera['camera_id'],{}).get('status','not_started')
            item['saved_dngs']=sum(r.get('dngs',0) for r in camera.get('runs',[]))
            item['runs']=[]
            base=folder/('camera-'+camera['camera_id'])
            audit=read(base/'source-audit.json').get('runs',{}) if (base/'source-audit.json').exists() else {}
            verification=read(base/'pipeline-verification.json') if (base/'pipeline-verification.json').exists() else {}
            for run in sorted((base/'captures').glob('control-*')):
                if not (run/'run.json').exists():continue
                record=read(run/'run.json')
                frames=audit.get(run.name,{}).get('frames',[])
                values={'name':run.name,'state':record['state'],'raw_size':record.get('raw_size'),
                        'auto_shutter_ns':record.get('baseline_exposure_time_ns'),'auto_iso':record.get('baseline_iso'),
                        'plan':record.get('plan',[]),'frames':[],
                        'controls':audit.get(run.name,{}).get('controls',{}),
                        'verification':verification.get(run.name,{})}
                for frame in frames:
                    values['frames'].append({k:frame[k] for k in ['frame','sha256','bytes','shape','cfa','black_per_channel','white','actual_exposure_ns','actual_iso','white_clip_pct','timestamps_match']})
                metrics_path=base/'comparison'/run.name/'metrics.json'
                if metrics_path.exists():
                    metrics=read(metrics_path)
                    values['color_description']=metrics['raw_metadata']['color_description']
                    values['cfa_label']=cfa_label(metrics['raw_metadata']['pattern'],values['color_description'])
                summary=base/'comparison/summary.json'
                if summary.exists():values['analysis_script_sha256']=read(summary)['source_script_sha256']
                item['runs'].append(values)
            condition['cameras'].append(item)
        path=folder/'source-manifest.json'
        if not path.exists():path=folder/'manifest.json'
        if path.exists():
            condition['source_files']=[f for f in read(path)['files'] if 'captures' in Path(f['path']).parts or 'capabilities' in Path(f['path']).parts or f['path'] in ['conditions.json','capture-status.json']]
        document['conditions'][folder.name]=condition
    return document


def facts(document):
    lines=[START, '', '| Lighting | Camera / facing | RAW / CFA | Middle ms / ISO | Longer single ms / ISO | Bracket / single integration | RAW storage |',
           '| --- | --- | --- | --- | --- | --- | --- |']
    for lighting,condition in sorted(document['conditions'].items()):
        for camera in condition['cameras']:
            for run in camera['runs']:
                frames=run['frames']
                if len(frames)!=4:continue
                middle=frames[1];single=frames[3];shape=middle['shape']
                ratio=sum(f['actual_exposure_ns'] for f in frames[:3])/single['actual_exposure_ns']
                storage=sum(f['bytes'] for f in frames[:3])/single['bytes']
                face={0:'front',1:'back',2:'external'}.get(camera['lens_facing'],'unknown')
                lines.append(f"| {lighting} {run['name']} | {camera['camera_id']} / {face} | {shape[1]} × {shape[0]} / {cfa_label(middle['cfa'],run['color_description'])} | {middle['actual_exposure_ns']/1e6:.3f} / {middle['actual_iso']} | {single['actual_exposure_ns']/1e6:.3f} / {single['actual_iso']} | {ratio:.4f}× | {storage:.2f}× |")
    lines.extend(['', 'Integration is summed sensor exposure, not elapsed capture latency. Paths without four recorded frames are excluded from this table.', ''])
    for lighting, condition in sorted(document['conditions'].items()):
        failed=[p['camera_id'] for p in condition['physical'] if p['status']=='direct_open_failed']
        lines.append(f"{lighting}: physical direct-access failures: {', '.join(failed) or 'none recorded'}.")
    lines.extend(['', '| Lighting / camera / run | Auto ISO → middle ISO | Black bracket → single | Middle / single clipping % | Long shutter clamped | Single / middle nominal product |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for lighting,condition in sorted(document['conditions'].items()):
        for camera in condition['cameras']:
            for run in camera['runs']:
                f=run['frames']
                if len(f)!=4:continue
                middle,single=f[1],f[3]
                product=single['actual_exposure_ns']*single['actual_iso']/(middle['actual_exposure_ns']*middle['actual_iso'])
                clamped=any(p['exposure_clamped'] for p in run['plan'][2:])
                black=f"{middle['black_per_channel']} → {single['black_per_channel']}"
                lines.append(f"| {lighting} / {camera['camera_id']} / {run['name']} | {run['auto_iso']} → {middle['actual_iso']} | {black} | {middle['white_clip_pct']:.5f} / {single['white_clip_pct']:.5f} | {clamped} | {product:.6f} |")
    lines.extend(['', '| Lighting / camera / run | Focal lengths mm | Auto shutter ms | Actual bracket EV relative to middle |', '| --- | --- | --- | --- |'])
    for lighting, condition in sorted(document['conditions'].items()):
        for camera in condition['cameras']:
            for run in camera['runs']:
                frames=run['frames']
                if len(frames)!=4:continue
                middle=frames[1]
                spacing=' / '.join(f"{math.log2(f['actual_exposure_ns']*f['actual_iso']/(middle['actual_exposure_ns']*middle['actual_iso'])):+.3f}" for f in frames[:3])
                auto=run.get('auto_shutter_ns')
                lines.append(f"| {lighting} / {camera['camera_id']} / {run['name']} | {camera.get('focal_lengths_mm', 'not recorded')} | {auto/1e6 if auto is not None else 'not recorded'} | {spacing} |")
    lines.extend(['',END]);return '\n'.join(lines)


def update_report(index, report, check=False):
    report=Path(report);text=report.read_text();block=facts(read(index))
    if START not in text or END not in text:raise ValueError('Report needs explicit generated-block markers')
    start=text.index(START);end=text.index(END,start)+len(END)
    updated=text[:start]+block+text[end:]
    if check and updated!=text:raise ValueError('Report facts are stale: '+str(report))
    if not check:report.write_text(updated)


def status(document, verbose=False):
    lines=[document['device']+' — '+document['experiment']]
    for lighting,condition in sorted(document['conditions'].items()):
        lines.append(f"{lighting} cleanup: {condition.get('cleanup',{}).get('ok',condition.get('cleanup',{}).get('status','not_recorded'))}")
        for camera in condition['cameras']:
            count=sum(len(r['frames']) for r in camera['runs'])
            lines.append(f"{lighting} camera {camera['camera_id']}: capture={camera['status']}, analysis={camera['analysis_status']}, saved RAWs={camera.get('saved_dngs','unknown')}, audited RAWs={count}")
        for camera in condition['physical']:
            lines.append(f"{lighting} physical {camera['camera_id']}: {camera['status']} (not counted as a photographed path)")
        if verbose:
            for camera in condition['cameras']+condition['physical']:
                for key in ('error','device_error','analysis_error'):
                    if camera.get(key):lines.append(f"  camera {camera['camera_id']} {key}: {camera[key]}")
                for path in camera.get('log_paths',[]):lines.append('  log: '+document['source_root']+'/'+path)
        failed=[c['camera_id'] for c in condition['cameras'] if c['status'] in ('capture_failed','failed','pending') or (c['status']=='captured' and c['analysis_status']!='verified')]
        if failed:
            fresh=shlex.quote(document['source_root']+'-retry')
            ids=' '.join(shlex.quote(i) for i in failed)
            lines.append(f'Next: preserve this run; choose a fresh unused root, unlock the phone and restore {lighting} lighting. Capture retry: python3 tools/raw-camera-experiment/batch.py --stage capture --lighting {lighting} --output {fresh} --camera-ids {ids}')
            lines.append(f'After capture succeeds: python3 tools/raw-camera-experiment/batch.py --stage analyze --lighting {lighting} --output {fresh} --camera-ids {ids}')
    source=shlex.quote(document['source_root'])
    for lighting in ['normal','dark']:
        condition=document['conditions'].get(lighting)
        if not condition:
            lines.append(f'Next: unlock phone, set {lighting} lighting, then python3 tools/raw-camera-experiment/batch.py --stage capture --lighting {lighting} --output {source}')
        elif any(c['status']=='captured' and c['analysis_status']!='verified' for c in condition['cameras']):
            lines.append(f'Next: inspect failed/partial output logs before resuming analysis for {lighting}; existing outputs will not be overwritten.')
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    export=sub.add_parser('index');export.add_argument('source',type=Path);export.add_argument('--device',required=True);export.add_argument('--output',type=Path,required=True)
    render=sub.add_parser('report');render.add_argument('index',type=Path);render.add_argument('report',type=Path);render.add_argument('--check',action='store_true')
    show=sub.add_parser('status');show.add_argument('index',type=Path);show.add_argument('--json',action='store_true');show.add_argument('--verbose',action='store_true');show.add_argument('--source',type=Path,help='Read a current local experiment instead of the saved index; stays offline')
    verify=sub.add_parser('verify');verify.add_argument('index',type=Path);verify.add_argument('--root',type=Path)
    args=p.parse_args()
    if args.action=='index':write_json(args.output,export_index(args.source,args.device))
    elif args.action=='report':update_report(args.index,args.report,args.check)
    elif args.action=='status':
        document=read(args.index)
        if args.source:document=export_index(args.source,document['device'])
        print(json.dumps(document,indent=2) if args.json else status(document,args.verbose))
    else:
        document=read(args.index);root=args.root or ROOT/document['source_root']
        for lighting,condition in document['conditions'].items():verify_manifest(root/lighting,{'files':condition['source_files']})
        print('All indexed source files verified')


if __name__=='__main__':main()
