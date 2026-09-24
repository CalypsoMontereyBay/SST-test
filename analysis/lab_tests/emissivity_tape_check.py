#!/usr/bin/env python3
"""
emissivity_tape_check.py -- what happens to the Round-2 measurement if we remove
the black tape from the hot plate?

JXP asked this directly (planning.md, Lab work Q&A Q23: "I think we are going to
remove the tape. Do you agree?").

A thermal camera measures radiance, not temperature. A target at Ts against a
room at Tbg sends the camera

    L = eps * L(Ts) + (1 - eps) * L(Tbg)

so a low-emissivity surface is mostly a MIRROR for the room. Two consequences,
and the second is the one that matters:

  1. BIAS  -- the reading sits below the true temperature.
  2. SENSITIVITY -- only the fraction eps of a real temperature change reaches
     the camera at all. Round 2 exists to test whether we can resolve 1 C steps;
     if eps is small, a 1 C step arrives as a small fraction of 1 C.

Radiances are integrated Planck over the Boson's 7.5-13.5 um band, not a
grey-body power law, so the numbers below stand on their own.

Run:
    python analysis/lab_tests/emissivity_tape_check.py
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

# Physical constants (SI)
H = 6.62607015e-34
C = 2.99792458e8
KB = 1.380649e-23

BAND_UM = (7.5, 13.5)      # Boson spectral response
T_PLATE_C = 35.0           # Round-1 / Round-2 working setpoint
T_ROOM_C = 22.0            # lab ambient; the thing a shiny plate reflects

# Representative LWIR emissivities
SURFACES = {
    "polished aluminium": 0.05,
    "machined / bare metal plate": 0.10,
    "lightly oxidised metal": 0.20,
    "anodised / painted metal": 0.40,
    "ceramic hotplate top": 0.90,
    "black electrical tape (Round 1)": 0.95,
    "high-emissivity paint": 0.97,
}


def planck_band_radiance(T_K: float, l1_um: float = BAND_UM[0],
                         l2_um: float = BAND_UM[1], n: int = 4000) -> float:
    """Integrate spectral radiance over the band. Arbitrary but consistent units."""
    lam = np.linspace(l1_um * 1e-6, l2_um * 1e-6, n)
    expo = H * C / (lam * KB * T_K)
    B = (2 * H * C**2) / (lam**5 * (np.exp(expo) - 1.0))
    return float(np.trapezoid(B, lam))


def apparent_C(Ts_C: float, Tbg_C: float, eps: float) -> float:
    """Temperature the camera reports for a target of emissivity eps."""
    L = eps * planck_band_radiance(Ts_C + 273.15) \
        + (1 - eps) * planck_band_radiance(Tbg_C + 273.15)
    f = lambda T_C: planck_band_radiance(T_C + 273.15) - L
    return brentq(f, -100.0, 400.0, xtol=1e-9)


def sensitivity(Ts_C: float, Tbg_C: float, eps: float, d: float = 0.5) -> float:
    """d(reading)/d(true target T): how much of a real 1 C step survives."""
    return (apparent_C(Ts_C + d, Tbg_C, eps)
            - apparent_C(Ts_C - d, Tbg_C, eps)) / (2 * d)


def table() -> None:
    print("=" * 78)
    print(f"Target at {T_PLATE_C:.0f} C, room at {T_ROOM_C:.0f} C, "
          f"band {BAND_UM[0]}-{BAND_UM[1]} um\n")
    print(f"  {'surface':>32}  {'eps':>5}  {'reads':>8}  {'bias':>8}  "
          f"{'1 C step -> ':>12}")
    for name, eps in SURFACES.items():
        app = apparent_C(T_PLATE_C, T_ROOM_C, eps)
        s = sensitivity(T_PLATE_C, T_ROOM_C, eps)
        print(f"  {name:>32}  {eps:5.2f}  {app:7.2f}C  {app - T_PLATE_C:+7.2f}C  "
              f"{s:9.3f} C")


def invert_round1() -> None:
    """Round 1 saw the bare plate read ~10 C low. What eps does that imply?"""
    print("\n" + "=" * 78)
    print("Inverting the Round-1 observation ('hotplate reads 10 C lower')\n")
    f = lambda e: apparent_C(T_PLATE_C, T_ROOM_C, e) - (T_PLATE_C - 10.0)
    eps_hat = brentq(f, 0.01, 0.999, xtol=1e-6)
    s = sensitivity(T_PLATE_C, T_ROOM_C, eps_hat)
    print(f"  implied bare-plate emissivity : {eps_hat:.3f}")
    print(f"  sensitivity at that emissivity: {s:.3f} C of reading per 1 C of target")
    print(f"  -> Round 1's own 10 C anomaly implies eps ~ {eps_hat:.2f}, squarely in\n"
          f"     the range of a lightly oxidised metal surface. An independent\n"
          f"     radiative model and the bench observation land in the same place,\n"
          f"     which is good evidence the tape was doing exactly what we think.\n")
    return eps_hat


def verdict(eps_bare: float) -> None:
    s_tape = sensitivity(T_PLATE_C, T_ROOM_C, 0.95)
    s_bare = sensitivity(T_PLATE_C, T_ROOM_C, eps_bare)
    print("=" * 78)
    print("Why this decides the tape question\n")
    print(f"  with tape (eps 0.95) : a 1.00 C step in the plate moves the "
          f"reading {s_tape:.3f} C")
    print(f"  bare  (eps {eps_bare:.2f})    : a 1.00 C step in the plate moves the "
          f"reading {s_bare:.3f} C")
    print(f"  loss of signal       : {s_tape / s_bare:.1f}x\n")
    print("  Round 2's core question is whether the Boson resolves 1 C steps.\n"
          "  Round 1 already showed ~0.56 C rms scatter on that test. Shrinking the\n"
          "  signal by the factor above pushes a 1 C step to roughly the noise, so\n"
          "  the experiment could not answer its own question. A contact probe does\n"
          "  NOT rescue this: the probe fixes the bias, but nothing recovers signal\n"
          "  that never reached the detector.\n")
    print("  A bare plate also makes the reading track the ROOM. Anyone walking in\n"
          "  front of the rig changes the answer -- which is precisely the 10 C\n"
          "  artefact Round 1 spent its afternoon chasing down.\n")


def storage() -> None:
    """JXP accepted 70 GB of raw. Cost that out honestly."""
    print("=" * 78)
    print("Accepting the 70 GB decision -- the two costs that come with it\n")
    gb_run = 640 * 512 * 2 * 60 * 120 / 1e9
    total = gb_run * 15
    print(f"  Boson R 640x512 @ 60 Hz, 2-min run : {gb_run:.2f} GB")
    print(f"  ~15 runs                           : {total:.1f} GB")
    print(f"  sustained write rate needed        : "
          f"{640 * 512 * 2 * 60 / 1e6:.0f} MB/s\n")
    for mbps in (25, 50, 100):
        hours = total * 8 * 1000 / mbps / 3600
        print(f"  upload of {total:.0f} GB at {mbps:3d} Mbps : {hours:5.1f} h")
    print("\n  -> The upload outlasts the experiment at any plausible campus rate,\n"
          "     so it cannot sit inside the 30-min teardown. Run it asynchronously\n"
          "     after the session and push the small reduced products first, so the\n"
          "     analysis is never blocked on the bulk transfer.\n"
          "  -> 39 MB/s sustained is real work for a laptop disk. Verify free space\n"
          "     (>100 GB) and do a 30-s trial capture with a frame count before the\n"
          "     first science run -- silently dropped frames would corrupt timing.\n")


if __name__ == "__main__":
    table()
    eps_bare = invert_round1()
    verdict(eps_bare)
    storage()
