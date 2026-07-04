# Engineering Notes

Companion to `schematic-trace.md`. Covers the four things the brief asked the
notes file to answer: **polarity verification (both paths)**, **B+ node voltage
estimates**, **values I could not confirm from the 6G8‑A schematic**, plus the
design justifications (PT/rectifier, relay supply, clean blend).

---

## 1. Polarity verification — bypass vs engaged

Requirement: net signal polarity must be **identical** in bypass and engaged
modes. Both paths deliberately share the **same output cathode follower (V1b)**,
so the only difference is the number of inverting gain stages ahead of it.

### Bypass path
```
IN ─▶ C7 ─▶ (relay NC) ─▶ V1b cathode follower ─▶ C8 ─▶ LEVEL ─▶ OUT
```
| Stage | Type | Inversions |
|-------|------|-----------|
| Coupling caps, relay | passive | 0 |
| V1b cathode follower | follower | 0 |
| **Total** | | **0 (even)** |

### Engaged path
```
IN ─▶ V1a driver ─▶ HPF/LPF split ─▶ V2a/V2b mixers ─▶ MIX ─▶ (relay NO) ─▶ V1b follower ─▶ OUT
```
| Stage | Type | Inversions |
|-------|------|-----------|
| V1a input driver | common‑cathode | 1 |
| HPF/LPF passive split | passive | 0 |
| V2a / V2b mixers (summed) | common‑cathode | 1 |
| V1b cathode follower | follower | 0 |
| **Total** | | **2 (even)** |

### Result
- **Bypass inversions = 0 (even). Engaged inversions = 2 (even).**
- Both even ⇒ **output is in‑phase with input in both modes.** ✅ Net polarity
  identical, so switching bypass↔engaged produces no phase flip.
- This is *why* the follower is shared and *why* the mixer count is even: it makes
  the polarities match without an extra inverter. If you ever add/remove an
  inverting stage in the trem path, keep the engaged count **even** to preserve this.

> The two cathodyne LFO drives are intentionally *anti‑phase to each other* (that
> is the tremolo mechanism); they are not in the audio path, so they do not affect
> audio polarity.

---

## 1a. Level matching bypass vs engaged — why the trim attenuator (VR1)

Polarity and output impedance are matched by routing both paths through the shared
cathode follower V1b. **Level is not** — and cannot be fixed *by* the follower,
because a cathode follower (like a cathodyne) is **~unity gain**: it buffers, it
does not amplify. Whatever level difference exists is set entirely by the stages
**ahead** of the follower:

- **Bypass leg ahead of follower:** a coupling cap only → **unity**.
- **Engaged leg ahead of follower:** V1a driver (~×30) → lossy HPF/LPF split →
  bias‑varied modulators → 470 k mix. Net is **not** unity, and it is
  **time‑varying** (that is the tremolo).

