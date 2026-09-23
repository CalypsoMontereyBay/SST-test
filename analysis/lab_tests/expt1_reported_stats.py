#!/usr/bin/env python3
"""
expt1_reported_stats.py -- reduce the numbers reported in the first Boson lab
test ("Boson Experiment", 2026-08-02, GDrive .../Sensors/SST/Lab Tests).

Nothing here re-analyses raw frames; it simply takes the mean temperatures
written into that document and asks what they actually constrain, so that the
second set of tests can be designed to close the gaps.

Two reported experiments:

  Expt 1  hot plate held at 35 C, camera at 15 / 30 / 45 cm.
          Question asked: does stand-off distance bias the reading?

  Expt 2  camera at 30 cm, plate commanded 35 -> 40 C in 1 C steps,
          10 frames averaged per step.
          Question asked: can the Boson resolve a 1 C step?

Run:
    conda activate ocean14
    python analysis/lab_tests/expt1_reported_stats.py
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# Expt 1: distance sweep, plate commanded 35 C throughout
# --------------------------------------------------------------------------
# distance_cm -> (min average, max average, mean average), all Celsius
DISTANCE = {
    15: (34.242, 34.776, 34.515),
    30: (34.829, 35.484, 35.166),
    45: (34.425, 35.084, 34.785),
}
PLATE_SETPOINT_C = 35.0

# --------------------------------------------------------------------------
# Expt 2: 1 C increment sweep at 30 cm, 10 frames averaged per step
# --------------------------------------------------------------------------
COMMANDED_C = np.array([35.0, 36.0, 37.0, 38.0, 39.0, 40.0])
MEASURED_C = np.array([33.740, 35.075, 35.285, 36.979, 36.690, 39.100])

# Per-pixel noise quoted in the document. The 30 cm entry is written as
# "1.0109C", an order of magnitude above its neighbours -- flagged, not fixed.
REPORTED_NOISE_C = {15: 0.0831, 30: 1.0109, 45: 0.1026}


def distance_sweep() -> None:
    print("Expt 1 -- distance sweep (plate commanded 35.0 C)")
    print(f"  {'d (cm)':>7}  {'mean':>7}  {'resid':>7}  {'max-min':>8}")
    means = []
    for d, (lo, hi, mean) in sorted(DISTANCE.items()):
        means.append(mean)
        print(f"  {d:>7}  {mean:>7.3f}  {mean - PLATE_SETPOINT_C:>+7.3f}  {hi - lo:>8.3f}")
    means = np.array(means)
    spread = means.max() - means.min()
    print(f"\n  spread across all three distances : {spread:.3f} C")
    print(f"  mean offset from setpoint         : {means.mean() - PLATE_SETPOINT_C:+.3f} C")
    print("  ordering with distance            : "
          f"{'monotonic' if np.all(np.diff(means) > 0) or np.all(np.diff(means) < 0) else 'NON-monotonic'}")
    print("  -> a non-monotonic spread of this size is consistent with an\n"
          "     uncertainty floor / plate settling, not with a distance term.\n"
          "     Distance cannot be separated from drift without a reference\n"
          "     thermometer on the plate surface and repeated visits to each\n"
          "     distance in randomised order.\n")


def increment_sweep() -> None:
    resid = MEASURED_C - COMMANDED_C
    steps = np.diff(MEASURED_C)
    slope, intercept = np.polyfit(COMMANDED_C, MEASURED_C, 1)
    fit_resid = MEASURED_C - (slope * COMMANDED_C + intercept)

    print("Expt 2 -- 1 C increments at 30 cm (10 frames averaged per step)")
    print(f"  {'commanded':>10}  {'measured':>9}  {'resid':>7}  {'step':>7}")
    for i, (c, m, r) in enumerate(zip(COMMANDED_C, MEASURED_C, resid)):
        step = f"{steps[i-1]:+7.3f}" if i else " " * 7
        print(f"  {c:>10.1f}  {m:>9.3f}  {r:>+7.3f}  {step}")

    print(f"\n  residual mean (bias)      : {resid.mean():+.3f} C")
    print(f"  residual std (scatter)    : {resid.std(ddof=1):.3f} C")
    print(f"  measured steps            : {np.round(steps, 3)}")
    print(f"  smallest / largest step   : {steps.min():+.3f} / {steps.max():+.3f} C")
    print(f"  steps that go backwards   : {(steps < 0).sum()} of {steps.size}")
    print(f"  linear fit                : measured = {slope:.3f} * commanded {intercept:+.3f}")
    print(f"  scatter about that fit    : {fit_resid.std(ddof=1):.3f} C rms")
    print("\n  -> the camera tracks the ramp (slope ~1), but one of five steps is\n"
          "     NEGATIVE and the rms scatter about the fit exceeds half a step.\n"
          "     On these data a 1 C change is NOT yet resolvable step-by-step.\n"
          "     The commanded temperature also rose monotonically in time, so a\n"
          "     drift of order 1 C over the run is fully degenerate with a gain\n"
          "     error -- the sweep must be re-run in randomised order, with a\n"
          "     return to a fixed anchor temperature between steps.\n")


def noise_check() -> None:
    print("Reported per-pixel noise")
    for d, n in sorted(REPORTED_NOISE_C.items()):
        flag = "  <-- 10x its neighbours; suspected typo for 0.10109" if n > 0.5 else ""
        print(f"  {d:>3} cm : {n:.4f} C{flag}")
    print("\n  -> If 0.101 C is right, single-pixel NETD is ~0.1 C and the median\n"
          "     of a 30x30 ROI averages down to well under 0.01 C. The ~1 C\n"
          "     residual scatter above is therefore NOT sensor noise; it is\n"
          "     target/scene systematics (emissivity, reflected background,\n"
          "     plate non-uniformity, FFC state, drift).\n")


if __name__ == "__main__":
    distance_sweep()
    increment_sweep()
    noise_check()
