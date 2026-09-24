#!/usr/bin/env python3
"""
round2_time_budget.py -- can Round 2 of the Boson lab tests fit in "a few hours"
on 2026-09-24?

JXP asked this directly (planning.md, Lab work Q&A Q18). The answer depends
almost entirely on the per-setpoint dwell time, which in turn depends on whether
a contact thermometer is present: with one, "settled" means the probe is stable,
which is fast; without one, "settled" means we have waited long enough to trust
the hot-plate dial, which is slow and still not trustworthy.

This also sizes the raw data volume, which turned out to be the other binding
constraint -- see data_volume().

Run:
    python analysis/lab_tests/round2_time_budget.py
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Scenario knobs
# --------------------------------------------------------------------------
# Per-setpoint dwell = settle + record, in minutes.
SETTLE_DIAL = 10.0      # no probe: wait out the plate, trust the dial
SETTLE_PROBE = 3.0      # probe on surface: wait until it is stable to <0.1 C/min
RECORD = 2.0            # 2-minute capture per the Day-2 doc

# Increment sweep: 6 setpoints (35..40 C). Anchor returns break the
# drift/gain degeneracy by revisiting a fixed temperature.
N_SETPOINTS = 6
ANCHORS_FULL = 5        # anchor between every step
ANCHORS_LIGHT = 2       # anchor only at start and end (bracketing)

FIXED_OVERHEAD = {
    "setup: rig, tape, markers, wiring, SDK check, setup photos": 45.0,
    "teardown + data offload": 30.0,
}


def sweep_minutes(settle: float, n_anchors: int) -> float:
    dwells = N_SETPOINTS + n_anchors
    return dwells * (settle + RECORD)


def scenario(name: str, settle: float, n_anchors: int,
             do_distance: bool, do_drift: bool, do_wind: bool,
             do_external: bool = False) -> float:
    items = dict(FIXED_OVERHEAD)

    # Drift test: FFC disabled, camera powered on cold, staring at a stable
    # target while the focal plane warms to equilibrium. Must run FIRST -- once
    # the camera is warm a cold start cannot be recovered in a single session.
    if do_drift:
        items["T1 drift, FFC disabled, cold start -> equilibrium"] = 50.0

    items[f"T2 increment sweep ({N_SETPOINTS} pts + {n_anchors} anchors)"] = \
        sweep_minutes(settle, n_anchors)

    # Plate is already at 35 C and stays there, so only the camera moves:
    # no plate settling needed, just a short restabilise after each move.
    if do_distance:
        items["T3 distance / scene-fill (5 configs, plate held at 35 C)"] = \
            5 * (1.0 + RECORD) + 5.0

    if do_wind:
        items["T4 wind (4 configs + rig changes)"] = 4 * (1.0 + RECORD) + 10.0

    # Rob asked (Q10 refinement) that we learn how External FFC mode behaves.
    # Kept deliberately separate from the measurement runs: External computes
    # its correction FROM the scene, so running it during a science capture
    # would inject the very artefact we are trying to quantify.
    if do_external:
        items["T5 External-mode FFC characterisation (separate block)"] = 15.0

    total = sum(items.values())
    print(f"--- {name}")
    for k, v in items.items():
        print(f"    {v:6.0f} min   {k}")
    print(f"    {'-' * 6}")
    print(f"    {total:6.0f} min   TOTAL  = {total / 60:.1f} h\n")
    return total


def data_volume() -> None:
    """Raw TIFF volume per 2-minute capture, by camera variant."""
    print("=" * 74)
    print("Raw data volume per 2-minute capture (16-bit TIFF, uncompressed)\n")
    print(f"  {'variant':>22}  {'MB/frame':>9}  {'frames':>8}  {'GB/run':>8}  {'GB x 15 runs':>13}")
    for label, (w, h, fps) in {
        "Boson 640 @ 60 Hz": (640, 512, 60),
        "Boson 640 @  9 Hz": (640, 512, 9),
        "Boson 320 @ 60 Hz": (320, 256, 60),
        "Boson 320 @  9 Hz": (320, 256, 9),
        "any, decimated to 2 Hz": (640, 512, 2),
    }.items():
        mb_frame = w * h * 2 / 1e6
        frames = fps * RECORD * 60
        gb_run = mb_frame * frames / 1e3
        print(f"  {label:>22}  {mb_frame:9.3f}  {frames:8.0f}  {gb_run:8.2f}  {gb_run * 15:13.1f}")
    print("\n  -> At 640/60 Hz a single run is ~4.7 GB and a full day ~70 GB. That does\n"
          "     not belong in a Google Drive folder, and the upload alone would outlast\n"
          "     the experiment. Thermal drift is a slow signal; 2 Hz preserves it at\n"
          "     ~1/30 the volume. Decide capture rate BEFORE the session, not after.\n")


if __name__ == "__main__":
    print("=" * 74)
    print("Round-2 bench-time scenarios (2026-09-24)\n")

    scenario("A. As answered in the Q&A: no probe, full anchors, everything",
             SETTLE_DIAL, ANCHORS_FULL, do_distance=True, do_drift=True, do_wind=True)

    scenario("B. Contact probe shortens settle; everything else unchanged",
             SETTLE_PROBE, ANCHORS_FULL, do_distance=True, do_drift=True, do_wind=True)

    scenario("C. Probe + bracketing anchors only + drop the distance re-test",
             SETTLE_PROBE, ANCHORS_LIGHT, do_distance=False, do_drift=True, do_wind=True)

    scenario("C+. Scenario C plus Rob's External-mode characterisation block",
             SETTLE_PROBE, ANCHORS_LIGHT, do_distance=False, do_drift=True, do_wind=True,
             do_external=True)

    scenario("D. C, but defer the FFC-disabled drift test to its own session",
             SETTLE_PROBE, ANCHORS_LIGHT, do_distance=False, do_drift=False, do_wind=True)

    data_volume()
