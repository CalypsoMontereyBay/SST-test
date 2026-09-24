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

2. We have answered your questions in the Q&A section below.  Please read those answers and see if you have any further questions.  If so, ask them in the Q&A section below.  Use Opus 5. Log your work.

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

>A. (1) Yes, we will have a contact thermometer attached or use a thermal gun; (2) We do not have a proper calibrated blackbody, or a blackbody at all. 

**B. Emissivity and reflected background**

3. Round 1 found the bare plate read ~10 C low from specular reflection, fixed by
   black electrical tape. But the tape's emissivity was never measured — it is
   assumed. The earlier "Static Sensor SST Checklist" says to set emissivity 0.98
   *in the FLIR GUI*; as far as I can tell the Boson's TLinear output has no
   user emissivity setting, so that correction has to happen in our analysis
   instead. Is that your understanding too? Should the checklist record raw
   TLinear and apply emissivity in post, rather than trying to set it on the camera?
>A.   Should be verified, but yes, if user-side emissivity settings don't exist in the gui, we must correct in post.  However, if they exist in the SDK, we should set it in camera using software for the real missions.

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
>A.  Unless set to a manual mode by the user, the boson intelligently fires FFC as needed, which is called External Mode. Using the Boson's SDK and Manual Mode, we can sample the temperature sensor and trigger a FFC. In External Mode, the boson ignores the internal shutter and runs FFC on the scene. The observed video frame freeze is simple: video output is paused during FFC on the GUI app. 

10. The Day-2 checklist says "Set FFC interval -> one that doesnt mess up testing".
    Which do you want: FFC *disabled* during a recording (clean, but drift accrues),
    or FFC on a **manual** trigger at known timestamps we log and exclude in analysis?
    *Recommendation: manual, logged. It is the only version where we can measure
    drift and correct for it rather than hoping it cancels.*
>A. FFC that is manually triggered at a known time stamp, we need to be able to manually trigger FFC during flight for optimal performance.  Other tests we need to run also involve disabling FFC entirely, separate tests for different performance metrics of the camera.  For example, we will need to test how error increases with thermal drift across the entire operating temperature range of the camera, meaning FFC must be disabled for such a test to be relevant. Knowing how External Mode works should potenially inform future tests.

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
>A. Both, flying at the BlackSwift S2 cruise speed of 18 m/s while the camera is attatched to the nose cone will introduce fast, moving air over the camera, before ever accounting for wind direction and speed. This will certainly introduce a non-zero amount of cooling effect on, at the very least, the camera's body and lens. We need to be able to understand what about, and how are our measurements change with both of these variables. An anemometor will be available for the experiment to measure and set wind speed.

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

---

**Claude, 2026-09-23 (round 2) — follow-ups after reading your answers.**

Thank you — those resolve most of it. Round 3 taking the water bath and the
viewing-angle sweep is the right call, and it makes the day tractable. Five
things changed enough to need another pass, and I have put the schedule
arithmetic in `analysis/lab_tests/round2_time_budget.py` so the numbers below
are reproducible rather than asserted.

**G. Answering your question in Q18 — will it fit in a few hours?**

20. **Not as currently specified: I get ~5.0 hours.** The budget breaks down as
    45 min setup + 50 min drift test + 132 min increment sweep + 20 min distance
    + 22 min wind + 30 min teardown/offload. The increment sweep dominates
    because 6 setpoints plus 5 anchor returns at a 10-min settle is 11 dwells.
    Three levers bring it down, and the first is free:
    - **A contact probe collapses the settle time.** With a probe on the target
      surface we no longer wait for the plate to *reach* the dial value — we wait
      only until the surface is *stable* (say <0.1 C drift over 60 s), and we
      record the probe reading as truth whatever it says. That alone takes the
      sweep from 132 to 55 min and the day from 5.0 to **3.7 h**.
    - Anchoring only at the start and end rather than between every step, and
      dropping the distance re-test (see Q25): **3.1 h**.
    - Deferring the FFC-disabled drift test to its own session: **2.3 h**.

    My recommendation is the **3.1 h version** — it keeps everything that is
    diagnostic and drops only the re-test I think is confounded anyway. But 3.1 h
    of *bench* time with no slack, on a rig being assembled for the first time in
    this configuration, realistically means a half day. Is that what "a few hours"
    means, or do we need the 2.3 h version? If it is the latter, I would move the
    drift test rather than cut the anchors.
