#!/usr/bin/env python3
"""
round2_setpoint_order.py -- generate the randomised setpoint order for the
Round-2 increment sweep (T2), with anchor visits.

Round 1 ran 35 -> 40 C monotonically, which makes camera drift degenerate with a
gain error: both produce a sloped residual and the data cannot tell them apart.
Randomising the order converts drift from a systematic into scatter, and the
repeated anchor visits let us MEASURE the drift directly (any change in the
anchor reading across the run is drift, since the anchor's true temperature is
the same each time).

Seeded so the order in the checklist is reproducible and can be regenerated if
the sheet is lost.

Run:
    python analysis/lab_tests/round2_setpoint_order.py
"""

from __future__ import annotations

import random

SEED = 20260924          # the test date; arbitrary but recorded
SETPOINTS_C = [35, 36, 37, 38, 39, 40]
ANCHOR_C = 35            # revisited first and last


def build_order() -> list[tuple[str, int]]:
    rng = random.Random(SEED)
    shuffled = SETPOINTS_C[:]
    rng.shuffle(shuffled)
    seq = [("ANCHOR", ANCHOR_C)]
    seq += [("setpoint", t) for t in shuffled]
    seq += [("ANCHOR", ANCHOR_C)]
    return seq


if __name__ == "__main__":
    seq = build_order()
    print(f"Randomised T2 order (seed={SEED})\n")
    print(f"  {'#':>3}  {'kind':>9}  {'T (C)':>6}")
    for i, (kind, t) in enumerate(seq, 1):
        print(f"  {i:>3}  {kind:>9}  {t:>6}")
    print(f"\n  {len(seq)} dwells total.")
    print("  The two ANCHOR visits bracket the run: comparing them gives a direct")
    print("  measurement of how far the camera drifted over the whole sweep.")
    print(f"  35 C is visited {sum(1 for _, t in seq if t == 35)} times in all, which")
    print("  doubles as a repeatability check at a single temperature.")
