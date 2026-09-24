# FLIR Boson R — Command & Control SDK Reference

**Purpose:** context file for an agent writing Python command/control scripts against a
radiometric FLIR Boson R camera (Project Calypso). Everything below is verified directly
from the vendor SDK source, not from marketing docs or web mirrors.

**Source of truth:** `3.0 IDD & SDK.zip` (user-supplied), specifically:
- `Boson_SDK_Documentation_rev300.pdf` — the Software IDD (doc #102-2013-42, rev300),
  matches firmware Release 3.0 (the release that introduced radiometry).
- `SDK_USER_PERMISSIONS/ClientFiles_Python/Client_API.py` — the actual Python client
  class (`pyClient`) with every callable method.
- `SDK_USER_PERMISSIONS/ClientFiles_Python/Client_Packager.py` — low-level byte
  packing/dispatch (confirms wire format; no client-side range validation is done here —
  whatever float you pass is sent straight to firmware).

This is the **plain Boson** SDK (not Boson+). If any camera in the fleet is a Boson+
module, double-check function IDs before reusing scripts — Boson+ renumbers some modules.

---

## Connecting to the camera

```python
from BosonSDK import CamAPI  # adjust import path to wherever the SDK folder lives

# ex=False (default): every call returns (returnCode, data) — check returnCode yourself
# ex=True: raises an Exception on any non-success FLR_RESULT instead
myCam = CamAPI.pyClient(manualport="/dev/ttyACM0", ex=True)  # or "COM7" on Windows

# ... do things ...

myCam.Close()
```

- Baudrate is fixed at 921600 for Boson; `Initialize()`/`Close()` are handled by the
  `pyClient` constructor/`.Close()`.
- `myCam.LookupAPI("search_str")` — introspection helper to find a method by partial
  name at runtime, useful for exploratory scripting.
- Every wrapped call in `Client_API.py` mirrors the IDD name minus the module prefix
  casing (e.g. IDD's `radiometrySetEmissivityTarget()` is exactly
  `myCam.radiometrySetEmissivityTarget(data)` in Python — 1:1 naming).

---

## Module: RADIOMETRY — Environmental Factors

This is the block that feeds the TLinear (temperature-linear) conversion. All are plain
floats, no structs, get/set pairs, and **all confirmed from the IDD text** (not inferred):

| Function (Set / Get) | Quantity | Units (per IDD) | FunctionID (set/get) |
|---|---|---|---|
| `radiometrySetTempWindow` / `GetTempWindow` | external window temperature | degK | 0x0042006B / 0x0042006C |
| `radiometrySetTransmissionWindow` / `GetTransmissionWindow` | window transmission | percentage | 0x0042006D / 0x0042006E |
| `radiometrySetReflectivityWindow` / `GetReflectivityWindow` | window reflectivity | percentage | 0x0042006F / 0x00420070 |
| `radiometrySetTempWindowReflection` / `GetTempWindowReflection` | temp reflected by window | degK | 0x00420071 / 0x00420072 |
| `radiometrySetTransmissionAtmosphere` / `GetTransmissionAtmosphere` | atmospheric transmission | percentage | 0x00420073 / 0x00420074 |
| `radiometrySetTempAtmosphere` / `GetTempAtmosphere` | atmospheric temperature | degK | 0x00420075 / 0x00420076 |
| **`radiometrySetEmissivityTarget` / `GetEmissivityTarget`** | **target/scene emissivity** | **percentage** | **0x00420077 / 0x00420078** |
| `radiometrySetTempBackground` / `GetTempBackground` | background temperature | degK | 0x00420079 / 0x0042007A |

**Do not confuse with:** `radiometrySetEmissivityShutterHousing` /
`GetEmissivityShutterHousing` (FunctionIDs earlier in the module) — this is a
factory-calibration term describing the *shutter housing's own* emissivity, used
internally for self-emission modeling during FFC. It is not the scene/water-surface
emissivity and should not be touched by a flight script.

**Open question / verify before trusting:** the IDD literally says "percentage," which
implies a 0–100 float scale. But the client-side packager (`Client_Packager.py`) does
**no range validation** — it just serializes whatever float it's given — and FLIR's own
published sample code has been inconsistent for the sibling `TransmissionWindow` call
(one official example passes `1.00`, another passes `100`). **Before scripting a real
value, do a round-trip test:** call the `Set`, then immediately call the matching `Get`,
and confirm the readback matches what you intended (e.g. set 95, read back 95 vs 0.95).

**Required after changing any of the above:** call
`myCam.TLinearRefreshLUT(mode)` (mode is `FLR_BOSON_TABLETYPE_E.FLR_BOSON_HIGHGAIN_TABLE`
or `..._LOWGAIN_TABLE`) — this recalculates the flux→temperature LUT from the new
radiometry parameters. Skipping this means your environmental-factor change has no
effect on the TLinear output until the next automatic recalculation trigger.

---

## Module: TLINEAR

Converts the corrected 16-bit signal to absolute temperature.

```python
from EnumTypes import FLR_ENABLE_E, FLR_BOSON_GAINMODE_E, FLR_BOSON_TABLETYPE_E

myCam.TLinearSetControl(FLR_ENABLE_E.FLR_ENABLE)          # enable TLinear output
myCam.TLinearGetControl()                                  # -> current enable state
myCam.TLinearGetLUT(mode, offset)                           # -> raw LUT coefficients (a, b), for inspection
myCam.TLinearRefreshLUT(FLR_BOSON_GAINMODE_E.FLR_BOSON_HIGH_GAIN)  # recompute LUT after param change
```

In high-gain state, TLinear 16-bit output = Kelvin × 100. In low-gain state, × 50.

---

## Module: BOSON — gain / FFC (relevant to radiometric accuracy)

```python
myCam.bosonSetGainMode(FLR_BOSON_GAINMODE_E.FLR_BOSON_HIGH_GAIN)  # or LOW_GAIN / AUTO_GAIN
myCam.bosonGetGainMode()
myCam.bosonRunFFC()          # trigger a flat-field correction
myCam.bosonGetFfcStatus()    # FLR_BOSON_FFCSTATUS_E: NO_FFC_PERFORMED / IMMINENT / IN_PROGRESS / COMPLETE
myCam.bosonlookupFPATempDegKx10()  # sensor temp, useful for logging alongside radiometry params
```

---

## Modules: IMAGESTATS / SPOTMETER (relevant to `boson_roi_stats.py` / ROI pipeline)

Two parallel statistics paths — pick based on whether you want raw pre-processing stats
or post-pipeline (TLinear-aware) stats:

```python
# IMAGESTATS — collected after NUC block, in raw counts (16-bit), full-frame or ROI
myCam.imageStatsSetROI(roi)              # roi: FLR_ROI_T(rowStart, rowStop, colStart, colStop)
myCam.imageStatsGetROI()
myCam.imageStatsGetMeanInROI()
myCam.imageStatsGetImageStats()          # -> (meanIntensity, peakIntensity, baseIntensity), UINT_16 counts

# SPOTMETER — collected at end of 16-bit pipeline; reports in temperature units
# directly IF Radiometry + TLinear are both enabled
myCam.spotMeterSetEnable(FLR_ENABLE_E.FLR_ENABLE)
myCam.spotMeterSetRoi(roi)
myCam.spotMeterGetSpotStats()            # -> (mean, deviation, min, max) in raw counts
myCam.spotMeterGetTempStats()            # -> (mean, deviation, min, max) as FLOAT, degrees —
                                          #    this is the one that gives you calibrated
                                          #    brightness temperature per-ROI without manual
                                          #    Planck-inversion math
```

`spotMeterGetTempStats()` is likely the most direct replacement/cross-check for whatever
`boson_roi_stats.py` currently does by hand, since it returns temperature-unit statistics
straight from firmware once TLinear is enabled and Emissivity/environmental factors are
set correctly.

---

## Basic data types (per IDD, Python mapping)

| SDK type | Python type |
|---|---|
| CHAR / UCHAR | int |
| INT_16 / UINT_16 / INT_32 / UINT_32 | int |
| FLOAT / DOUBLE | float |
| `FLR_ROI_T` | struct: `rowStart, rowStop, colStart, colStop` (UINT_16 each) |

Enums (`FLR_ENABLE_E`, `FLR_BOSON_GAINMODE_E`, `FLR_BOSON_TABLETYPE_E`,
`FLR_BOSON_FFCSTATUS_E`, etc.) live in `EnumTypes.py` in the same SDK folder.

---

## Project context (Calypso)

- SST retrieval method is airmass extrapolation (Bouguer-style fit): brightness
  temperature vs. sec(θ), zero-airmass intercept = SST. **Emissivity cancels out of that
  fit** — a constant multiplicative/offset error in emissivity shifts every point on the
  sec(θ) line equally and washes out in the intercept.
- It still matters for anything read directly off the camera (telemetry logs, raw
  TLinear brightness-temperature frames, `spotMeterGetTempStats()` output) — those are
  offset by whatever's actually configured in firmware, independent of what the
  downstream retrieval does with them.
- Practical implication for script design: set the Environmental Factors block once per
  flight/session (with a verified round-trip), log the values used alongside the data for
  reproducibility, and don't assume they need to be re-tuned per-frame — see the "cancels
  out" note above.