>A. Agreed, let's do the 3.1 h version.

21. Your Q10 answer **added scope** I had not budgeted: the FFC-disabled
    thermal-drift test. It is worth doing, but it carries a sequencing constraint
    that shapes the whole day — see Q24.
>A. ok

**H. The reference thermometer — one concern with your Q1 answer**

22. You said "a contact thermometer attached **or use a thermal gun**". These are
    not interchangeable, and I want to flag it before tomorrow. A thermal (IR)
    gun is *another radiometer*, looking at the same surface with the same unknown
    emissivity, typically spec'd at ±2 C. Calibrating the Boson against it is
    circular: a shared emissivity error cancels out of the comparison and we would
    conclude the Boson is fine when it is not. The contact probe is the only
    option here that is genuinely independent. **Can a K-type thermocouple and
    reader be sourced today?** They are ~$25 and often already in a lab drawer —
    worth asking BELS or Steve McGuire's group this afternoon. If it truly cannot
    be found by tomorrow, I will write the checklist with the gun as a
    *cross-check* rather than a reference, and label every accuracy number in the
    output as uncalibrated. I would rather say that up front than discover it in
    the analysis.
>A. Ok, we will find a contact probe.

23. Minor, but it affects one checklist line: a probe taped *under* the black tape
    reads the plate/tape interface, not the radiating surface. At 35–40 C the
    gradient is small, but do you want the probe under the tape (protected, reads
    slightly hot) or on top at the frame edge just outside the ROI (reads the true
    radiating surface, but is itself in the image)? *Recommendation: on top, just
    outside the ROI — and it doubles as a visible landmark in the frame.*
>A. I think we are going to remove the tape.  Do you agree?

**I. FFC mode — I want to check one thing in your Q9 answer**

24. Your description of External mode matches mine, with one consequence worth
    stating: because External mode computes the correction **from the scene**, any
    structure in that scene gets burned into the flat field. Over open ocean the
    scene really is near-uniform, so External is a sensible *flight* strategy. On
    the bench, pointed at a hot plate against a structured room, it would inject
    exactly the artefact we are trying to measure. So for the lab I want
    **Manual mode with the internal shutter** (a genuinely uniform reference),
    triggered at logged timestamps. Agreed? This is a one-line change but it
    changes what every run means.
>A. Agreed, let's do the Manual mode with the internal shutter.

25. **Sequencing constraint.** The drift test needs the camera to start *cold*, and
    once it is warm a cold start cannot be recovered in a session. Every other test
    wants the opposite — a thermally settled camera. So the drift test must run
    **first, from power-on**, which means the Boson should arrive unpowered and
    stay unplugged through rig assembly. Can you make sure it is not left running
    during setup? It is the easiest way to lose the test.
>A. Yes, add this to our checklist and plan

26. Also on the drift test: you wrote "across the entire operating temperature
    range of the camera". That range is roughly −40 to +80 C ambient and needs an
    environmental chamber — not achievable on a bench tomorrow. What *is*
    achievable, and I think is what you want, is the **warm-up transient**: FFC
    disabled, camera cold, staring at a stable target while the FPA climbs to
    equilibrium (typically 10–20 C above ambient over ~30–45 min), with
    `fpatemp.py` logging throughout. That gives us drift-vs-FPA-temperature over
    the range the camera will actually self-generate. Confirm that is the intent?
>A. We confirm

**J. Two design problems I found while writing this up**

27. **The distance test and the scene-fill test are the same test.** Moving the
    camera from 15 to 45 cm changes the stand-off *and* the fraction of the frame
    the hot plate fills. So Round 1's "distance" result was never a clean distance
    measurement — it is entangled with exactly the scene-fill effect you asked me
    to pin down in Q11. Two ways out: hold the fill fraction constant while varying
    distance (scale the target), or hold distance constant and vary the surround
    (mask the plate down, or change what is around it). *Recommendation: drop the
    distance re-test as such, and run Q11's scene-fill test properly at fixed
    distance — it answers the question that actually matters for the ocean, where
    the scene fills the frame uniformly and there is no "object" at all.* Do you
    agree, or do you want distance kept for continuity with Round 1?
>A. Ok, use your recommendation.

