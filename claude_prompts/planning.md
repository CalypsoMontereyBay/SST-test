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

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

...

## Logs
