# Planning SST-test

## Goals

This document plans the work for the SST-test repository. The overarching goal is:

- Organize and enable our tests to collect data of Sea Surface Temperature (SST)
  for the Calypso Monterey Bay project.

To get there, we need to make and record a set of decisions and plans. In
particular, we will:

- Identify the **sensor** to use for measuring SST (and any companion
  observables, e.g. ocean color).
- Identify the **UAV** (platform) that will carry the sensor.
- Identify **where to fly** within Monterey Bay to collect the data.
- Plan how to **coordinate with in-situ measurements** for calibration and
  validation.

The prompts below build up a design/planning document,
`docs/design/SST_design.md`, that captures these decisions. As with our other
repositories, the document will not include specific code recommendations; we
will generate a separate doc for that.

## Claude

### Skills

Consider using the skills in `.claude/skills/`.

## Context

Examine the following resources that may help with the planning. *I will add a
number of papers on previous efforts* (place them in `docs/PDFs/`); read them as
they appear and fold the relevant content into `docs/context.md`.

- **Papers on previous efforts** — to be added by JXP to `docs/PDFs/`
  (airborne / UAV SST campaigns, sensor characterizations, Monterey Bay
  oceanography, in-situ SST calibration/validation).
- **The `flight-plan` repository** on this computer
  (`/home/xavier/Projects/CMB/flight-plan`) — the existing sun-aware
  flight-planning engine for the Calypso project. It already encodes a working
  platform (BlackSwift S2 fixed-wing UAV), a science-leg geometry (135° from the
  sun to avoid glint), and a flight region (lawnmower grid centered on the **M1
  mooring** in Monterey Bay). This is a primary input for the UAV, sensor, and
  flight-region work below.
- **The M1 mooring** (MBARI) — its location, instrumentation, and the in-situ SST
  record it provides.
- Any relevant Monterey Bay datasets / assets JXP points to during the work.

## Overview

Guidelines for the planning/design document, which will be named
`SST_design.md` and stored in `docs/design/`. Keep in mind:

- You are encouraged to suggest your own ideas and options.
- This document will be used to guide the work of the SST-test project.
- It will not include specific code recommendations; we will generate a separate
  doc for that.
- Add a version number (start at 0.1), a date, and authors (JXP and Claude).
- Where a decision is not yet made, write questions in the relevant **Q&A**
  section below and I will answer them; fold the answers back into the document.

## Prompts

### Context

1. Read the Context section above. Read the papers (as they are added) and the
   `flight-plan` repository. Generate a `docs/context.md` file that is a reduced
   form of the relevant information. Add a version number and date to the file.
   Log your work in the Logs section below.

### Prep

1. Start `docs/design/SST_design.md` with a "Preamble" section describing what
   the document is for. Add a version number (0.1), today's date, and authors
   (JXP and Claude). Log your work.

### Lab work

1. We are performing a series of in the lab tests on the Boson sensor in preparation for the flight tests.  There are 2 Google docs on "GDrive:Oceanography/Research/Calypso Monterey Bay/Sensors/SST/Lab Tests" describing: (i) our first set of tests and (ii) our planned second set of tests.  Please read both docs.  We are going to generate a detailed checklist for the 2nd set of tests as a separate doc in the Drive.  Discuss this with me before doing so; ask questions in the Q&A section below.  Use Opus 5. Log your work.

#### Q&A

**Claude, 2026-09-23 — questions before drafting the Round-2 checklist.**

I read both Drive docs ("Boson Experiment", 2026-08-02, and "Boson Experiment 2",
the Day-2 plan) in `GDrive:Oceanography/Research/Calypso Monterey Bay/Sensors/SST/Lab Tests`,
plus the local `boson_roi_stats.py` / `process_thermal_data.py` / `fpatemp.py`.
I reduced the Round-1 numbers in `analysis/lab_tests/expt1_reported_stats.py`.
What that reduction says, and which drives most of the questions below:

- **Distance sweep** (plate at 35 C): means 34.52 / 35.17 / 34.79 C at 15 / 30 / 45 cm
  — a 0.65 C spread that is *non-monotonic* in distance. That is an uncertainty
  floor, not a distance effect. The experiment as run cannot detect one.
- **1 C increment sweep**: bias −1.36 C, scatter 0.56 C rms, measured steps
  +1.34, +0.21, +1.69, **−0.29**, +2.41. One step of five goes *backwards*.
  A 1 C change is not yet resolvable step-by-step. Because the commanded
  temperature rose monotonically in time, drift is fully degenerate with a
  gain error — the ramp cannot distinguish them.