28. **The wind test needs the contact probe to be interpretable at all.** Blowing
    room-temperature air at a 35 C plate will cool *the plate*, possibly by several
    degrees. Without a probe on the target we cannot tell target cooling from
    camera cooling — the two effects you said in Q14 you want to separate. With a
    probe we can: the probe gives the target's true temperature, so any residual
    discrepancy is instrumental. Proposed four configs rather than the full grid:
    fan on **camera only** (target shielded) at low/med/high, plus fan on **target
    only** (camera shielded) at high as a check. Reasonable?
>A. Yes, this is reasonable.

29. Related: a household fan moves perhaps 2–5 m/s, against the BlackSwift's 18 m/s
    cruise. So this test establishes the **sign and rough scaling** of the effect,
    not its flight magnitude, and I will label it that way. Is there a stronger
    airflow source available (shop blower, ducted fan)? If not, we extrapolate and
    say so.
>A. Agreed, count on not having access to a stronger fan for now.

**K. Data volume — this one is urgent and nobody has costed it**

30. Your Q19 answer puts the data in the Drive `Lab Tests` folder. At Boson 640 and
    60 Hz, a single 2-minute capture of 16-bit TIFFs is **4.7 GB**, and a full day
    of ~15 runs is **~71 GB**. That will not fit in a Drive folder in any practical
    sense, and the upload would outlast the experiment. Options, in my order of
    preference: capture at a **reduced frame rate** (thermal drift is slow — 2 Hz
    keeps everything we need at ~1/30 the volume, 0.16 GB/run), or capture fast and
    **decimate on the bench** before anything leaves the laptop. Which do you want?
    This has to be decided *before* the session.
>A. 70Gb is fine

31. To size that properly I need two facts I do not have: **is this a Boson 640 or
    320, and is it the 60 Hz or the 9 Hz variant?** The table in
    `round2_time_budget.py` spans 0.18 to 4.72 GB per run across those four cases —
    a 26x range, so it is not a detail.
>A. Boson R 640 x 512, 60 Hz variant.

32. Given the above, my proposal for Q19: **reduced products and metadata to Drive**
    (per-run CSVs, the `fpatemp.py` logs, the recording sheet, a few sample frames),
    **raw TIFFs to an external SSD or the lab machine**, with the Drive folder
    holding an index of what lives where. Does that work, or do you specifically
    want raw frames in Drive?
>A. Again, 70Gb is no problem

**L. Two loose ends**

33. On Q3 — for the *real missions* you suggested setting emissivity in-camera via
    the SDK. I would push back gently: baking an emissivity correction into the
    recorded data is irreversible, and if we later revise our value for water's
    emissivity (likely, given the angular dependence we will measure in Round 3)
    the archived data cannot be recovered. *Recommendation: always record raw
    TLinear and apply emissivity in post, in-camera setting used only for the live
    display.* Also — who is verifying whether the SDK exposes emissivity at all
    before tomorrow? That is a 10-minute desk check, not a bench task, and the
    checklist wording depends on it.
>A. Ok, and add to the checklist and plan

34. Practical: is there a confirmed **Windows machine with the Boson GUI/SDK
    working** for tomorrow? Round 1 needed a borrowed BELS laptop, and "make sure
    usb is talking to VM" appears in the Round-1 scratch notes as a live problem.
    If that is still unsettled I will put it at the top of the checklist as a
    blocking pre-flight item with a fallback.
>A. Confirmed

Still nothing created in Drive — I will draft "Detailed Plan for Round 2 of Boson
SST Tests" in the Lab Tests folder once these are settled. The ones that genuinely
block drafting are **Q20** (which scenario), **Q22** (probe or not), **Q30/31**
(capture rate and camera variant); the rest I can write around with a stated
assumption if you would rather I just go.

**Claude, 2026-09-23 (reconciliation) — after merging Rob's refinements to Q2, Q10 and Q14.**

Rob revised three answers while I was drafting the follow-ups above. They merge
cleanly with my additions (no textual conflict), but two of them partly overtake
questions I had already asked, so I am marking those rather than leaving you to
answer something already settled.

- **Q29 is largely answered — an anemometer was found.** That is a real upgrade:
  the wind test now produces a calibrated trend against *measured* m/s instead of
  "low / medium / high", which is the difference between a result we can cite and
  an anecdote. What it does **not** do is extend the range — an anemometer measures
  the fan, it does not make the fan faster. A household fan tops out around 2–5 m/s
  against the S2's 18 m/s cruise, so we will still be extrapolating roughly 4–9x
  beyond our measured span. The remaining question is narrower than Q29 as written:
  **what is the fan's top speed measured at the camera position?** Please have
  someone take that one reading early, because it sets how honest the extrapolation
  can be — and if it comes in near 5 m/s, it is worth a sentence in the write-up
  saying so explicitly rather than implying flight-relevant coverage.
