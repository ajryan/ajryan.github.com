# Schematic Trace — Standalone Harmonic Tremolo (Fender 6G8‑A based)

**Values traced directly from the Fender Twin‑Amp 6G8‑A schematic** (K‑FJ,
`Fender_twin_6g8a.pdf`, both sheets). The 6G8‑A is a full amp; **this project
extracts only the harmonic‑vibrato section** and repackages it as a standalone
effect with an added output buffer, relay bypass, and its own power supply.

Confidence markers:

- **[C]** Confirmed — read off the 6G8‑A schematic.
- **[P]** Probable — reasonable value, not explicitly legible on the sheet.
- **[D]** Design addition — parts the 6G8‑A vibrato does **not** contain
  (input recovery triode, cathodyne, cathode‑follower output, relay bypass,
  standalone PSU, 12 V rail). Not a 6G8‑A value — my design.

> **What the tremolo uses in the stock amp:** the harmonic vibrato spans the
> **first 12AX7** (LFO oscillator, 2 triodes) and a **7025** running at **+330 V**
> (the two bias‑varied modulator triodes with the RC split bridge between them).
> The two 7025s on the right of the schematic (PRESENCE, 100k/470k long‑tail,
> +295 V/+330 V) are the **power‑amp phase inverter/driver — NOT the tremolo** and
> are not reproduced here.

---

## Triode allocation for the standalone unit (3 × 12AX7 = 6 triodes)

| Tube | Triode a | Triode b | Notes |
|------|----------|----------|-------|
| **V1** | Input recovery/driver **[D]** | Cathode‑follower output **[D]** | both audio |
| **V2** | HF modulator **[C values]** | LF modulator **[C values]** | both audio |
| **V3** | LFO oscillator **[C values]** | Cathodyne phase splitter **[D]** | both LFO, isolated |

**Topology note (honest):** the stock 6G8‑A makes its LFO from a **2‑triode
phase‑shift oscillator** and drives the two modulators from that network — it has
**no dedicated cathodyne.** The brief explicitly asked for a phase‑shift LFO **and**
a cathodyne, so this build uses a **1‑triode oscillator + 1‑triode cathodyne**
(V3a/V3b) to generate the two anti‑phase LFO drives. That is a deliberate design
choice, not the stock wiring — see the caveat in `notes.md §6`. All the *component
values* below are the stock 6G8‑A values; the *interconnection* of the LFO is the
brief's cathodyne variant.

---

## Audio path

```
IN ─▶ [relay select] ────────────────────────────────────────────┐ (bypass, dry)
  └▶ V1a recovery ─▶ HPF/LPF split ─▶ V2a (HF) ┐                   │
                                 └──▶ V2b (LF) ┴─▶ MIX ─▶ [relay]─▶ V1b follower ─▶ LEVEL ─▶ OUT
                                       ▲    ▲
                               anti‑phase bias from cathodyne (LFO)
```

### 1. Input recovery / driver — V1a **[D]**
The stock circuit feeds the modulators from the vibrato‑channel preamp (a whole
7025 + tone stack). A standalone effect doesn't have that, so V1a is a single
recovery stage to make up the passive‑split loss. **These are my values, not 6G8‑A.**

| Part | Value | Conf | Note |
|------|-------|------|------|
| R1 grid stopper | 68 k | [P] | (stock vibrato input stoppers are 68 k) |
| R2 grid leak | 1 M | [D] | |
| R3 plate load | 100 k | [D] | to B+3 |
| R4 cathode | 1.5 k | [D] | |
| C1 output coupling | 0.022 µF | [D] | into split |

*Inversion: 1.*

### 2. HPF / LPF split (passive) — **all confirmed on the 6G8‑A**
The defining harmonic‑vibrato node: audio splits into a high‑pass leg to the HF
modulator and a low‑pass leg to the LF modulator.

