"""
Run this WHILE capturing your TIFFs/video (separate process/terminal).

Polls the Boson's internal FPA (focal-plane-array) temperature and logs it
with elapsed seconds, so it can be joined against your per-frame ROI
analysis afterward with:

    python boson_roi_analysis.py <capture> --fpa-log fpa_log.csv --csv out.csv

Start this logger at the same moment you start your capture (video record
or TIFF sequence) so t_sec=0 lines up in both files.
"""
from __future__ import annotations

import argparse
import csv
import time

from flirpy.camera.boson import Boson


def main() -> None:
    ap = argparse.ArgumentParser(description="Log Boson FPA temperature during capture.")
    ap.add_argument("--out", default="fpa_log.csv", help="output CSV path")
    ap.add_argument("--hz", type=float, default=1.0,
                    help="poll rate in Hz (default 1; thermal drift is slow, "
                         "no need to go faster)")
    ap.add_argument("--duration", type=float, default=None,
                    help="stop automatically after N seconds (default: run "
                         "until Ctrl-C)")
    args = ap.parse_args()

    period = 1.0 / args.hz
    camera = Boson()

    print(f"Logging FPA temperature to {args.out} at {args.hz} Hz. Ctrl-C to stop.")
    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t_sec", "fpa_temp_C"])
        f.flush()
        t0 = time.time()
        try:
            while True:
                now = time.time() - t0
                if args.duration is not None and now >= args.duration:
                    break
                temp = camera.get_fpa_temperature()
                writer.writerow([round(now, 3), temp])
                f.flush()
                print(f"  t={now:7.1f}s  FPA={temp:6.2f} C", end="\r")
                time.sleep(period)
        except KeyboardInterrupt:
            pass

    print(f"\nDone. Wrote log to {args.out}")


if __name__ == "__main__":
    main()