- **Q24 is revised, not withdrawn.** Rob's point that External-mode behaviour
  "should potentially inform future tests" is right, and it is compatible with my
  recommendation once the two uses are separated. External mode computes its flat
  field *from the scene*, so running it during a science capture injects exactly
  the artefact we are trying to measure — but characterising it deliberately, in
  its own block, is valuable and is the only way we learn whether it is safe to
  rely on in flight. **Proposal: Manual + internal shutter for all measurement
  runs, plus a dedicated ~15-minute External-mode block.** I have added that to
  `round2_time_budget.py` as scenario C+, which comes to **3.4 h** (vs 3.1 h for C).
  Agreed?
- **Q2's refinement ("or a blackbody at all") changes nothing in my list, but it
  raises the stakes on Q22.** With no blackbody anywhere on campus, the contact
  probe is not merely the better reference — it is the *only* independent reference
  we will have tomorrow. If it cannot be sourced today, Round 2 has no absolute
  calibration at all and every accuracy number must be reported as relative.

So the still-open blockers are unchanged in substance: **Q20** (which scenario —
now C or C+), **Q22** (probe sourced today, yes or no), and **Q30/Q31** (capture
rate and Boson variant).




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

### 2026-09-23 (Lab work #2: read JXP's Q&A answers; posed follow-up questions and a schedule/data budget)

Executed the 2nd task under "Prompts / Lab work". Read JXP's answers to all 19
questions and worked through their consequences. Most are settled: Round 3 will
take the water bath and the viewing-angle sweep (Q12/Q13), randomised setpoints
with anchor returns are approved (Q6), 10-min settle + 2-min record with
`fpatemp.py` logging is approved (Q7), gain state will be logged (Q8), the
reflected-background foil step is in (Q4), manual logged FFC is confirmed (Q10),
and the deliverable is a native Google Doc named "Detailed Plan for Round 2 of
Boson SST Tests" in the Lab Tests folder, written as bench-side numbered steps
for Rob and Christian with JXP present, with short bracketed rationale (Q15–Q17).

**The direct question in Q18 — does it fit in a few hours on 2026-09-24?**
I costed it in `analysis/lab_tests/round2_time_budget.py` rather than guessing.
As specified it is **~5.0 h**, not a few hours. The increment sweep dominates at
132 min, because 6 setpoints plus 5 anchor returns at a 10-min settle is 11
dwells. The key realisation is that **the contact probe removes the need for a
long settle at all**: with truth read off the probe we stop waiting for the plate
to reach the dial value and wait only until the surface is stable, which takes the
day to 3.7 h; dropping to bracketing anchors and cutting the distance re-test
gives 3.1 h; deferring the drift test gives 2.3 h. I recommended the 3.1 h version
while noting that 3.1 h of bench time on a first-time rig realistically means a
half day. JXP's own Q10 answer also added unbudgeted scope — the FFC-disabled
drift test — which is worth doing but carries a sequencing constraint.

**Five substantive issues raised as follow-ups Q20–Q34:**

- **The thermal gun is not a reference (Q22).** JXP's Q1 answer offered "contact
  thermometer *or* thermal gun" as equivalent. They are not: an IR gun is another
  radiometer viewing the same surface with the same unknown emissivity, so a
  shared emissivity error cancels out of the comparison and we would wrongly
  conclude the Boson is accurate. Only the contact probe is independent. Since the
  test is tomorrow, I flagged sourcing a K-type thermocouple as urgent and
  same-day, with a fallback of labelling all accuracy numbers uncalibrated.
- **Distance and scene-fill are the same test (Q27).** Moving the camera changes
  stand-off *and* the fraction of frame the plate fills, so Round 1's distance
  result was always entangled with the scene-fill effect JXP asked me to isolate
  in Q11. Recommended dropping the distance re-test and running the scene-fill
  test properly at fixed distance, varying the surround — which is the version
  that bears on the ocean, where the scene is uniform and there is no "object".
