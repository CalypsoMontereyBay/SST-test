

from __future__ import annotations

import argparse
import csv
import glob as globmod
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------

GAIN_SCALE_K_PER_COUNT = {"high": 0.01, "low": 0.02}
KELVIN_OFFSET = 273.15
PLAUSIBLE_C = (-50.0, 200.0)

TIFF_EXTS = (".tif", ".tiff", ".TIF", ".TIFF")

EIGHT_BIT_PIX_FMTS = {
    "gray", "yuv420p", "yuvj420p", "yuv422p", "yuvj422p", "yuv444p", "yuvj444p",
    "nv12", "nv21", "bgr24", "rgb24", "bgra", "rgba", "argb", "abgr", "pal8",
    "uyvy422", "yuyv422",
}

# E[max-min] of n Gaussian samples, in sigma. Monte Carlo, 12k-40k trials.
_RANGE_N = np.array([4, 9, 16, 25, 49, 100, 169, 256, 400, 625, 900,
                     1444, 2500, 4096, 6400, 10000], dtype=float)
_RANGE_F = np.array([2.0527, 2.9668, 3.5341, 3.9331, 4.4853, 5.0142, 5.3798,
                     5.6552, 5.9369, 6.2109, 6.4250, 6.6952, 6.9936, 7.2529,
                     7.4806, 7.7026], dtype=float)


def expected_range_factor(n_pixels: int) -> float:
    return float(np.interp(np.log(n_pixels), np.log(_RANGE_N), _RANGE_F))


def counts_to_celsius(counts: np.ndarray, gain: str) -> np.ndarray:
    return counts.astype(np.float64) * GAIN_SCALE_K_PER_COUNT[gain] - KELVIN_OFFSET


def plausibility(counts: np.ndarray, gain: str) -> float:
    t = counts_to_celsius(counts, gain)
    return float(np.mean((t >= PLAUSIBLE_C[0]) & (t <= PLAUSIBLE_C[1])))