So the fix is not "gain makeup in bypass" (the follower can't add gain) but
**trimming the engaged leg down to the bypass's unity** — the inverse framing.
**VR1** (1 M cermet trimmer) is a divider in the engaged leg only, after C6:

```
MIX ─▶ C6 ─▶ VR1 top (T33)
                 │ wiper (T48) ─▶ relay engaged contact ─▶ V1b grid
                 ▼
                gnd (T35)
```

**Calibration reference:** because engaged amplitude is modulated, "equal level"
needs a defined operating point. Set VR1 with **INTENSITY at minimum** (shallowest
modulation, steadiest level) so switching bypass↔engaged there is seamless; deeper
INTENSITY then simply adds tremolo *around* that matched level. VR1 only
attenuates (engaged runs hotter than unity), which is the needed direction.

If a build ever comes out with the engaged path *quieter* than bypass (unlikely
with the driver present, but possible with a very lossy split), VR1 can't lift it —
that would require an actual gain stage (a common‑cathode triode, which inverts and
would need a second inversion to stay polarity‑even). Not expected here.

---

## 2. B+ node voltage estimates

**Inputs:** 269EX 190‑0‑190 (380 V CT), CT full‑wave, 22 µF reservoir. Peak of
each half‑winding = 190 × √2 ≈ 269 V, less ~1 V diode and winding sag.

**Load currents (estimated, light — this is a preamp‑only load):**

| Node | Fed stages | Est. current |
|------|-----------|-------------|
| B+1 | V1b follower + V3b cathodyne + bleeder + htr divider | ≈ 4 mA local, ≈ 8 mA total incl. downstream |
| B+2 | V2a + V2b mixer plates (100 k) | ≈ 2 mA |
| B+3 | V1a driver + V3a LFO plates | ≈ 1.8 mA |

**Node estimates:**

| Node | Cap | Dropper | Estimated V | Derivation |
|------|-----|---------|------------|-----------|
| **B+1** | C13 22 µF | — (reservoir) | **≈ 258 V** | 269 pk − diode − light‑load sag |
| **B+2** | C14 22 µF | R23 4.7 k | **≈ 240 V** | 258 − (3.8 mA × 4.7 k = 18 V) |
| **B+3** | C15 22 µF | R24 10 k | **≈ 222 V** | 240 − (1.8 mA × 10 k = 18 V) |

**Plate operating points (rough):**
- Mixer plates (B+2, 100 k, ~1 mA): ≈ **140 V** — healthy 12AX7 gain stage.
- Driver plate (B+3, 100 k, ~1 mA): ≈ **122 V**.
- B+1 lands the target window (250–300 V requested → ~258 V). ✅

**Ripple:** full‑wave 120 Hz into 22 µF at 8 mA ≈ 1.5 V pp at B+1; the RC sections
(4.7 k/22 µF, 10 k/22 µF) knock B+2/B+3 down well below audibility; the input
stage on B+3 (most filtered) is quietest.

> These are **estimates**, not measured. Real numbers depend on the actual 269EX
> DCR, mains voltage, and true tube currents. Expect ±15 V. Set them by
> measurement on the bench; if B+1 runs high, the 71 mA PT will sag less than a
> guitar‑amp PT so budget for the light‑load end.

### Cathode‑follower operating‑point caveat (V1b)
Because the follower grid is AC‑coupled (relay‑selected) and returned to 0 V DC,
the follower self‑biases at low current (cathode a few volts, limited by 12AX7
cutoff). R21 = 22 k puts Ik ≈ 0.1–0.15 mA, Zout ≈ 1.5 k — fine for driving the
1 M LEVEL pot + cable at guitar levels. Negative‑going headroom is the limit
(~2–3 V pk). If you want more clean headroom, **elevate the follower grid
reference** (return R20 to the +80 V heater‑elevation node instead of ground) and
raise R21 to 100 k; that trades a slightly more complex bias for large symmetric
swing. Left at 0 V/22 k as the simpler default. **[design choice — verify on bench]**

---

## 3. Value provenance — traced from the 6G8‑A schematic

The 6G8‑A schematic (`Fender_twin_6g8a.pdf`) was read directly. Earlier guesses
that were **wrong** and are now corrected from the sheet:

| Ref | Earlier guess | **Corrected (from schematic)** |
|-----|--------------|-------------------------------|
| **P2 INTENSITY** | 1 M | **10 M reverse‑audio (RA)** |
| **P1 SPEED** | 5 M | **3 M reverse‑audio (RA)** |
| R15 LFO plate load | 220 k | **470 k** |
| R16 LFO cathode | 2.2 k | **4.7 k // 25 µF** |
| C10/C11/C12 phase‑shift | .01/.01/.01 | **.01 / .02 / .03** (graduated) + **4.7 M** feedback |
| R7/R8 modulator plates | 100 k | **100 k, 5 % matched** |
| R10/R11 modulator grid R | 3.3 M | **1 M** |
| R9 modulator cathode | 1.5 k | **4.7 k // 2 µF** |
| plate mixing | (cap‑coupled) | **470 k** resistive mixing (R12/R13) |
| C3 LPF cap | 0.005 µF *(flagged)* | **0.005 µF — confirmed** |

Confirmed and unchanged: **C2 = 250 pF HPF**, **R5 = 220 k split**.

**Sourcing note — the specialty pots.** SPEED **3 M‑RA** and INTENSITY **10 M‑RA**
are Fender‑era reverse‑audio values that mainstream distributors (Mouser/Digikey)
do not stock — hence `TBD` in the BOM. Get them from guitar‑amp parts vendors
(Mojotone, Amplified Parts, Angela, Hoffman) who carry repro Fender vibrato pots,
**or** substitute: a **10 M** linear/audio for INTENSITY and **2 M–3 M** linear for
SPEED work if you can't find the RA taper — the taper only changes control feel,
not the range. Confirm on the bench.

Still genuinely **[P]** (probable, not legible on the sheet): R6 (HF grid ref).
Everything marked **[D]** in `schematic-trace.md` is my design (input recovery
triode, cathodyne, follower, relay, PSU, 12 V rail) — not a 6G8‑A value, so it is
"verify on bench" engineering rather than a schematic trace.

---

## 4. Design justifications

### 4a. PT + rectifier: 269EX, center‑tapped full‑wave (not a bridge)
The brief guessed a 269EX and a 1N4007 **bridge**. Datasheet check: the 269EX HV
secondary is **380 V center‑tapped @ 71 mA**.
- A 4‑diode bridge across the **full** 380 V winding → ≈ 380 × √2 ≈ **537 V DC**
  unloaded — roughly **double** the 250–300 V target. You'd then burn ~250 V across
  droppers, which a 43 VA / 71 mA PT cannot spare.
- Using the **center tap** with a **2‑diode full‑wave** rectifier → ≈ 190 × √2 ≈
  **~258 V** — lands the target directly, and 71 mA is plenty for a ~8 mA preamp
  load. **Chosen.** Two 1N4007 (D1/D2), anodes to the 190 V ends, cathodes to the
  reservoir; CT is the DC ground return.
- If you specifically want a bridge, that means **a different PT** (a non‑CT ~230 V
  winding, e.g. a Hammond 290‑series tap or a 240 V toroid). With the 269EX,
  CT full‑wave is the correct call. This is the "confirm with datasheet, then
  choose" the brief invited.

### 4b. 12 VDC relay supply: heater‑derived, not a separate winding
Chosen: **rectify/double the 6.3 VAC heater winding → ~16 V → 78L12 → 12 V.**
Justification:
- The 269EX has **no spare low‑voltage winding**, and its 6.3 V @ 2.5 A has ample
  headroom: 3× 12AX7 heaters = 3 × 0.3 A = **0.9 A**, leaving ~1.6 A. The relay
  coil draws only **12 mA** (1028 Ω) + LED ~10 mA — negligible.
- Avoids specifying a second transformer or a custom PT winding (cost, panel
  space, a second fused mains path).
- A voltage **doubler** (not a single rectifier) is used because 6.3 VAC peak is
  only ~8.9 V — below the 78L12's ~13.7 V minimum input. Doubling gives ~16 V,
  comfortably above dropout.
- Trade‑off accepted: the 12 V rail shares a ground/winding with the heaters, so
  keep the doubler/regulator physically near the PT and star‑ground it to the PSU
  node, not the input ground, to avoid injecting heater‑rate ripple into audio.

### 4c. Clean blend: evaluated, omitted
The brief asked whether a dedicated clean blend is worthwhile. **Recommendation:
omit it.**
- Harmonic (bias‑vary) tremolo is **not** a hard on/off VCA — at low INTENSITY the
  two bands are only lightly modulated and the summed output already retains most
  of the dry character. Turning INTENSITY down **is** effectively a "more clean"
  control, which is what a blend would buy you.
- A true parallel dry blend would need another mixing node and likely a 4th triode
  (a 4th tube or an op‑amp), plus a BLEND pot and rework of the board/chassis and
  the shared‑follower polarity trick. Marginal sonic gain for real added cost and
  complexity.
- If a blend is ever wanted, the lowest‑impact route is a dry‑mix resistor from the
  driver output summed at the follower grid through a small BLEND pot — but that
  reintroduces a polarity/level‑matching burden the current design avoids.

### 4d. Relay logic / fail state
Coil **de‑energized = bypass (dry)**. So a dead 12 V rail, blown fuse, or
unplugged footswitch fails to **clean dry signal**, not silence — the safe state
for a stage unit.

---

## 6. Topology caveat — cathodyne vs stock LFO

The stock 6G8‑A generates the two anti‑phase modulator drives from a **2‑triode
phase‑shift oscillator** (the first 12AX7), with **no dedicated cathodyne**. The
brief asked for a phase‑shift LFO **and** a cathodyne, so this build uses a
**1‑triode oscillator (V3a) + 1‑triode cathodyne (V3b)**. Consequence to verify on
the bench: a single‑triode phase‑shift oscillator has less loop gain than the stock
two‑triode design, so with the stock **.01/.02/.03 + 4.7 M + 3 M** network it may
need a nudge to oscillate reliably (raise the phase‑shift Rs, or reduce the
graduated caps toward three equal ~.02 µF). Two clean options:

- **Follow the brief (this build):** 1‑triode osc + cathodyne, tune for reliable
  start‑up.
- **Follow stock exactly:** use both triodes of V3 as the oscillator and take the
  two anti‑phase drives from the network directly — drop the cathodyne. Frees no
  parts but is the proven Fender arrangement.

Either way the modulator, split, and INTENSITY/SPEED values above are the stock
6G8‑A values.

## 7. Known limitations of this deliverable (honest scope)

1. **Standalone adaptation, not a 1:1 clone.** Trem *values* are traced from the
   6G8‑A; the input recovery stage, cathodyne, follower, bypass and PSU are added
   for standalone use (all marked **[D]**). The stock modulators run at **+330 V**;
   this build runs ~240 V per the 250–300 V brief, trading some headroom (§2).
2. **Turret‑board layout is optimized but bench‑verify.** Placement is banded
   (audio top rows, LFO middle, PSU bottom) with local B+/ground rail turrets so
   every component now spans ≤ ~1.1" of adjacent turrets (no long runs). Still,
   open `harmonic-tremolo.diy` in DIYLC 4.x and sanity‑check lug spacing and any
   0.25"‑pitch turret pairs against your actual turret‑lug diameter before drilling.
3. **The `.diy` is best‑effort DIYLC v4 XML** written without DIYLC to test it.
   It is valid XML with correct component classes and inch coordinates, but DIYLC
   may rescale/relabel on import. The **authoritative** layout artifacts are
   `turret-drill.csv` + `turret-drill.svg` + this trace, not the `.diy`.
4. **Node voltages are estimates**, ±15 V — Section 2.