- **The wind test is uninterpretable without the probe (Q28).** Room-temperature
  air on a 35 C plate cools the plate; without target truth we cannot separate
  target cooling from camera cooling, which is exactly the separation JXP asked
  for in Q14. Proposed four shielded configs instead of the full grid, and noted
  that a household fan at 2–5 m/s against an 18 m/s cruise gives sign and scaling
  only, not flight magnitude.
- **Data volume is unbudgeted and large (Q30–Q32).** Q19's answer puts data in the
  Drive folder, but at Boson 640/60 Hz one 2-minute TIFF capture is 4.7 GB and a
  day is ~71 GB — impractical for Drive, and the upload would outlast the session.
  Since drift is a slow signal, 2 Hz preserves everything at ~1/30 the volume.
  Proposed reduced products plus metadata to Drive and raw to external storage.
  I also asked which Boson variant this is: across 640/320 and 60/9 Hz the per-run
  volume spans 0.18–4.72 GB, a 26x range, so capture rate must be set beforehand.
- **FFC mode for the bench (Q24–Q26).** JXP's account of External mode matches
  mine, but because External computes the correction *from the scene*, structure in
  a bench scene gets burned into the flat field — sensible in flight over uniform
  ocean, harmful in a lab. Recommended Manual mode with the internal shutter for
  Round 2. Separately, the drift test needs a **cold** camera and every other test
  wants a warm one, so it must run first from power-on with the Boson unplugged
  during setup. I also noted that "entire operating temperature range" (−40 to
  +80 C) needs an environmental chamber and reinterpreted the test as the warm-up
  transient, asking JXP to confirm.

Also pushed back gently on setting emissivity in-camera for real missions (Q33):
baking it in is irreversible, and our value for water's emissivity is likely to be
revised after Round 3's angular measurements — so raw TLinear should always be the
archived product. Asked who verifies the SDK's emissivity capability before
tomorrow, and whether a Windows machine with a working GUI/SDK is confirmed (Q34),
since Round 1's scratch notes show USB/VM connectivity was an unresolved problem.

Created nothing in Drive, per the task's scope. Flagged that only Q20, Q22 and
Q30/Q31 genuinely block drafting; the rest I can write around under stated
assumptions if JXP prefers speed.

### 2026-09-23 (Merged Rob's Q&A refinements; reconciled two of my follow-ups)

JXP reported "conflicts" in `planning.md` after Rob pushed work. There were none
in the git sense: the local branch was simply 5 commits behind
`origin/thermal-testing` with my uncommitted follow-up edits on top, and nothing
had been merged yet. I verified this by replaying the merge on scratch copies with
`git merge-file` (base = HEAD, ours = working tree, theirs = origin) — it returned
exit 0, zero conflict hunks, with all three of Rob's refinements and both of my
additions present in the result. Rob touched only three lines, all inside the
original Q&A block; my edits append a follow-up section and a log entry further
down, so the two never overlap textually. Per the repo convention I ran no
state-changing git commands and left the pull to JXP, recommending
`git stash` → `git pull` → `git stash pop` as the path I had actually verified.

The genuine conflict was semantic. Rob's refinements partly overtook two questions
I had already posed, and answering them as written would have wasted JXP's time:

- **Q14 → an anemometer was found**, which largely answers my Q29. This upgrades
  the wind test from "low/medium/high" to a calibrated trend against measured m/s.
  But an anemometer measures the fan rather than speeding it up, so the ~2–5 m/s
  household-fan span against an 18 m/s cruise still leaves a 4–9x extrapolation.
  I narrowed Q29 to the one reading that now matters: the fan's top speed at the
  camera position, taken early, since it bounds how honest the extrapolation can be.
- **Q10 → Rob wants External-mode behaviour characterised**, which pushes against
  my Q24 recommendation of Manual mode on the bench. These reconcile once the uses
  are separated: External computes its flat field *from the scene*, so it must not
  run during a science capture, but characterising it deliberately in its own block
  is the only way to learn whether it can be trusted in flight. Revised Q24 to
  propose Manual for all measurement runs plus a dedicated ~15-min External block,
  and added that to `round2_time_budget.py` as scenario **C+ = 3.4 h** (vs C = 3.1 h).
- **Q2 → "or a blackbody at all"** changes no question but raises the stakes on
  Q22: with none available on campus, the contact probe is the only independent
  reference we will have, so failing to source one tomorrow means Round 2 carries
  no absolute calibration.

Open blockers unchanged in substance: Q20 (scenario C or C+), Q22 (probe sourced
today), Q30/Q31 (capture rate and Boson variant).
