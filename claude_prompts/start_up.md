# Getting started 

## Goals

This repository will be used to organize and enable our tests to collect data of Sea Surface Temperature (SST) for the Calypso Monterey Bay project.

## Prompts

1. Read this file.  Execute the 1st task under "Claude/CLAUDE.md file"
2. Read this file.  Execute the 1st task under "Skills"
3. Read this file.  Execute the 1st task under "Basic start up"
4. Read this file.  Execute the 1st task under "Planning"

## Claude

### CLAUDE.md file

1. Please generate a basic CLAUDE.md file for this project.  Have it indicate:

    - I will perform git commands

### Skills

1. Copy over the skills/ files from the IOPtics repository.

### Settings

## Basic start up

1. Generate the basic files that one needs for a Python GitHub repository, e.g. a file for dependencies.  Examine the other Repositories in Oceanography/python to see how I tend to organize things.  Also, make a suggestion of which of their settings.json files to copy into this one.

## Planning

1. Examine the prompt docs in the claude_prompts/ folders of the repositories in Oceanography/python to see how I tend to plan my work.  With those as a guide, generate a planning.md prompt file in this folder.  It should:

    - Indicate the goals of the project.  These are:
       - Organize and enable our tests to collect data of Sea Surface Temperature (SST) for the Calypso Monterey Bay project.
    - Suggest files to include for Context.  I will add a number of papers on previous efforts.
    - Include work to identify the sensor to use.  And the UAV
    - Include work to identify where to fly within Monterey Bay.
    - Include work on coordinating with in-situ measurements

Log your work in the Logs section below.

### Report

## Logging

The "Logs" section will record Claude's work.  Please use the following format:

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

...

## Logs

### 2026-06-20 (Planning #1: generated claude_prompts/planning.md)

Executed the 1st task under "Planning". First studied how JXP structures his
prompt docs by reading the `claude_prompts/`/`prompts/` folders across the
`Oceanography/python` repositories — most informatively `IOPtics/design_prompts.md`
and `PAB/design_prompts.md`. Their shared template: `# Title` → `## Goals`
(bulleted) → `## Claude` › `### Skills` ("Consider using the skills in
.claude/skills/") → `## Context` (files/resources to examine) → `## Overview`
(guidelines for the output design doc, with version/date/authors) → `## Prompts`
(numbered "Read this doc. Execute the Nth task under <Section>") → per-topic
sections each carrying a `### Tasks` list and a `### Q&A` (or `### Conversation`)
block where Claude poses questions and JXP answers inline → `## Logging` (the
date/summary format) → `## Logs`. The workflow is iterative: each task drafts or
edits a section of a single `docs/design/<name>_design.md`, asks questions, bumps
a version, and logs.

Created `claude_prompts/planning.md` following that template. It states the
project goal (organize/enable SST data collection for Calypso Monterey Bay),
points Context at the papers JXP will add (`docs/PDFs/`) and — a key find — the
existing `flight-plan` repository in this CMB project, which already encodes a
working sun-aware flight engine (BlackSwift S2 fixed-wing UAV, 135°-from-sun
glint-avoidance science legs, lawnmower grid centered on the MBARI **M1
mooring**). That repo directly informs the requested work items, which I turned
into four sections — **Sensor**, **Platform (UAV)**, **Flight Planning** (where to
fly in Monterey Bay), and **In-situ Coordination** — each with Tasks + Q&A. The
prompts drive building `docs/design/SST_design.md`. Did not run any git commands
(per CLAUDE.md, JXP handles git).
