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

## 3. Values I could NOT confirm from the 6G8‑A schematic

Punch‑list to reconcile against your copy of the sheet **before final ordering**.
Confirmed values (do not need checking): **C2 = 250 pF HPF**, **R5 = 220 k split**,
five‑triode topology, and the LFO being a 3‑stage phase‑shift oscillator.

| Ref | Assumed | Why unsure / what to check |
|-----|---------|---------------------------|
| C3 | 0.005 µF LPF cap | one text source; **some 6G8‑A variants show 0.02 µF**. Sets the LF band corner. |
| R10, R11 | 3.3 M mixer grid inject/leak | value drives depth & "thump"; brown vs BF differed. Could be 2.2 M–10 M. |
| R7, R8 | 100 k mixer plate loads | typical, not read off sheet |
| R9 | 1.5 k shared mixer cathode | typical |
| R3, R4 | 100 k / 1.5 k driver | typical driver values |
| R12, R13 | 100 k / 100 k cathodyne | standard balanced cathodyne; verify they're equal on your sheet |
| R15, R16 | 220 k / 2.2 k LFO | typical |
| C10–C12 | 0.01 µF ×3 phase‑shift | **sets tremolo rate range** — the value most worth confirming for feel |
| R17–R19 | 1 M ×3 phase‑shift | pairs with SPEED pot |
| **P1 SPEED** | 5 M audio | brown vs BF used 3 M vs 4 M‑class; confirm value **and** taper |
| **P2 INTENSITY** | 1 M audio | confirm value and where it taps (cathodyne output vs grid returns) |
| C9 | 0.02 µF osc→cathodyne | typical |

Everything marked **[D]** in `schematic-trace.md` (follower, relay, PSU, 12 V
rail) is my design, not a 6G8‑A value, so it is not on this list — but it is still
"verify on bench" engineering, not gospel.

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

## 5. Known limitations of this deliverable (honest scope)

1. **Unverified 6G8‑A values** — Section 3. The schematic image could not be
   fetched here; reconcile before ordering P1/P2/C3/C10‑12/R10‑11.
2. **Turret‑board layout is first‑pass.** The drill table and net map are complete
   and on the Hoffman 0.25" grid, but components are assigned to turrets by net,
   not yet optimized so every part spans adjacent turrets. `layout.svg` shows the
   long runs this creates. Open `harmonic-tremolo.diy` in DIYLC 4.x and nudge
   turrets/parts to minimize lead length before building.
3. **The `.diy` is best‑effort DIYLC v4 XML** written without DIYLC to test it.
   It is valid XML with correct component classes and inch coordinates, but DIYLC
   may rescale/relabel on import. The **authoritative** layout artifacts are
   `turret-drill.csv` + `turret-drill.svg` + this trace, not the `.diy`.
4. **Node voltages are estimates**, ±15 V — Section 2.