- **Noise**: the quoted per-pixel noise is 0.083 / **1.011** / 0.103 C. The middle
  value is 10x its neighbours and I read it as a typo for 0.101. If ~0.1 C
  per-pixel is right, the median of a 30x30 ROI averages down to <0.01 C —
  so the ~1 C scatter above is **not** sensor noise. It is target/scene
  systematics. Round 2 should be built to attack those, not to re-measure noise.

The Day-2 doc as written repeats Round 1 and adds a wind test. My concern is
that it would reproduce the same ~1 C floor, because the things that set that
floor are still unmeasured. Questions:

**A. The missing reference — this is the one that matters most**

1. There is no independent thermometer anywhere in either round. The hot-plate
   *dial setting* is being used as truth, but a plate dial reports the heater
   element, not the tape surface, and can easily be off by >1 C. Every accuracy
   number above is therefore uncalibrated. Can we get a contact reference on the
   target surface — a thermocouple/thermistor taped under the black tape, or a
   calibrated hand-held probe read at each setpoint? *Recommendation: yes, and
   treat the checklist as blocked on it. Without it Round 2 measures repeatability
   only, and we should say so explicitly rather than report "accuracy".*
2. Do we have access to a proper calibrated blackbody (e.g. through MBARI, BELS,
   or Steve McGuire's lab)? That would replace the hot-plate + tape entirely.
   Is it worth a week's delay to borrow one?

>A. (1) [RW] ; (2) We do not have a proper calibrated blackbody.  **IN PROGRESS, ASSUME NO FOR NOW (9/23/26 @ 12:02 PM)**

**B. Emissivity and reflected background**

3. Round 1 found the bare plate read ~10 C low from specular reflection, fixed by
   black electrical tape. But the tape's emissivity was never measured — it is
   assumed. The earlier "Static Sensor SST Checklist" says to set emissivity 0.98
   *in the FLIR GUI*; as far as I can tell the Boson's TLinear output has no
   user emissivity setting, so that correction has to happen in our analysis
   instead. Is that your understanding too? Should the checklist record raw
   TLinear and apply emissivity in post, rather than trying to set it on the camera?
>A. [RW/CP]
   -> RW: Should be verified by RW, but yes, if user-side emissivity settings don't exist in the gui, we must correct in post.
      However, if they exist in the SDK, we should set it in camera using software for the real missions.

4. To do that correction at all we need the **reflected background temperature**
   (the apparent temperature of whatever the target is reflecting — i.e. the room,
   or the person standing in front of it). Nothing currently records it. Shall I
   add a step: point the camera at a crumpled-foil diffuse reflector at the target
   position and log that reading at every setpoint?
>A. Yes, add that
5. The Day-2 checklist says "Check tape w/ heat gun". What is that step verifying?
   I want to write it down correctly, and if the intent is "confirm the tape and
   the plate are at the same temperature", there is a cleaner way to say it.
>A. Yes, that is the intent

**C. Confounds in the design**

6. May I randomise the order of the temperature setpoints, and return to a fixed
   anchor (say 35 C) between each one? That is what breaks the drift/gain
   degeneracy identified above. It costs maybe 40 extra minutes.
   *Recommendation: yes — without it Round 2's increment test is uninterpretable
   in the same way Round 1's was.*
>A. Yes, do that

7. Ten frames per step was flagged as too few in Round 1, and the Day-2 doc moves
   to 2-minute videos. At ~60 Hz that is ~7200 frames. Is 2 minutes per setpoint
   the right dwell, and — more important — how long do we wait after changing the
   setpoint before we start recording? Nothing specifies a settling time, and
   plate settling is my leading suspect for the Round-1 scatter.
   *Recommendation: 10 min settle, then 2 min record, and log the FPA temperature
   throughout with `fpatemp.py` so settling is visible rather than assumed.*
>A. Yes, use your recommendedation

8. **Gain state** (high vs low) is never recorded. It is a factor-of-2 in the
   counts-to-Kelvin conversion, so a mis-recorded gain is a catastrophic error,
   not a subtle one. I want it logged at the top of every run. Any objection?
>A. No objection

**D. FFC**

9. The Round-1 doc says "the camera FFCs every 16 frames". At 60 Hz that would be
   an FFC every 0.27 s, which I do not believe — I suspect that is the duplicate-frame
   pattern, not a shutter event. Can Rob/Christian confirm what was actually observed?
   The checklist's handling of FFC depends on the answer.
>A. [RW/CP] 
-> RW: Unless set to a manual mode by the user, the boson intelligently fires FFC as needed, which is called External Mode. Using the Boson's SDK and Manual Mode, we can sample the temperature sensor and trigger a FFC. In External Mode, the boson ignores the internal shutter and runs FFC on the scene. The observed video frame freeze is simple: video output is paused during FFC on the GUI app. 

10. The Day-2 checklist says "Set FFC interval -> one that doesnt mess up testing".
    Which do you want: FFC *disabled* during a recording (clean, but drift accrues),
    or FFC on a **manual** trigger at known timestamps we log and exclude in analysis?
    *Recommendation: manual, logged. It is the only version where we can measure
    drift and correct for it rather than hoping it cancels.*
>A. [RW/CP]
-> CP: FFC that is manually triggered at a known time stamp, we need to be able to manually trigger FFC during flight for optimal performance.
-> RW: Other tests we need to run also involve disabling FFC entirely, separate tests for different performance metrics of the camera.
         For example, we will need to test how error increases with thermal drift across the entire operating temperature range of the camera, meaning FFC
         must be disabled for such a test to be relevant.

11. Round 1 says "when the boson is not focusing on something ... everything will
    seem warmer" and that FFC removes drift when the object is out of focus. The
    Boson is normally fixed-focus, so I think this is describing a scene-dependent
    (non-uniformity / narcissus) effect rather than autofocus. Do you want me to
    include a dedicated test to pin that down? It matters for the ocean, where the
    scene fills the frame uniformly and there is no "object" at all.

>A. Yes, do that

**E. Scope — the part I think is actually missing**

12. Both rounds test a hot plate. Nothing tests **water**, yet water is the target:
    it has a different emissivity (~0.99 at nadir but strongly angle-dependent),
    a cool skin layer of a few tenths of a degree, and a moving, reflecting surface.
    The earlier "Static Sensor SST Checklist" had a water/skin-layer step that has
    since dropped out. Should Round 2 add a water-bath target — ideally with a
    thermometer in the bulk and the camera viewing at a few incidence angles?
    *Recommendation: yes. This is the closest lab analogue to the actual measurement,
    and I would rather cut the distance re-test than skip it.*
>A. No, let's save that for a Round 3 of tests.

13. **Viewing angle** is untested and is the one lab result that flows straight into
    the flight plan: water emissivity falls off sharply beyond ~40 degrees from nadir,
    which bounds the usable swath. Can we mount the camera to view the target at,
    say, 0 / 20 / 40 / 60 degrees? *Recommendation: yes, second priority after the
    water bath.*
>A. No, let's save that for a Round 3 of tests.

14. The wind test: "Low / Medium / High" fan settings are not a measurable quantity.
    Do we have an anemometer? If not I will record fan setting + distance and label
    the result qualitative. Also — is the intent to test wind cooling the *target*
    (a real evaporative effect on water, which is physics we want) or wind cooling
    the *camera housing* (an instrumental effect)? Those need different setups and
    the doc does not distinguish them.
>A. [RW/CP]

-> RW: Both, flying at the B.S cruise speed of 18 m/s while the camera is attatched to the nose cone will introduce fast, moving air over the camera, which
      will certainly introduce a non-zero amount of cooling effect on, at the very least, the camera's body and lens.
      We need to be able to understand what about, and how are our measurements change with both of these variables.
      Further, if an anemometer is found, fan speed will be denoted. If not, qualitative is the way we will be denoting fan speed, we can also reference the fan model's docs if available to say "Speed Setting X" ≅ N mph.

**F. Logistics for the deliverable**

15. **Format and location**: both existing docs are `.docx` uploads in the Lab Tests
    folder, owned by chsepere@ucsc.edu. Do you want the checklist as (a) a native
    Google Doc I create in that folder, (b) a `.docx` matching the existing pattern,
    or (c) a Markdown file in this repo that gets mirrored to Drive? I lean (a) for
    editability in the field, with a copy committed here as the version of record.
>A. (a).  Call it "Detailed Plan for Round 2 of Boson SST Tests" and put it in the "GDrive:Oceanography/Research/Calypso Monterey Bay/Sensors/SST/Lab Tests" folder.

16. **Audience and voice**: is this a checklist Rob and Christian execute
    unsupervised, bench-side? If so I will write it as strict numbered steps with
    explicit fill-in blanks and pass/fail criteria, not prose — and include a
    one-page data-recording sheet.
>A. Yes, and JXP will be with them too.

17. **Do you want the "why" in it?** A checklist that explains why each step exists
    is longer but survives contact with a student who hits something unexpected.
    *Recommendation: yes, as short bracketed notes.*
>A. Yes

18. **Schedule and effort**: the Undergrad Team notes point at the week of
    2026-10-26 or shortly after. Everything above is roughly a full day of bench
    time, maybe two. If that is too much, tell me and I will cut — my priority
    order would be: reference thermometer > water bath > randomised increments >
    viewing angle > wind > distance re-test.
>A. We are planning to do this in a few hours on 2026-09-24.  Is that enough (without the Round 3 tests)?

19. **Where does the raw data go?** Nothing in either doc says. Proposed convention:
    `data/lab_tests/2026-MM-DD/<run_id>/` with the TIFF sequence, the `fpatemp.py`
    CSV, and a `run.yaml` of the metadata the checklist collects — so
    `process_thermal_data.py` can be pointed at a run without anyone guessing.
    Does that fit how you want the repo organised?

I have not created anything in Drive yet, per the instruction to discuss first.

>A. The data should be in the `Lab Tests` folder.


### Sensor

1. Read this doc. Execute the 1st task under "Sensor / Tasks".
2. Read this doc. Execute the 2nd task under "Sensor / Tasks".

### Platform (UAV)

1. Read this doc. Execute the 1st task under "Platform / Tasks".
2. Read this doc. Execute the 2nd task under "Platform / Tasks".

### Flight Planning

1. Read this doc. Execute the 1st task under "Flight Planning / Tasks".
2. Read this doc. Execute the 2nd task under "Flight Planning / Tasks".

### In-situ Coordination

1. Read this doc. Execute the 1st task under "In-situ Coordination / Tasks".
2. Read this doc. Execute the 2nd task under "In-situ Coordination / Tasks".

## Sensor

We need to identify the sensor (or sensors) used to measure Sea Surface
Temperature, and understand what it requires of the platform and flight plan.
Candidate classes include thermal-infrared (TIR) radiometers/cameras and
companion ocean-color sensors already considered for the Calypso project.

### Tasks

1. Survey the candidate SST sensors, drawing on the added papers and the
   `flight-plan` repository (which already references an ocean-color + SST
   payload). For each candidate, summarize: measurement principle (e.g. TIR),
   accuracy/precision, spatial/spectral characteristics, mass/power/size,
   calibration needs, and any glint/atmospheric considerations. Write a
   "Sensor" section in the design document with a comparison table. Ask any
   questions in the Sensor / Q&A section below. Log your work.

2. Read my answers in the Sensor / Q&A section. Edit the Sensor section to
   reflect the decisions (including the chosen sensor and its requirements on the
   platform and flight plan). Bump the version. Log your work.

### Q&A

## Platform (UAV)

We need to identify the UAV that will carry the sensor. The `flight-plan`
repository currently targets a **BlackSwift S2** fixed-wing UAV; this task
confirms or revisits that choice in light of the sensor requirements.

### Tasks

1. Examine the platform assumptions in the `flight-plan` repository and the added
   papers. Summarize the candidate UAV(s) and their key specifications (endurance,
   range, payload mass/power, ceiling, launch/recovery method, regulatory class).
   Check that the chosen sensor's mass/power/size and pointing/glint needs are
   compatible. Write a "Platform" section in the design document. Ask any
   questions in the Platform / Q&A section below. Log your work.

2. Read my answers in the Platform / Q&A section. Edit the Platform section to
   reflect the decision and note any constraints it imposes on the flight plan.
   Bump the version. Log your work.

### Q&A

## Flight Planning

We need to decide where to fly within Monterey Bay to collect the SST data.
The `flight-plan` repository already builds a sun-aware lawnmower grid centered on
the **M1 mooring**; this task defines and justifies the target region(s) and
sampling pattern.

### Tasks

1. Using the `flight-plan` engine, the M1 mooring location, and the added papers,
   propose the flight region(s) within Monterey Bay and the sampling strategy
   (grid extent, leg spacing/resolution, altitude, glint-avoidance geometry,
   time-of-day windows, and how the region relates to in-situ assets). Write a
   "Flight Planning" section in the design document, including a map or
   description of the proposed area(s). Ask any questions in the Flight Planning /
   Q&A section below. Log your work.

2. Read my answers in the Flight Planning / Q&A section. Edit the Flight Planning
   section to reflect the decisions. Bump the version. Log your work.

### Q&A

## In-situ Coordination

We need to plan how the airborne SST collection coordinates with in-situ
measurements for calibration and validation (e.g. the M1 mooring, shipboard or
small-boat measurements, drifters).

### Tasks

1. Identify the available in-situ SST sources for Monterey Bay (starting with the
   M1 mooring) and propose how to coordinate the flights with them: spatial/temporal
   match-up criteria, what variables to record, calibration/validation procedure,
   and any logistical coordination. Write an "In-situ Coordination" section in the
   design document. Ask any questions in the In-situ Coordination / Q&A section
   below. Log your work.

2. Read my answers in the In-situ Coordination / Q&A section. Edit the section to
   reflect the decisions. Bump the version. Log your work.

### Q&A

## Logging

The "Logs" section will record Claude's work. Please use the following format:

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

...

## Logs

### 2026-09-23 (Lab work #1: read both Boson lab-test docs; questions posed for the Round-2 checklist)

Executed the 1st task under "Prompts / Lab work". Located
`GDrive:Oceanography/Research/Calypso Monterey Bay/Sensors/SST/Lab Tests` and read
both documents in it: **"Boson Experiment"** (the 2026-08-02 first session, with
results) and **"Boson Experiment 2"** (the Day-2 plan, an empty-template rerun plus
a new wind test). Also read the three analysis scripts already in this repo
(`boson_roi_stats.py`, `process_thermal_data.py`, `fpatemp.py`) and, for scheduling
and personnel context, the "2026 CMB Undergrad Team" and "SST Test Flight ToDo"
Drive docs.

**What Round 1 established.** Setup: FLIR Boson viewing a hot plate covered in black
electrical tape (bare plate read ~10 C low from specular reflection — a real and
well-caught result), 30x30-pixel centred ROI, TIFF sequences reduced frame-by-frame
in Python. Two experiments: a distance sweep at 15/30/45 cm with the plate at 35 C,
and a 1 C increment sweep from 35 to 40 C at 30 cm averaging 10 frames per step.

**What I found on reducing those numbers** (written to
`analysis/lab_tests/expt1_reported_stats.py` rather than done in chat, per the
repo convention):

- The distance sweep gives means of 34.52 / 35.17 / 34.79 C — a 0.65 C spread that
  is *non-monotonic* in distance. That is an uncertainty floor, not a distance
  term; the experiment as designed could not have detected one.
- The increment sweep has bias −1.36 C and scatter 0.56 C rms, with measured steps
  of +1.34, +0.21, +1.69, **−0.29**, +2.41 C. One step in five runs backwards, so a
  1 C change is not resolvable step-by-step on these data. Critically, the commanded
  temperature rose monotonically *in time*, which makes thermal drift completely
  degenerate with a gain error — the ramp as run cannot separate them. This is the
  single most important design flaw to fix in Round 2, and the fix is cheap:
  randomise the setpoint order and return to a fixed anchor temperature between steps.
- The quoted per-pixel noise (0.083 / 1.011 / 0.103 C) has a middle value 10x its
  neighbours; I read it as a typo for 0.101. Taking ~0.1 C per pixel, the median of
  a 30x30 ROI averages down below 0.01 C — which means **the ~1 C scatter is not
  sensor noise at all**. It is target and scene systematics: emissivity of the tape,
  reflected background, plate non-uniformity, FFC state, drift. Round 2 should be
  built to attack those; re-measuring noise would be wasted bench time.

**Assessment of the Day-2 plan.** As written it largely repeats Round 1 and appends
a wind test, so my expectation is that it reproduces the same ~1 C floor. The
binding gap is that there is still **no independent thermometer** anywhere in the
experiment — the hot-plate dial is standing in for truth, and a dial reports the
heater element rather than the tape surface. Until that is fixed, Round 2 measures
repeatability, not accuracy. Two further gaps: nothing records the reflected
background temperature (without which no emissivity correction is possible) or the
camera gain state (a factor of 2 in the counts-to-Kelvin conversion); and neither
round tests **water**, which is the actual target and differs from a hot plate in
emissivity, angular dependence, cool-skin structure and surface motion. Viewing
angle is likewise untested and is the lab result that feeds most directly into the
flight plan, since water emissivity falls off sharply beyond ~40 degrees from nadir
and therefore bounds the usable swath.

**Deliverable status.** Per the prompt's instruction to discuss before writing,
I created nothing in Drive. Instead I wrote 19 questions into the Lab work / Q&A
section above, grouped as: the missing reference thermometer (A), emissivity and
reflected background (B), design confounds — randomisation, settling time, gain
logging (C), FFC behaviour, including scepticism of the reported "FFC every 16
frames" (D), scope, i.e. adding water-bath and viewing-angle tests (E), and
logistics — Drive format, audience, schedule, and a proposed
`data/lab_tests/<date>/<run_id>/` layout (F). Each carries my recommendation so
JXP can confirm or redirect quickly. I also supplied a priority order in case bench
time is short: reference thermometer > water bath > randomised increments > viewing
angle > wind > distance re-test. Awaiting answers before drafting the checklist.
