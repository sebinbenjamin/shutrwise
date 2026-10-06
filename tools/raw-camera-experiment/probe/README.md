# Throwaway Camera2 evidence probe

This branch adds `--mode control`: one four-request burst with fixed focus/AWB.
Frames0–2 use fixed-ISO -2/0/+2 EV; frame3 uses the clamped +2 EV shutter and
inversely reduced, rounded/clamped ISO. Plans log role, clamps and nominal
shutter-times-ISO product; actual results determine analysis. The all-camera
[batch README](../README.md) drives this probe and its analysis.

Question: can the connected Samsung phone expose RAW/manual controls, write an independently decodable DNG, and save three distinct exposures through Camera2?

This is research code on `prototype/s22-camera-probe`, not a production camera app. Native Android code is required to measure Camera2; a browser simulation cannot answer this question. There is no ML, image generation, HDR merging or database. Exported evidence is intentionally preserved.

## Build and run

Requires Java 21, Android platform 36, build-tools 36.0.0 and platform-tools. This workspace's local installations are the defaults in `build.py` and `run.py`. Override `--sdk`, `--java-home` or `--adb` for another machine. Source targets Java 8 bytecode and Android API 28 or later; the manifest targets API 35.

```bash
python3 probe/build.py
python3 probe/run.py --action capabilities --output /path/to/new/capability-directory
python3 probe/run.py --skip-install --action capture --camera-id 0 --mode single --output /path/to/new/single-directory
python3 probe/run.py --skip-install --action capture --camera-id 0 --mode bracket --output /path/to/new/bracket-directory
```

The first run installs the debug APK, grants its declared CAMERA permission through ADB and launches the probe. Later `--skip-install` runs use the already installed APK. Keep the phone unlocked. The runner requires one authorized phone or `--device` to select it. It operates only `dev.shutrwise.probe`, refuses to overwrite evidence directories and excludes the unique ADB serial from collection metadata.

After the initial build, each experiment runs with one `run.py` command. It waits for the on-device state and exports only that new run's files through the debug package's `run-as` access. No user media directory is read or modified.

The UI has a preview and a live JSON capture-state display. Buttons target camera 0; the intent-driven runner can choose another listed camera ID. Capture requests and complete results are saved alongside the DNGs.

## Capture method

- Enumerate listed camera IDs and any additional physical IDs whose characteristics are readable. Collect all advertised characteristic/request/result keys and stream configurations. Readable physical characteristics do not establish independently openable physical cameras.
- For capture, require both RAW and MANUAL_SENSOR and choose the largest regular RAW_SENSOR size. Create a RAW ImageReader plus a 640 × 480 preview where supported.
- Meter with auto exposure and continuous-picture focus if available for at least 2.5 seconds. Proceed when AE converges or after 5 seconds with a metered result.
- Hold the metered ISO and use manual shutter requests. A single frame uses 0 EV; a bracket uses -2/0/+2 EV relative to that run's metered shutter. Clamp requests to the advertised exposure range and record any clamp.
- Reuse the metered focus distance with AF off when supported, request AWB lock when available, and record actual focus, gains, lock states and OIS. These requests are not a guarantee; inspect their returned results.
- Submit one `capture` or one ordered `captureBurst`. Pair Image timestamps with result SENSOR_TIMESTAMP before writing each DNG with DngCreator.
- Use TIFF Orientation 1 explicitly. This preserves unrotated sensor axes rather than guessing a world-upright orientation.

DNG writes occur serially on the camera callback handler. Timing from this prototype does not establish maximum sustained burst throughput. No ZSL, physical-output routing, lens switching or motion analysis is tested. Captures close their camera session after saving; the debug app and source files remain on the phone.

## Independent inspection

Install rawpy, NumPy, Pillow and tifffile in a local virtual environment, then:

```bash
/path/to/venv/bin/python probe/inspect_dng.py /path/to/evidence-root --output /path/to/new/inspection.json
```

Inspection decodes the sensor mosaic through LibRaw/rawpy, checks dimensions and DNG exposure/ISO metadata against Camera2, reports sample statistics and writes derived JPEG previews. The previews use camera white balance, no automatic brightness normalization and the same rendering parameters. They are review images; the DNGs are source captures.

Pass `--contact-sheet-run main-bracket-01` to choose a different three-frame run for the contact sheet. Record the scene conditions separately from camera metadata. The initial S22 captures had varying light and establish controls and file output only. Three repeat brackets were then collected after the owner confirmed a closed garage, lights on and fixed phone placement.

Use each bracket's middle frame as the single-RAW baseline when comparing source information within that sequence. Every new run meters and focuses again, so ISO, focus and white balance can vary between runs. Artificial-light flicker is not measured. This probe does not prove dynamic-range improvement or superiority over Samsung Camera.

## Sources

- [CameraCharacteristics](https://developer.android.com/reference/android/hardware/camera2/CameraCharacteristics)
- [CameraCaptureSession](https://developer.android.com/reference/android/hardware/camera2/CameraCaptureSession)
- [Image timestamps](https://developer.android.com/reference/android/media/Image#getTimestamp()) and [SENSOR_TIMESTAMP](https://developer.android.com/reference/android/hardware/camera2/CaptureResult#SENSOR_TIMESTAMP)
- [DngCreator](https://developer.android.com/reference/android/hardware/camera2/DngCreator)
- [rawpy](https://github.com/letmaik/rawpy)
