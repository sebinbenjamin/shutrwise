# S22 Ultra device evidence

Recorded through the authorized USB ADB connection on 2026-10-06. Source: [software inventory JSON](software-inventory-20261006T043309Z.json).

| Item | Observed value |
| --- | --- |
| Manufacturer | samsung |
| Model | SM-S908E |
| Device codename | b0q |
| Android version / API level | 16 / 36 |
| Raw One UI property | 80000, not converted to a display version |
| Build | BP2A.250605.031.A3.S908EXXSEGZH4 |
| Security patch | 2026-08-05 |
| Samsung Camera version | 16.0.00.66 |
| Expert RAW | No package version found by the scoped package query |
| Open Camera | No package version found by the scoped package query |

Debian sees the Samsung USB device, and ADB reports it as authorized. Software inventory collection succeeded. A subsequent native probe exercised its CAMERA permission and collected Camera2 capabilities and original DNGs. See the [measurement report](../../../../docs/research/s22-camera2-probe-20261006.md), [final capability dump](camera2-probe-20261006/capabilities-final/capabilities.json) and [standardized repeat inspection](camera2-probe-controlled-20261006/dng-inspection.json).

T3 now reports Android available, lists this phone as a physical device, and has opened it in this thread's Device panel. Native screen capture succeeds. The host's missing tooling/path prerequisites were fixed, and a reversible Device hub 0.12.0 compatibility patch defaults physical phones to `scrcpy`. A fresh hub session also passes. See the [fix report](../../../../docs/research/t3-device-panel-fix-20261006.md), [redacted verification](t3-device-panel-verification-20261006.json) and [connection guide](../../../../docs/development-phone.md).

All four listed paths advertise RAW and MANUAL_SENSOR and yielded a decodable DNG. Main-camera brackets saved separate exposures with fixed ISO, focus and white-balance gains within each bracket. Three repeats after the owner standardized conditions produced nine valid DNGs. Original varying-light trials are retained separately. Sustained burst reliability, telephoto physical routing and capture-quality advantages remain unmeasured. This record applies to the spare development phone and does not establish target S25 Ultra behavior.

Subsequent [longer-single control measurements](../../../../docs/research/long-single-control-20261006.md) captured twelve fresh DNGs in matched four-frame sessions. An 80 ms single near ISO 282 looks less grainy than its 20 ms metered baseline near ISO 1130, with similar brightness and clipping. A bracket merge appears quieter still, with extra source/storage costs. These are bounded scene/render observations, not calibrated SNR/DR, sustained reliability, Samsung or S25 findings.