def looks_like_upscaled_8bit(counts: np.ndarray) -> bool:
    """All values multiples of 257/256 => only 256 levels => 8-bit source."""
    flat = counts.reshape(-1)
    s = flat[:: max(1, flat.size // 200_000)]
    return bool(np.all(s % 257 == 0) or np.all(s % 256 == 0))


def natural_key(path: str):
    """Sort frame_2 before frame_10 (lexicographic sort gets this wrong)."""
    name = os.path.basename(path)
    return [int(tok) if tok.isdigit() else tok.lower()
            for tok in re.split(r"(\d+)", name)]


# --------------------------------------------------------------------------
# outlier removal + median downsampling
# --------------------------------------------------------------------------

def remove_outliers_iqr(data, axis=0, k=1.5):
    """
    Replace outliers (outside Q1 - k*IQR, Q3 + k*IQR) with NaN, computed along
    the given axis. Works for 1D, 2D, or 3D (frames, H, W) arrays.

    Pass axis=None to compute IQR over the WHOLE array at once (e.g. for a
    single 2D ROI, where you want one global IQR rather than a per-row/
    per-column one).
    """
    q1 = np.percentile(data, 25, axis=axis, keepdims=True)
    q3 = np.percentile(data, 75, axis=axis, keepdims=True)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr

    cleaned = data.astype(np.float64).copy()
    mask = (data < lower) | (data > upper)
    cleaned[mask] = np.nan
    return cleaned, int(np.sum(mask))


def median_downsample(data, chunk_size=115, mode="pixels"):
    """
    Group the data into chunks of `chunk_size` along either:
      - 'pixels' : last spatial axis (default) -- good for (H, W) or
                   (n_frames, H, W), grouping along W (or along the array's
                   flattened pixel axis for 1D pixel-intensity arrays)
      - 'frames' : axis 0 (time/frame axis) -- good for (n_frames, H, W) or (n_frames,)

    NaNs (from outlier removal) are ignored via nanmedian.
    Returns the downsampled array. Any leftover partial chunk at the end is
    dropped (change to keep it if you'd rather average a short final chunk).
    """
    if mode == "frames":
        axis = 0
    elif mode == "pixels":
        axis = data.ndim - 1  # last axis = columns/pixels
    else:
        raise ValueError("mode must be 'frames' or 'pixels'")

    n = data.shape[axis]
    n_chunks = n // chunk_size
    usable = n_chunks * chunk_size
    if usable == 0:
        return None  # not enough frames/pixels to fill even one chunk

    moved = np.moveaxis(data, axis, 0)[:usable]
    new_shape = (n_chunks, chunk_size) + moved.shape[1:]
    reshaped = moved.reshape(new_shape)

    medians = np.nanmedian(reshaped, axis=1)
    result = np.moveaxis(medians, 0, axis)
    return result


# --------------------------------------------------------------------------
# TIFF reading
# --------------------------------------------------------------------------

_TIFF_READER = None


def _get_tiff_reader():
    """Pick whichever TIFF library is installed; all handle 16-bit fine."""
    global _TIFF_READER
    if _TIFF_READER is not None:
        return _TIFF_READER
    try:
        import tifffile

        def read(p):
            a = tifffile.imread(p)
            return a if a.ndim == 3 else a[None, ...]
        _TIFF_READER = ("tifffile", read)
        return _TIFF_READER
    except ImportError:
        pass
    try:
        from PIL import Image

        def read(p):
            out = []
            with Image.open(p) as im:
                for i in range(getattr(im, "n_frames", 1)):
                    im.seek(i)
                    out.append(np.array(im))
            return np.stack(out)
        _TIFF_READER = ("Pillow", read)
        return _TIFF_READER
    except ImportError:
        pass
    try:
        import cv2

        def read(p):
            a = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            if a is None:
                raise OSError(f"cv2 could not read {p}")
            return a[None, ...]
        _TIFF_READER = ("opencv", read)
        return _TIFF_READER
    except ImportError:
        pass
    sys.exit("No TIFF library found. Install one:  pip install tifffile")


def _coerce_tiff_page(a: np.ndarray, path: str) -> np.ndarray:
    if a.ndim == 3 and a.shape[2] in (3, 4):
        sys.exit(f"{path} is a colour image ({a.shape[2]} channels) — that is a "
                 "colorized export, not radiometric data.")
    if a.dtype == np.uint16:
        return a
    if a.dtype == np.uint8:
        return a.astype(np.uint16)          # flagged later as 8-bit
    if np.issubdtype(a.dtype, np.integer):
        return a.astype(np.uint16)
    sys.exit(f"{path}: unexpected TIFF dtype {a.dtype}")


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

class TiffSource:
    kind = "tiff"

    def __init__(self, paths: list[str], fps: float):
        self.paths = paths
        self.fps = fps
        libname, self._read = _get_tiff_reader()
        self.lib = libname
        raw_first = self._read(paths[0])[0]
        self.dtype = raw_first.dtype          # BEFORE coercion, so 8-bit is visible
        first = _coerce_tiff_page(raw_first, paths[0])
        self.height, self.width = first.shape
        self._first = first
        # count pages so a multipage file reports a true frame count
        if len(paths) == 1:
            self.n_frames = int(self._read(paths[0]).shape[0])
            self.multipage = self.n_frames > 1
        else:
            self.n_frames = len(paths)
            self.multipage = False

    def describe(self) -> str:
        what = (f"multi-page TIFF, {self.n_frames} pages" if self.multipage
                else f"{self.n_frames} TIFF file(s)")
        return (f"{what}  {self.width}x{self.height}  dtype={self.dtype}  "
                f"reader={self.lib}")

    def first_frame(self) -> np.ndarray:
        return self._first

    def frames(self):
        for p in self.paths:
            stack = self._read(p)
            for page in stack:
                yield _coerce_tiff_page(page, p)


class VideoSource:
    kind = "video"

    def __init__(self, path: str, gain: str):
        require_ffmpeg()
        self.path = path
        info = probe_video(path)
        self.width, self.height = info["width"], info["height"]
        self.fps = info["fps"]
        self.n_frames = info["nb_frames"]
        self.pix_fmt = info["pix_fmt"]
        self.codec = info["codec"]
        self.nbytes = self.width * self.height * 2
        self.strategy, self._first = self._choose(gain)

    def _cmd(self, strategy: str) -> list[str]:
        base = ["ffmpeg", "-v", "error", "-i", self.path]
        if strategy == "copy":
            return base + ["-c:v", "copy", "-f", "rawvideo", "-"]
        return base + ["-f", "rawvideo", "-pix_fmt", "gray16le", "-"]

    def _one(self, strategy: str):
        p = subprocess.Popen(self._cmd(strategy), stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        try:
            buf = p.stdout.read(self.nbytes)
        finally:
            p.stdout.close(); p.kill(); p.wait()
        if not buf or len(buf) < self.nbytes:
            return None
        return np.frombuffer(buf, np.uint16).reshape(self.height, self.width)

    def _choose(self, gain: str):
        best = None
        for s in ("copy", "gray16"):
            f = self._one(s)
            if f is None:
                continue
            sc = plausibility(f, gain)
            if best is None or sc > best[2]:
                best = (s, f, sc)
        if best is None:
            sys.exit("Could not read a full frame from the video.")
        return best[0], best[1]

    def describe(self) -> str:
        return (f"{self.codec}  {self.width}x{self.height}  "
                f"pix_fmt={self.pix_fmt}  decode={self.strategy}"
                + (f"  frames={self.n_frames}" if self.n_frames else ""))

    def first_frame(self) -> np.ndarray:
        return self._first

    def frames(self):
        p = subprocess.Popen(self._cmd(self.strategy), stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        try:
            while True:
                buf = p.stdout.read(self.nbytes)
                if not buf or len(buf) < self.nbytes:
                    break
                yield np.frombuffer(buf, np.uint16).reshape(self.height, self.width)
        finally:
            if p.poll() is None:
                p.kill()
            p.stdout.close(); p.wait()


def require_ffmpeg() -> None:
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        sys.exit(f"Video input needs {', '.join(missing)} on PATH.\n"
                 "  macOS:  brew install ffmpeg")


def probe_video(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams",
         "-of", "json", path], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"ffprobe failed on {path!r}:\n{out.stderr.strip()}")
    try:
        st = json.loads(out.stdout)["streams"][0]
    except (KeyError, IndexError, json.JSONDecodeError):
        sys.exit(f"No video stream in {path!r}")

    def rate(s):
        if not s or "/" not in s:
            return 0.0
        a, b = s.split("/")
        return float(a) / float(b) if float(b) else 0.0

    return {"width": int(st["width"]), "height": int(st["height"]),
            "pix_fmt": st.get("pix_fmt", "?"), "codec": st.get("codec_name", "?"),
            "fps": rate(st.get("avg_frame_rate")) or rate(st.get("r_frame_rate")),
            "nb_frames": int(st["nb_frames"])
            if str(st.get("nb_frames", "")).isdigit() else None}


def build_source(target: str, gain: str, fps_hint: float):
    """Auto-detect folder / glob / multipage TIFF / video."""
    if os.path.isdir(target):
        paths = [os.path.join(target, f) for f in os.listdir(target)
                 if f.endswith(TIFF_EXTS)]
        if not paths:
            sys.exit(f"No .tif/.tiff files in {target!r}")
        return TiffSource(sorted(paths, key=natural_key), fps_hint)

    if any(ch in target for ch in "*?["):
        paths = [p for p in globmod.glob(target) if p.endswith(TIFF_EXTS)]
        if not paths:
            sys.exit(f"Pattern {target!r} matched no TIFF files")
        return TiffSource(sorted(paths, key=natural_key), fps_hint)

    if not os.path.exists(target):
        sys.exit(f"No such file or folder: {target!r}")

    if target.endswith(TIFF_EXTS):
        return TiffSource([target], fps_hint)

    return VideoSource(target, gain)


# --------------------------------------------------------------------------
# ROI + verdict
# --------------------------------------------------------------------------

def roi_bounds(h: int, w: int, size: int):
    if size > min(h, w):
        sys.exit(f"ROI {size}x{size} does not fit in a {w}x{h} frame")
    y0, x0 = (h - size) // 2, (w - size) // 2
    return y0, y0 + size, x0, x0 + size


def verdict(src, frame: np.ndarray, gain: str) -> bool:
    score = plausibility(frame, gain)
    print(f"Decode : plausibility={score:.1%}")

    if src.kind == "video" and src.pix_fmt in EIGHT_BIT_PIX_FMTS:
        print(f"\n  VERDICT: NOT radiometric — stream is {src.pix_fmt}, 8 bits per "
              "component.\n  This is AGC display video; temperatures are unrecoverable.")
        return False

    if src.kind == "tiff" and src.dtype == np.uint8:
        print("\n  VERDICT: NOT radiometric — these TIFFs are 8-bit.\n"
              "  Re-export with USB Video Mode set to IR16 (pre-AGC).")
        return False

    if looks_like_upscaled_8bit(frame):
        print("\n  VERDICT: NOT radiometric — every value is a multiple of 257/256,\n"
              "  so the data only ever had 256 levels. 8-bit widened to 16.")
        return False

    if score < 0.5:
        print(f"\n  VERDICT: UNRELIABLE — only {score:.1%} of pixels imply a sensible\n"
              "  temperature. Likely the wrong --gain, or 16-bit data that is not\n"
              "  TLinear (raw flux counts have no temperature mapping).")
        return False

    print("\n  VERDICT: looks like genuine 16-bit TLinear data.")
    return True


def geometry_note(src) -> None:
    """Boson frame sizes carry setup information worth surfacing."""
    w, h = src.width, src.height
    if (w, h) == (640, 514):
        print("  note   : 640x514 — telemetry rows enabled (last 2 rows are metadata)")
    elif (w, h) == (320, 258):
        print("  note   : 320x258 — telemetry rows enabled (last 2 rows are metadata)")
    elif (w, h) == (640, 512):
        print("  note   : 640x512 — Boson 640, no telemetry rows")
    elif (w, h) == (320, 256):
        print("  note   : 320x256 — Boson 320 in Y16/IR16 mode")


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def expectation_check(frame: np.ndarray, roi: tuple[int, int, int, int],
                      expect_C: float, gain: str) -> None:
    """Given a known target temperature, test whether the counts are really TLinear."""
    y0, y1, x0, x1 = roi
    obs = float(frame[y0:y1, x0:x1].mean())
    want_hi = (expect_C + KELVIN_OFFSET) * 100.0
    want_lo = (expect_C + KELVIN_OFFSET) * 50.0
    implied = obs / (expect_C + KELVIN_OFFSET)

    print(f"\n--- EXPECTATION CHECK against a known {expect_C:g} C target ---")
    print(f"  observed mean ROI counts      : {obs:9.0f}")
    print(f"  expected if TLinear high gain : {want_hi:9.0f}   "
          f"(off by {obs - want_hi:+.0f})")
    print(f"  expected if TLinear low  gain : {want_lo:9.0f}   "
          f"(off by {obs - want_lo:+.0f})")
    print(f"  implied counts-per-Kelvin     : {implied:9.2f}"
          "   (TLinear = 100 high / 50 low)")

    if abs(implied - 100.0) < 3.0:
        print("  => consistent with TLinear HIGH gain. Use --gain high.")
    elif abs(implied - 50.0) < 2.0:
        print("  => consistent with TLinear LOW gain. Re-run with --gain low.")
    else:
        print("  => NOT a TLinear scale factor. The camera is almost certainly")
        print("     outputting pre-AGC FLUX ('temperature stable') data rather than")
        print("     temperature-linear data. 16-bit and pre-AGC is not sufficient:")
        print("     radiometry/TLinear must also be ENABLED, and the TLinear LUT")
        print("     refreshed afterwards. Flux counts can land in a range that looks")
        print("     like a believable temperature, which is why this check exists.")


def summarise(rows: list[dict], roi_size: int, iqr_k: float, chunk_size: int) -> None:
    mins = np.fromiter((r["min_C"] for r in rows), float)
    maxs = np.fromiter((r["max_C"] for r in rows), float)
    means = np.fromiter((r["mean_C"] for r in rows), float)
    mins_clean = np.fromiter((r["min_C_clean"] for r in rows), float)
    maxs_clean = np.fromiter((r["max_C_clean"] for r in rows), float)
    medians = np.fromiter((r["median_C"] for r in rows), float)
    n_outliers_total = sum(r["n_outliers"] for r in rows)
    n_px = roi_size * roi_size
    total_px = len(rows) * n_px

    print(f"\nFrames analysed : {len(rows)}")

    print("\n--- RAW (no outlier cropping) ---")
    print(f"  MIN average     : {mins.mean():9.3f} C   (sd {mins.std(ddof=0):.3f})"
          "   avg of per-frame ROI minimum")
    print(f"  MAX average     : {maxs.mean():9.3f} C   (sd {maxs.std(ddof=0):.3f})"
          "   avg of per-frame ROI maximum")
    print(f"  AVERAGE average : {means.mean():9.3f} C   (sd {means.std(ddof=0):.3f})"
          "   avg of per-frame ROI mean")

    print(f"\n--- AFTER OUTLIER REMOVAL (IQR, k={iqr_k}) ---")
    print(f"  outliers cropped        : {n_outliers_total} / {total_px} px "
          f"({100 * n_outliers_total / total_px:.2f}%)")
    print(f"  MIN average (clean)     : {mins_clean.mean():9.3f} C   "
          "avg of per-frame ROI min, outliers excluded")
    print(f"  MAX average (clean)     : {maxs_clean.mean():9.3f} C   "
          "avg of per-frame ROI max, outliers excluded")
    print(f"  MEDIAN average (clean)  : {medians.mean():9.3f} C   (sd {medians.std(ddof=0):.3f})"
          "   <- robust estimate, use this")

    ds_mean = median_downsample(means, chunk_size=chunk_size, mode="frames")
    ds_median = median_downsample(medians, chunk_size=chunk_size, mode="frames")
    print(f"\n--- MEDIAN DOWNSAMPLE (chunks of {chunk_size} frames) ---")
    if ds_mean is None:
        print(f"  skipped: only {len(rows)} frames, fewer than chunk size {chunk_size}")
    else:
        print(f"  {len(rows)} frames -> {len(ds_mean)} chunk(s)")
        print(f"  downsampled AVERAGE (raw mean, chunked)     : {ds_mean.mean():9.3f} C")
        print(f"  downsampled MEDIAN (clean median, chunked)  : {ds_median.mean():9.3f} C")

    spread = float((maxs - mins).mean())
    factor = expected_range_factor(n_px)
    print("\n--- interpretation ---")
    print("  Use MEDIAN average (clean) as the temperature of the target --")
    print("  it is robust to the outlier pixels that AVERAGE average is not.")
    print(f"    mean per-frame spread (MAX-MIN), raw : {spread:8.3f} C")
    print(f"    expected range for n={n_px:<6d}            : {factor:8.3f} sigma")
    print(f"    => implied per-pixel noise sigma     : {spread / factor:8.4f} C"
          "   (compare to NETD)")
    asym = (maxs.mean() - means.mean()) - (means.mean() - mins.mean())
    tag = ("(symmetric: uniform target)" if abs(asym) < 0.25 * spread
           else "(ASYMMETRIC: real structure or a bad pixel in the ROI)")
    print(f"    min/max asymmetry about mean         : {asym:+8.4f} C   {tag}")

    print("\n--- whole clip ---")
    print(f"  coldest pixel seen (raw)     : {mins.min():9.3f} C")
    print(f"  hottest pixel seen (raw)     : {maxs.max():9.3f} C")
    print(f"  drift of ROI mean, last-first: {means[-1] - means[0]:+8.3f} C")


# --------------------------------------------------------------------------

def run(target: str, gain: str, roi_size: int, csv_path: str | None,
        max_frames: int | None, force: bool, probe_only: bool,
        fps_hint: float, expect_C: float | None,
        iqr_k: float = 1.5, chunk_size: int = 115) -> None:
    src = build_source(target, gain, fps_hint)
    print(f"\nInput  : {target}")
    print(f"Source : {src.describe()}")
    geometry_note(src)

    frame0 = src.first_frame()
    ok = verdict(src, frame0, gain)

    lo, hi = int(frame0.min()), int(frame0.max())
    print(f"\n  raw counts : min={lo}  max={hi}  mean={frame0.mean():.1f}")
    for g in ("high", "low"):
        s = GAIN_SCALE_K_PER_COUNT[g]
        mark = "   <-- selected" if g == gain else ""
        print(f"    as {g:>4} gain : {lo * s - KELVIN_OFFSET:8.2f} .. "
              f"{hi * s - KELVIN_OFFSET:8.2f} C{mark}")

    y0, y1, x0, x1 = roi_bounds(src.height, src.width, roi_size)

    if expect_C is not None:
        expectation_check(frame0, (y0, y1, x0, x1), expect_C, gain)

    if probe_only:
        if ok:
            roi = counts_to_celsius(frame0[y0:y1, x0:x1], gain)
            print(f"\n  ROI {roi_size}x{roi_size} at rows {y0}:{y1}, cols {x0}:{x1} "
                  f"({roi.size} px)")
            print(f"    frame 0: min={roi.min():.3f}  max={roi.max():.3f}  "
                  f"mean={roi.mean():.3f} C")
        else:
            print("\n  In the Boson GUI: Image Appearance -> USB Video Mode Controls")
            print("  -> USB Video Mode = IR16 (pre-AGC), with radiometry/TLinear on.")
            print("  Select the Boson COM port first or settings will not apply.")
        print()
        return

    if not ok and not force:
        sys.exit("\nRefusing to report temperatures from non-radiometric data.\n"
                 "Run --probe for detail, or --force to override (output invalid).\n")
    if not ok:
        print("\n  --force given. THESE ARE NOT VALID TEMPERATURES.")

    print(f"\nROI {roi_size}x{roi_size} at rows {y0}:{y1}, cols {x0}:{x1}  "
          f"(gain={gain}, {GAIN_SCALE_K_PER_COUNT[gain]} K/count)")
    print(f"  frame-0 ROI raw counts: mean={frame0[y0:y1, x0:x1].mean():.0f}  "
          f"(a T degC target should read {(0 + KELVIN_OFFSET) * 100:.0f} + T*100)")
    print(f"  outlier crop: IQR k={iqr_k}   median downsample: chunks of {chunk_size} frames")

    fps = src.fps
    rows: list[dict] = []
    for idx, img in enumerate(src.frames()):
        if max_frames is not None and idx >= max_frames:
            break
        if img.shape != (src.height, src.width):
            print(f"  skipping frame {idx}: shape {img.shape} differs from first frame")
            continue
        roi = counts_to_celsius(img[y0:y1, x0:x1], gain)
        roi_clean, n_out = remove_outliers_iqr(roi, axis=None, k=iqr_k)
        rows.append({"frame": idx,
                     "t_sec": round(idx / fps, 6) if fps > 0 else "",
                     "min_C": float(roi.min()), "max_C": float(roi.max()),
                     "mean_C": float(roi.mean()), "std_C": float(roi.std(ddof=0)),
                     "min_C_clean": float(np.nanmin(roi_clean)),
                     "max_C_clean": float(np.nanmax(roi_clean)),
                     "median_C": float(np.nanmedian(roi_clean)),
                     "n_outliers": n_out})

    if not rows:
        sys.exit("No frames read.")

    summarise(rows, roi_size, iqr_k, chunk_size)

    if csv_path:
        with open(csv_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["frame", "t_sec", "min_C", "max_C",
                                               "mean_C", "std_C", "min_C_clean",
                                               "max_C_clean", "median_C", "n_outliers"])
            w.writeheader(); w.writerows(rows)
        print(f"\nPer-frame values -> {csv_path}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="ROI temperature statistics from FLIR Boson TIFF sequences or video.")
    ap.add_argument("input", help="TIFF folder, glob, multipage TIFF, or video file")
    ap.add_argument("--roi", type=int, default=30,
                    help="edge length of the centred square ROI (default 30)")
    ap.add_argument("--gain", choices=("high", "low"), default="high",
                    help="Boson gain state during capture (default high)")
    ap.add_argument("--csv", default=None, help="write per-frame values here")
    ap.add_argument("--probe", action="store_true",
                    help="inspect and report whether the data is radiometric, then exit")
    ap.add_argument("--fps", type=float, default=60.0,
                    help="frame rate for TIFF sequences, for the t_sec column "
                         "(default 60; use 30 if Averager Mode was enabled)")
    ap.add_argument("--max-frames", type=int, default=None, help="stop after N frames")
    ap.add_argument("--force", action="store_true",
                    help="process non-radiometric data anyway (output invalid)")
    ap.add_argument("--expect", type=float, default=None, metavar="DEG_C",
                    help="known target temperature; checks whether the counts are "
                         "really on a TLinear scale")
    ap.add_argument("--iqr-k", type=float, default=1.5, metavar="K",
                    help="IQR multiplier for outlier cropping per frame's ROI "
                         "(default 1.5; lower = stricter, higher = more lenient)")
    ap.add_argument("--chunk", type=int, default=115, metavar="N",
                    help="median-downsample the per-frame series in chunks of N "
                         "frames (default 115)")
    args = ap.parse_args()

    if args.roi < 1:
        sys.exit("--roi must be >= 1")
    run(args.input, args.gain, args.roi, args.csv, args.max_frames,
        args.force, args.probe, args.fps, args.expect, args.iqr_k, args.chunk)


if __name__ == "__main__":
    main()