| Part | Value | Conf | Note |
|------|-------|------|------|
| C2 HPF cap → HF grid | **250 pF (.00025)** | **[C]** | |
| R5 LPF split resistor | **220 k** | **[C]** | |
| C3 LPF cap → LF grid | **0.005 µF (.005)** | **[C]** | now confirmed (earlier this was flagged) |

*Inversion: 0.*

### 3. Modulator triodes — V2a (HF), V2b (LF) — **7025 @ +330 V in stock**
Each amplifies its band; the LFO varies the two grids' bias in **anti‑phase**.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R7 / R8 plate loads | **100 k, 5 % matched** | **[C]** | 5 % for balanced modulation; to B+2 |
| R12 / R13 plate mixing | **470 k each** | **[C]** | sum the two plates into the MIX node |
| R9 shared cathode | **4.7 k** | **[C]** | with C4 bypass |
| C4 cathode bypass | **2 µF** | **[C]** | stock "2 / 25" (2 µF/25 V) |
| R10 / R11 modulator grid R | **1 M each** | **[C]** | LFO reaches the grids via the 10 M INTENSITY pot |
| — grid DC bias | ~+68 V | [C] | stock shows +68.5 V / +70 V bias points |

*Inversion: 1 (summed).* Stock plate supply is **+330 V**; this build runs ~240 V
(B+2) per the 250–300 V brief — see headroom note in `notes.md §2`.

### 4. Cathode‑follower output — V1b **[D — not in the 6G8‑A]**
Both trem and dry bypass route through this one follower so both paths get
identical buffering, level, and polarity.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R20 grid leak | 1 M → gnd | [D] | grid at 0 V DC |
| R21 cathode / output | 22 k | [D] | operating‑point note in `notes.md §2` |
| C8 output coupling | 0.1 µF | [D] | to OUTPUT LEVEL P3 |

*Inversion: 0.*

---

## LFO path (physically isolated from audio)

### 5. LFO oscillator — V3a — **first 12AX7 in stock; values confirmed**
| Part | Value | Conf | Note |
|------|-------|------|------|
| R15 plate load | **470 k** | **[C]** | stock plates at +170 V/+175 V |
| R16 cathode | **4.7 k** | **[C]** | with C5 bypass |
| C5 cathode bypass | **25 µF** | **[C]** | stock "25 / 25" |
| C10 / C11 / C12 phase‑shift caps | **.01 / .02 / .03** | **[C]** | graduated network (stock) |
| R17 / R18 phase‑shift R | **1 M** | **[C]** | |
| R19 feedback R | **4.7 M** | **[C]** | |
| series R after speed | 100 k | [C] | |
| **P1 SPEED** | **3 M reverse‑audio (RA)** | **[C]** | stock "SPEED 3M‑RA" |

### 6. Cathodyne phase splitter — V3b **[D]**
Produces two equal anti‑phase LFO drives to bias the modulators oppositely.
INTENSITY sets depth.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R33 plate load | 100 k | [D] | equal to cathode for balance |
| R34 cathode load | 100 k | [D] | |
| R14 grid leak | 1 M | [D] | |
| C9 osc→cathodyne coupling | 0.02 µF | [C] | stock uses .02 here |
| **P2 INTENSITY** | **10 M reverse‑audio (RA)** | **[C]** | stock "INTENSITY 10M‑RA" — a specialty value, see `notes.md §3` for sourcing |

---

## Relay true‑bypass — K1 (Takamisawa NA12W‑K, DPDT, 12 VDC) **[D]**
Unchanged from the first pass: coil de‑energized = **bypass (dry)**; pop
suppression via 1 M bleeds (R20/R22/R31) holding all coupling nodes at 0 V DC;
D5 coil flyback; latching footswitch over TRS (J3).

## Power supply **[D]**
Hammond 269EX (380 VCT @ 71 mA, datasheet confirmed), **center‑tapped full‑wave
(2× 1N4007)** to land ~258 V — *not* a bridge (see `notes.md §4a`). Three RC filter
nodes, DC‑elevated heaters, 12 V relay rail doubled/regulated off the 6.3 VAC
heater. Full detail and node voltages in `notes.md`.
