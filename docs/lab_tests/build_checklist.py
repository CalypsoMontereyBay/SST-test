#!/usr/bin/env python3
"""Build the Round-2 Boson lab-test checklist as a .docx."""
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BLUE = RGBColor(0x1F, 0x4E, 0x79)
BLUE2 = RGBColor(0x2E, 0x5E, 0x8C)
GREY_T = RGBColor(0x59, 0x59, 0x59)
GREY_L = RGBColor(0x80, 0x80, 0x80)
SH_GREY, SH_AMBER, SH_RED, SH_GREEN, SH_BLUE = "F2F2F2", "FFF2CC", "FCE4E4", "E8F3E8", "1F4E79"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec, m, Inches(0.75))
CONTENT_IN = 7.0

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10)
st.paragraph_format.space_after = Pt(5)


def shade(cell, hexfill):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear"); el.set(qn("w:color"), "auto"); el.set(qn("w:fill"), hexfill)
    cell._tc.get_or_add_tcPr().append(el)


def runs(p, parts):
    for t, o in parts:
        r = p.add_run(t)
        r.bold = o.get("b", False); r.italic = o.get("i", False)
        r.font.size = Pt(o.get("sz", 10))
        if "c" in o: r.font.color.rgb = o["c"]
    return p


def para(parts, indent=0, after=5, before=0, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(before)
    if indent: p.paragraph_format.left_indent = Inches(indent)
    if align is not None: p.alignment = align
    return runs(p, parts)


def H1(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(15); r.font.color.rgb = BLUE
    return p


def H2(text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(11.5); r.font.color.rgb = BLUE2
    return p


def step(n, text, bold=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.first_line_indent = Inches(-0.3)
    r = p.add_run("☐  "); r.font.size = Pt(11)
    if n:
        r = p.add_run(f"{n}. "); r.bold = True; r.font.size = Pt(10)
    r = p.add_run(text); r.font.size = Pt(10); r.bold = bold
    return p


def why(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6); p.paragraph_format.left_indent = Inches(0.6)
    r = p.add_run("[ " + text + " ]"); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = GREY_T
    return p


def fill(label, unit=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3); p.paragraph_format.left_indent = Inches(0.6)
    p.add_run(label + ":  ").font.size = Pt(10)
    r = p.add_run("_" * 24); r.font.size = Pt(10); r.font.color.rgb = GREY_L
    if unit:
        r = p.add_run("   " + unit); r.font.size = Pt(9); r.font.color.rgb = GREY_T
    return p


def mktable(widths_in, header, rows, header_shade=SH_BLUE):
    t = doc.add_table(rows=1, cols=len(widths_in))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    for i, lab in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(lab); r.bold = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(hdr[i], header_shade)
    for row in rows:
        cells = t.add_row().cells
        for i, spec in enumerate(row):
            txt, o = (spec if isinstance(spec, tuple) else (spec, {}))
            cells[i].text = ""
            p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(txt); r.bold = o.get("b", False); r.font.size = Pt(o.get("sz", 9))
            if "sh" in o: shade(cells[i], o["sh"])
    for r_ in t.rows:
        for i, c in enumerate(r_.cells):
            c.width = Inches(widths_in[i])
    return t


def callout(title, lines, fillhex):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; t.autofit = False
    c = t.rows[0].cells[0]; c.width = Inches(CONTENT_IN); shade(c, fillhex)
    c.text = ""
    p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(3)
    r = p.add_run(title); r.bold = True; r.font.size = Pt(10.5)
    for ln in lines:
        p = c.add_paragraph(); p.paragraph_format.space_after = Pt(3)
        r = p.add_run(ln); r.font.size = Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def spacer(pts=8):
    doc.add_paragraph().paragraph_format.space_after = Pt(pts)


# ------------------------------------------------------------------ title
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
r = p.add_run("Boson Experiment 2 — Detailed Checklist"); r.bold = True; r.font.size = Pt(20); r.font.color.rgb = BLUE
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
r = p.add_run("Round 2 of the Boson SST lab tests"); r.font.size = Pt(12); r.font.color.rgb = GREY_T
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(10)
r = p.add_run("Version 1.0  ·  2026-09-24  ·  Calypso Monterey Bay"); r.font.size = Pt(9.5); r.font.color.rgb = GREY_L

_meta = mktable([1.7, 5.3], ["", ""], [
    [("At the bench", {"b": True, "sh": SH_GREY}), "Rob Woods, Christian Sepere, J. Xavier Prochaska"],
    [("Prepared by", {"b": True, "sh": SH_GREY}), "JXP and Claude (Opus 5)"],
    [("Camera", {"b": True, "sh": SH_GREY}), "FLIR Boson R, 640 × 512, 60 Hz variant, radiometric (TLinear)"],
    [("Planned duration", {"b": True, "sh": SH_GREY}), "3.7 h of bench time (§1 has the drop order if running late)"],
    [("Supersedes", {"b": True, "sh": SH_GREY}), "“Boson Experiment 2” (Day-2 plan). Round 1 = “Boson Experiment”, 2026-08-02."],
], header_shade="FFFFFF")
# drop the placeholder header row - this table is a key/value block, not a grid
_meta._tbl.remove(_meta.rows[0]._tr)
spacer(6)

H1("What Round 2 is for")
para([("Round 1 established that the Boson tracks temperature but could not resolve 1 °C steps: the residual scatter was 0.56 °C rms and one step of five ran backwards. Reducing those numbers showed the scatter is far too large to be sensor noise — at about 0.1 °C per pixel, a 900-pixel median averages down below 0.01 °C. The limit is therefore not the detector. It is the target and the scene: emissivity, reflected background, plate non-uniformity, FFC state and thermal drift.", {})])
para([("Round 2 is built to attack those systematics rather than re-measure noise. Three changes carry most of the weight:", {})])
para([("A contact probe on the target. ", {"b": True}), ("Round 1 used the hot-plate dial as truth, but a dial reports the heater element, not the radiating surface. The probe is the only independent reference we have — there is no blackbody available on campus.", {})], indent=0.3)
para([("Randomised setpoint order with anchor returns. ", {"b": True}), ("Round 1 ramped 35→40 °C monotonically in time, which makes drift and a gain error mathematically indistinguishable. Randomising separates them.", {})], indent=0.3)
para([("Manual FFC at logged timestamps. ", {"b": True}), ("This is what lets us measure drift and correct for it, instead of hoping it cancels.", {})], indent=0.3)
para([("Water targets and the viewing-angle sweep are deliberately deferred to Round 3.", {"i": True})], after=8)

callout("Five rules that decide whether today's data is usable", [
    "1.  The camera stays UNPOWERED until test T1 begins. T1 needs a cold start, and once the camera is warm a cold start cannot be recovered in a single session.",
    "2.  KEEP the black tape on the hot plate. Bare metal reads about 10 °C low and, worse, shrinks a real 1 °C step to about 0.24 °C — a 4× loss of signal that no probe can repair. See §9.",
    "3.  Manual FFC for every science run, and write down the timestamp of each FFC.",
    "4.  Nobody stands in front of the rig during a capture. A person is a 30 °C reflector; this cost Round 1 an afternoon.",
    "5.  Record the gain state (high or low) on every single run. It is a factor of 2 in the counts-to-Kelvin conversion, so getting it wrong is catastrophic, not subtle.",
], SH_AMBER)

# ------------------------------------------------------------------ 1
H1("1.  Schedule and drop order")
mktable([0.6, 3.1, 0.8, 2.5], ["Block", "What", "Time", "Notes"], [
    [("Pre", {"b": True}), "Pre-flight setup", "45 min", "Camera stays unpowered throughout"],
    [("T1", {"b": True}), "Warm-up drift, FFC disabled", "50 min", ("MUST run first, from a cold camera", {"b": True})],
    [("T2", {"b": True}), "1 °C increment sweep, randomised", "40 min", "The core result of the day"],
    [("T3", {"b": True}), "Scene-fill / narcissus", "20 min", "Replaces the Round-1 distance test"],
    [("T4", {"b": True}), "Wind", "22 min", "Needs the anemometer"],
    [("T5", {"b": True}), "External-mode FFC characterisation", "15 min", "Drop this first if time runs short"],
    [("Post", {"b": True}), "Teardown and data handling", "30 min", "Bulk upload runs afterwards, not now"],
    [("", {"sh": SH_GREY}), ("TOTAL", {"b": True, "sh": SH_GREY}), ("3.7 h", {"b": True, "sh": SH_GREY}), ("", {"sh": SH_GREY})],
])
spacer(6)
para([("If the day runs late, drop in this order: ", {"b": True}), ("T5 (External mode) → T3 (scene-fill) → the second anchor visit in T2. Do not cut T1 or the body of T2 — T1 cannot be re-run without another cold start, and T2 is the reason Round 2 exists.", {})])
para([("Note on the estimate: ", {"b": True}), ("this is 3.7 h, not the 3.4 h previously circulated. The earlier figure accidentally dropped the scene-fill test along with the distance re-test, because one line item covered both. The scene-fill test is the one we agreed to keep.", {})])

# ------------------------------------------------------------------ 2
doc.add_page_break()
H1("2.  Pre-flight  —  45 min, camera unpowered")
para([("Work through these in order. Do not plug in the Boson at any point in this section.", {"i": True})])

H2("2.1  Machine and storage")
step(1, "Windows machine boots; Boson GUI and SDK both launch.")
step(2, "Confirm free disk space on the capture drive.", bold=True)
fill("Free space", "GB   —  need > 100 GB")
why("At 640×512 and 60 Hz, one 2-minute capture is 4.72 GB and a full day is roughly 71 GB. A disk that fills at run 8 ends the session. If space is short, an external SSD is the fallback — sort this out before powering anything.")
step(3, "Confirm the capture disk sustains 39 MB/s. The 30-second trial capture below is the real test.")
step(4, "Create today's capture folder and note the path.")
fill("Capture path")
step(5, "Run a 30-second trial capture and COUNT THE FRAMES. Expect about 1800.", bold=True)
fill("Trial frames counted", "expected ~1800")
why("Dropped frames corrupt run timing silently — there is no error message. Catching it now costs thirty seconds; catching it in analysis costs the day.")

H2("2.2  SDK desk-check  (~10 min, can run in parallel)")
step(6, "Determine whether the Boson SDK exposes a scene-emissivity setting at all.")
fill("Emissivity setting exists?", "yes / no   —  function name if yes")
why("The GUI appears not to offer one, so emissivity has to be applied in post. If the SDK does expose it, that is useful to know for flight — but we archive raw TLinear either way, because an emissivity baked into the recording cannot be undone if we later revise our value for water.")
step(7, "Record the firmware version and confirm the unit is the radiometric (TLinear) build.")
fill("Firmware")

H2("2.3  Target rig")
step(8, "Hot plate on the bench, set to 35 °C, switched on now so it is settled by T1.")
step(9, "Black electrical tape covering the plate surface — KEEP THE TAPE.", bold=True)
why("Bare metal has emissivity around 0.2 and is mostly a mirror for the room. Beyond the 10 °C bias, it shrinks a genuine 1 °C change to about 0.24 °C at the detector. Since Round 2 exists to test 1 °C resolution, that alone would make the day unusable. Section 9 has the numbers.")
step(10, "Tape smooth and flat, no wrinkles or air gaps, no bare metal visible in the camera's field of view.")
step(11, "Contact probe in place: lead run out under the edge of the tape, sensing junction under the tape near the centre but outside the 30×30 ROI.")
why("Under the tape it reads the tape/plate interface, which at 35–40 °C sits within about 0.1 °C of the radiating face — close enough, and it keeps the probe out of the image.")
step(12, "Check the tape has reached plate temperature: warm the plate, then confirm probe and plate agree once stable.")
fill("Probe reads", "°C      Plate dial set to: ______ °C")
why("The dial and the probe will disagree. That is expected and is the whole point — from here on the PROBE is truth and the dial is just a knob.")

H2("2.4  Camera rig  (still unpowered)")
step(13, "Camera mounted 30 cm from the target, lens cap OFF, axis normal to the plate.")
fill("Measured distance", "cm")
step(14, "Mark camera and plate positions on the wooden board so the geometry can be restored exactly.")
step(15, "Crumpled-foil diffuse reflector available, sized to sit at the target position when needed.")
why("Pointing the camera at crumpled foil at the target position measures the reflected background temperature — the apparent temperature of whatever the target is mirroring. Without it no emissivity correction is possible at all.")
step(16, "Anemometer present and working; fan positioned but OFF.")
step(17, "Take setup photographs from at least three angles. Note the filenames.")
fill("Setup photos")
step(18, "Agree and write down who does what: one person drives capture, one records the sheet, one stays clear of the field of view.")

H2("2.5  Baseline readings")
fill("Room air temperature", "°C")
fill("Relative humidity", "%  (if available)")
fill("Fan top speed at the camera position", "m/s")
why("Take the fan reading now. It sets how far we are extrapolating in T4: a household fan reaching perhaps 2–5 m/s against the BlackSwift S2's 18 m/s cruise means a 4–9× gap, and we should state that honestly rather than imply flight-relevant coverage.")

# ------------------------------------------------------------------ 3
doc.add_page_break()
H1("3.  T1  —  Warm-up drift, FFC disabled  —  50 min")
callout("This test must run FIRST, from a cold camera", [
    "Every other test wants a thermally settled camera. This one wants the opposite. Once the Boson has been powered for twenty minutes, a cold start cannot be recovered today — so if the camera gets plugged in during setup, this test is lost until another session.",
], SH_RED)
para([("Goal: measure how the reading drifts as the focal plane warms from ambient to equilibrium, with FFC disabled so nothing masks the drift. This is the warm-up transient, not the camera's full −40/+80 °C rated range — that would need an environmental chamber.", {})], after=8)
step(1, "Plate at 35 °C and stable: probe drifting less than 0.1 °C over 60 s.")
step(2, "Record the foil background reading.")
step(3, "Set FFC to DISABLED.", bold=True)
step(4, "Start fpatemp.py logging AND the TIFF capture at the same moment as camera power-on. Note the wall-clock time.")
fill("Power-on time")
why("fpatemp.py polls the internal focal-plane-array temperature at 1 Hz and writes elapsed seconds, so it can be joined against the per-frame ROI analysis afterwards. Starting both together is what makes t = 0 line up in the two files.")
step(5, "Record continuously for 45 minutes without touching anything.")
step(6, "Watch the FPA temperature in the log. Stop when it has plateaued — typically 10–20 °C above ambient.")
fill("FPA at start", "°C       FPA at plateau: ______ °C")
fill("Apparent target T at start", "°C       at end: ______ °C")
spacer(4)
para([("Pass / fail: ", {"b": True}), ("the FPA temperature should rise and visibly flatten. If it is still climbing at 45 minutes, note that and carry on — it means equilibrium takes longer than expected, which is itself a useful result for flight planning.", {})])

# ------------------------------------------------------------------ 4
doc.add_page_break()
H1("4.  T2  —  1 °C increment sweep, randomised  —  40 min")
para([("This is the core measurement of the day: can the Boson resolve a 1 °C change? Round 1 said no, with 0.56 °C rms scatter and one step running backwards.", {})], after=8)

H2("4.1  Configuration")
step(1, "FFC mode: MANUAL, internal shutter.", bold=True)
why("Manual with the internal shutter gives a genuinely uniform flat-field reference. External mode computes its correction FROM THE SCENE, so on a bench pointed at a structured room it would burn that structure into the flat field — injecting the very artefact we are trying to measure. External mode gets its own separate block in T5.")
step(2, "Trigger an FFC now and write down the timestamp. Repeat before every dwell.")
step(3, "Confirm and record the gain state.", bold=True)
fill("Gain", "high / low")
step(4, "Confirm the ROI: 30 × 30 pixels (900 px), centred, median statistic. Record the corner coordinates.")
fill("ROI corners", "(x0, y0) → (x1, y1)")
why("The Round-1 notes say both “30×30 square” and “median of 115 pixels”, which disagree — 30×30 is 900 pixels. 30×30 is correct. Writing down the corners makes it reproducible instead of “the middle”.")

H2("4.2  Order of setpoints — follow this exactly")
mktable([0.6, 1.1, 0.9, 4.4], ["Dwell", "Kind", "Plate °C", "Purpose"], [
    ["1", ("ANCHOR", {"b": True, "sh": SH_GREEN}), "35", "Opening reference"],
    ["2", "setpoint", "38", ""],
    ["3", "setpoint", "40", ""],
    ["4", "setpoint", "37", ""],
    ["5", "setpoint", "36", ""],
    ["6", "setpoint", "39", ""],
    ["7", "setpoint", "35", "Third visit to 35 °C — repeatability check"],
    ["8", ("ANCHOR", {"b": True, "sh": SH_GREEN}), "35", "Closing reference"],
])
spacer(6)
why("Round 1 ramped 35→40 °C in time order, which makes camera drift and a gain error produce the same sloped residual — the data cannot tell them apart. Randomising turns drift into scatter instead of a fake slope. The two anchors bracket the run at a known identical temperature, so any difference between them IS the drift, measured directly. Generated with seed 20260924; regenerate with analysis/lab_tests/round2_setpoint_order.py if this sheet is lost.")

H2("4.3  Repeat for each of the 8 dwells")
step(5, "Set the plate to the next temperature in the table.")
step(6, "Wait until the PROBE is stable to better than 0.1 °C over 60 s. Do not wait for the dial to agree with anything.")
why("This replaces Round 1's fixed 10-minute wait. Because the probe is truth, we no longer care whether the plate reached the commanded value — only that it has stopped moving. It is also what brings the sweep from 132 minutes down to 40.")
step(7, "Trigger a manual FFC. Record the timestamp.")
step(8, "Record probe temperature, FPA temperature, and foil background reading.")
step(9, "Capture 2 minutes of TIFFs. Record the filename / folder.")
step(10, "Record the probe temperature again at the END of the capture.")
why("If the probe moved during the capture, the dwell was not settled and the point should be flagged in analysis.")
step(11, "Fill in one row of the run sheet (§8) before moving on.")

# ------------------------------------------------------------------ 5
doc.add_page_break()
H1("5.  T3  —  Scene-fill / narcissus  —  20 min")
para([("Round 1 noticed that the apparent temperature changed depending on what else was in the frame, and described it as a focus effect. The Boson is fixed-focus, so it is not focus — it is a scene-dependent non-uniformity. This test pins it down.", {})], after=6)
callout("Why this replaces the Round-1 distance test", [
    "Moving the camera from 15 to 45 cm changes the stand-off AND the fraction of the frame the hot plate fills. Those two effects were never separated, so Round 1's “distance” result was always entangled with this one. Holding distance fixed at 30 cm and varying only the surround is what isolates it — and it is the version that matters for the ocean, where the scene fills the frame uniformly and there is no “object” at all.",
], SH_GREY)
para([("Plate stays at 35 °C and settled for all four configurations. Distance stays at 30 cm. Only the surroundings change.", {"i": True})], after=8)
mktable([0.6, 2.7, 3.7], ["#", "Configuration", "What it tests"], [
    [("A", {"b": True}), "Plate alone, normal room behind", "Baseline — matches the T2 geometry"],
    [("B", {"b": True}), "Plate masked down to about 1/4 of the frame", "Small warm target in a cool field"],
    [("C", {"b": True}), "Plate surrounded by room-temperature card", "Uniform cool surround, no clutter"],
    [("D", {"b": True}), "Frame filled edge to edge by the target", "Closest analogue to looking at open ocean"],
])
spacer(6)
step(1, "For each configuration: manual FFC (log timestamp), record probe / FPA / foil, capture 2 minutes, record filename.")
step(2, "Photograph each configuration — this one is hard to reconstruct from notes alone.")
spacer(4)
para([("What we are looking for: ", {"b": True}), ("the ROI covers the same physical patch of tape at the same true temperature in all four. Any change in the reading between A, B, C and D is the scene-fill effect — and configuration D is the one that predicts what happens over water.", {})])

# ------------------------------------------------------------------ 6
H1("6.  T4  —  Wind  —  22 min")
para([("Two different effects are in play and they must be separated: wind cooling the TARGET (real physics, and over water it will be evaporative) and wind cooling the CAMERA body and lens (an instrumental artefact). In flight, 18 m/s over the nose cone guarantees the second.", {})], after=6)
para([("The contact probe is what makes this interpretable. ", {"b": True}), ("Room-temperature air on a 35 °C plate will cool the plate, possibly by several degrees. The probe tells us the target's true temperature throughout, so any remaining discrepancy in the camera's reading is instrumental.", {})], after=8)
mktable([0.5, 1.9, 1.4, 3.2], ["#", "Air directed at", "Fan setting", "Shielding"], [
    [("1", {"b": True}), "Camera only", "Low", "Target shielded from airflow"],
    [("2", {"b": True}), "Camera only", "Medium", "Target shielded from airflow"],
    [("3", {"b": True}), "Camera only", "High", "Target shielded from airflow"],
    [("4", {"b": True}), "Target only", "High", "Camera shielded from airflow"],
])
spacer(6)
step(1, "Measure and record the actual air speed with the anemometer, at the position of whatever is being cooled.", bold=True)
why("Record measured m/s, not “low / medium / high”. A number gives a trend we can cite and extrapolate; a fan setting gives an anecdote.")
step(2, "For each configuration: manual FFC (log timestamp), record probe / FPA / foil / air speed, capture 2 minutes.")
step(3, "Note the wind direction relative to the camera axis.")
step(4, "Let the rig re-stabilise between configurations — watch the probe.")
spacer(4)
para([("Honest limitation to write into the results: ", {"b": True}), ("the fan reaches a few m/s against an 18 m/s cruise, so this establishes the sign and rough scaling of the effect, not its flight magnitude. Say so explicitly rather than implying coverage we do not have.", {})])

# ------------------------------------------------------------------ 7
H1("7.  T5  —  External-mode characterisation  —  15 min  (drop first if late)")
para([("Kept deliberately separate from every measurement run above. The point is to learn how External mode behaves so we know whether it can be trusted in flight — not to use it for science data today.", {})], after=8)
step(1, "Plate at 35 °C, settled, geometry as in T2.")
step(2, "Switch FFC to EXTERNAL mode.")
step(3, "With a structured scene (plate plus normal cluttered room), trigger an FFC. Capture 1 minute.")
step(4, "Look for ghosting or burned-in scene structure in the image. Note what you see.")
fill("Ghosting observed?", "yes / no — describe")
step(5, "Now fill the frame uniformly (configuration D from T3), trigger an FFC, capture 1 minute.")
step(6, "Compare. Record which scene produced a clean flat field.")
why("External mode computes its flat field from whatever the camera is looking at. Over open ocean the scene really is near-uniform, so External may be a sensible flight strategy — but only if this test shows it behaves well on a uniform scene and badly on a structured one, which is the prediction.")

# ------------------------------------------------------------------ 8
doc.add_page_break()
H1("8.  Run sheet  —  one row per capture")
para([("Fill this in as you go, not afterwards. Every column here is something the analysis needs and cannot recover later.", {"i": True})], after=8)
mktable([0.62, 0.5, 0.52, 0.72, 0.7, 0.55, 0.65, 0.45, 0.62, 0.5, 1.17],
        ["Run ID", "Test", "Time", "Probe °C start", "Probe °C end", "FPA °C", "Foil bg °C", "Gain", "FFC time", "Air m/s", "Filename / notes"],
        [[" "] * 11 for _ in range(18)])
spacer(6)
para([("Run ID convention: ", {"b": True}), ("T2-03, T4-01 and so on — test number, then sequence within that test. Use the same string as the capture folder name so the two can never be mismatched.", {})])

# ------------------------------------------------------------------ 9
doc.add_page_break()
H1("9.  Reference: why the tape stays on")
para([("A thermal camera measures radiance, not temperature. A surface with low emissivity is largely a mirror for the room, so what reaches the detector is mostly reflected background rather than the target itself.", {})], after=7)
mktable([2.3, 0.7, 2.0, 2.0], ["Surface", "ε", "Reads (35 °C plate, 22 °C room)", "A real 1.00 °C step moves the reading"], [
    ["Bare / lightly oxidised metal", "0.22", "24.7 °C   (−10.3 °C)", ("0.24 °C", {"b": True, "sh": SH_RED})],
    ["Ceramic hotplate top", "0.90", "33.8 °C   (−1.2 °C)", "0.91 °C"],
    ["Black electrical tape", "0.95", "34.4 °C   (−0.6 °C)", ("0.96 °C", {"b": True, "sh": SH_GREEN})],
])
spacer(6)
para([("There are two distinct problems with bare metal, and the second is the one that ends the experiment:", {})])
para([("Bias. ", {"b": True}), ("The reading sits about 10 °C low. A contact probe can correct for this, so on its own it would be survivable.", {})], indent=0.3)
para([("Sensitivity. ", {"b": True}), ("Only the fraction ε of any real temperature change reaches the detector at all. Bare, a 1 °C step arrives as roughly 0.24 °C — a 4× loss of signal. No probe recovers signal that never arrived. Set against Round 1's measured 0.56 °C rms scatter, a 1 °C step would sit at about the noise floor, and Round 2 could not answer its own question.", {})], indent=0.3)
spacer(4)
para([("A consistency check worth knowing: inverting Round 1's own observation that the bare plate “reads 10 °C lower” gives ε ≈ 0.22, squarely in the range for lightly oxidised metal. An independent radiative model and the bench observation land in the same place — good evidence the tape was doing exactly what we assumed.", {})], after=7)
para([("Figures computed by integrating Planck over the Boson's 7.5–13.5 µm band in analysis/lab_tests/emissivity_tape_check.py, not from a grey-body approximation.", {"i": True, "sz": 9, "c": GREY_T})])

# ------------------------------------------------------------------ 10
H1("10.  Teardown and data handling  —  30 min")
step(1, "Photograph the final rig state before dismantling anything.")
step(2, "Check the run sheet is complete. Fill any gaps now, while people still remember.")
step(3, "Verify every capture folder exists and is non-empty. Spot-check frame counts against the expected ~7200 per 2-minute run.")
why("A short folder means dropped frames, which corrupt run timing silently. Better to find out now than in analysis.")
step(4, "Copy the SMALL products first: run sheet, fpatemp.py CSVs, a few sample frames per run, setup photos.")
step(5, "Start the bulk raw transfer and leave it running.", bold=True)
why("About 71 GB of raw TIFFs takes roughly 6.3 h at 25 Mbps, or 3.1 h at 50 Mbps. It will not finish inside teardown, so it runs afterwards — and because the small products went first, analysis is never blocked waiting on it.")
step(6, "Record where the raw data physically lives.")
fill("Raw data location")
step(7, "Power the camera down last, and note total powered-on time.")

spacer(14)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Checklist v1.0 · 2026-09-24 · prepared by JXP and Claude for Calypso Monterey Bay.  Supporting calculations in the SST-test repository under analysis/lab_tests/.")
r.italic = True; r.font.size = Pt(8.5); r.font.color.rgb = GREY_L

doc.save(sys.argv[1])

# python-docx's stock template emits <w:zoom/> with no w:percent, which the OOXML
# schema requires. Word tolerates it; validators and stricter consumers do not.
import re, shutil, zipfile
_src = sys.argv[1]
_tmp = _src + ".tmp"
with zipfile.ZipFile(_src) as zin, zipfile.ZipFile(_tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/settings.xml":
            txt = data.decode("utf-8")
            txt = re.sub(r'<w:zoom(?![^>]*w:percent)([^>]*?)/>',
                         r'<w:zoom\1 w:percent="100"/>', txt)
            data = txt.encode("utf-8")
        zout.writestr(item, data)
shutil.move(_tmp, _src)

print("wrote", sys.argv[1])
