# Schematic Trace — Standalone Harmonic Tremolo (Fender 6G8‑A based)

This is the stage‑by‑stage circuit the layout, BOM, and `.diy` are built from.
Every value carries a confidence marker:

- **[C]** Confirmed — corroborated by multiple 6G8‑A / harmonic‑vibrato sources.
- **[P]** Probable — standard harmonic‑vibrato practice, matches the topology, but
  **not** cross‑checked against a verified 6G8‑A schematic image. **Verify.**
- **[D]** Design addition — my design for the parts the 6G8‑A does *not* contain
  (cathode‑follower output, relay bypass, standalone PSU, 12 V rail). Not a 6G8‑A value.

> ⚠️ I could not fetch a clean 6G8‑A schematic image in this session (the usual
> archives — el34world, ampwares, tdpri — blocked automated fetch with HTTP 403).
> Values below marked **[P]** come from my knowledge of the circuit plus text
> corroboration, not from reading the sheet. Treat `notes.md` "Unconfirmed values"
> as the punch‑list to reconcile against your copy of the 6G8‑A schematic before
> ordering the last few parts. This is exactly the "flag anything you can't
> confirm" the brief asked for.

---

## Triode allocation (3 × 12AX7 = 6 triodes)

The 6G8‑A five‑triode harmonic vibrato needs exactly 5 triodes; the 6th (the
"spare half tube" the brief mentions) becomes the cathode‑follower output. I
grouped triodes by **function per envelope** to keep the LFO out of the audio
tubes — cleaner than the original, which shares envelopes between LFO and audio:

| Tube | Triode a | Triode b | Rationale |
|------|----------|----------|-----------|
| **V1** | Input driver | Cathode‑follower output | both **audio**, one envelope |
| **V2** | HF mixer/modulator | LF mixer/modulator | both **audio**, one envelope |
| **V3** | LFO oscillator | Cathodyne phase splitter | both **LFO**, isolated envelope |

Physical order in the chassis (input end → PT end): **V1 → V2 → V3**, so the
LFO tube (V3) sits farthest from the input jack.

---

## Signal path (audio)

```
IN ─▶ [relay bypass select] ──────────────────────────────┐ (bypass, dry)
  └▶ V1a driver ─▶ HPF/LPF split ─▶ V2a (HF) ┐             │
                              └────▶ V2b (LF) ┴─▶ MIX ─▶ [relay select]─▶ V1b follower ─▶ LEVEL ─▶ OUT
                                    ▲    ▲
                            bias‑vary from cathodyne (LFO)
```

### 1. Input driver — V1a
Recovers level and drives the passive split (which is lossy).

| Part | Value | Conf | Note |
|------|-------|------|------|
| R1 grid stopper | 68 k | [P] | |
| R2 grid leak | 1 M | [P] | |
| R3 plate load | 100 k | [P] | to B+3 |
| R4 cathode | 1.5 k (unbypassed) | [P] | unbypassed = a little local NFB, tames the split drive |
| C1 output coupling | 0.022 µF | [P] | into split node |

*Inversion: 1 (common‑cathode).* 

### 2. HPF / LPF split (passive) — **the defining harmonic‑vibrato node**
The driver output splits into a **high‑pass** leg to the HF modulator and a
**low‑pass** leg to the LF modulator. When the two are re‑summed after opposite
bias modulation, the crossover between them sweeps — the "harmonic" (phase‑y)
character.

| Part | Value | Conf | Note |
|------|-------|------|------|
| C2 HPF series cap → HF grid | **250 pF** | **[C]** | corroborated across sources |
| R5 LPF series R (split) | **220 k** | **[C]** | corroborated |
| C3 LPF cap → LF grid | 0.005 µF | [P] | one source says .005 µF; **some variants show 0.02 µF — verify** |
| R6 HF grid reference | 220 k | [P] | |

*Inversion: 0 (passive).* 

### 3. Mixer / modulator triodes — V2a (HF), V2b (LF)
Each amplifies its band; the LFO varies each grid's bias (bias‑vary tremolo) in
**anti‑phase**, so as one band ducks the other swells.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R7 / R8 plate loads | 100 k each | [P] | to B+2; outputs re‑summed at MIX via C4/C5 |
| R9 shared cathode | 1.5 k | [P] | |
| R10 / R11 grid LFO‑inject / leak | 3.3 M each | [P] | **high‑Z bias nodes — value strongly affects depth/thump; verify** |
| C4 / C5 output coupling | 0.022 µF each | [P] | sum at MIX node |

*Inversion: 1 (each mixer is common‑cathode; summed → net 1).* 

### 4. Cathode‑follower output — V1b **[D — my addition, not 6G8‑A]**
Both the trem path and the dry bypass path are routed **through this one
follower**, per the brief, so both paths get identical output buffering, level,
and polarity.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R20 grid leak | 1 M → gnd | [D] | grid at 0 V DC |
| R21 cathode / output tap | 22 k | [D] | see operating‑point note in `notes.md` |
| C8 output coupling | 0.1 µF | [D] | to OUTPUT LEVEL pot P3 (1 M) |

*Inversion: 0 (follower).* 

---

## LFO path (kept physically away from audio)

### 5. LFO oscillator — V3a (3‑stage RC phase‑shift)
A phase‑shift oscillator: 3 RC sections give the 180° needed for oscillation at
the low tremolo rate; SPEED (P1) varies the network R to set rate.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R15 plate load | 220 k | [P] | to B+3 |
| R16 cathode | 2.2 k | [P] | |
| C10 / C11 / C12 phase‑shift caps | 0.01 µF ×3 | [P] | **set tremolo rate range — verify against sheet** |
| R17 / R18 / R19 phase‑shift R | 1 M ×3 | [P] | with SPEED pot |
| **P1 SPEED** | **5 M audio** | [P] | brown‑era used a very large speed pot (3 M–5 M class); **verify value/taper** |

### 6. Cathodyne phase splitter — V3b
Takes the oscillator output and produces two equal, **anti‑phase** LFO drives
(plate vs cathode) to bias the two mixers oppositely. INTENSITY (P2) sets how
much LFO reaches the mixer grids = tremolo depth.

| Part | Value | Conf | Note |
|------|-------|------|------|
| R12 plate load | 100 k | [P] | anti‑phase A → HF mixer grid |
| R13 cathode load | 100 k | [P] | anti‑phase B → LF mixer grid (equal loads = balanced) |
| R14 grid leak | 1 M | [P] | |
| C9 osc→cathodyne coupling | 0.02 µF | [P] | |
| **P2 INTENSITY** | **1 M audio** | [P] | in the cathodyne→mixer bias path; **verify value** |

---

## Relay true‑bypass — K1 (Takamisawa NA12W‑K, DPDT, 12 VDC) **[D]**

- **Pole 1** selects the follower‑grid source: **NC = bypass** (dry `IN` via C7),
  **NO = engaged** (`MIX` via C6). Coil de‑energized = bypass (fail‑safe to dry).
- **Pole 2** spare — used for the LED/status indication.
- **Pop suppression:** permanent 1 M bleeds (R20 on the grid, R22 on the bypass
  node, R31 on the engaged node) hold every coupling‑cap board node at 0 V DC, so
  the relay never connects a DC‑charged node to the grid → no switch pop. Coupling
  caps (C6/C7) block any residual DC. D5 = coil flyback diode.
- **Footswitch:** latching SPST (push‑on/off) over a TRS jack (J3): tip = 12 V to
  coil, ring = LED return in the footswitch, sleeve = ground.

---

## Power supply **[D]**

- **PT:** Hammond **269EX** — 380 V **CT** @ 71 mA, 6.3 V @ 2.5 A, 43 VA (datasheet
  confirmed). See `notes.md` for why this is rectified **center‑tapped full‑wave
  (2× 1N4007)** rather than a 4‑diode bridge.
- **Rectifier:** D1/D2 (1N4007) full‑wave CT → reservoir C13 (22 µF/450 V).
- **Three filter nodes:** B+1 (C13) → R23 4.7 k → B+2 (C14) → R24 10 k → B+3 (C15).
  Estimated voltages in `notes.md`.
- **Heaters:** 6.3 VAC twisted pair, artificial center tap (R29/R30 = 100 Ω),
  DC‑elevated to ~+80 V off a B+1 divider (R25 220 k / R26 100 k, C16 bypass).
- **12 VDC relay rail:** 6.3 VAC → voltage doubler (D3/D4, C17/C18 100 µF) →
  ~16 VDC → 78L12 (U1) → 12 V. R28 = 220 k safety bleeder across B+1.

See `notes.md` for polarity verification, node‑voltage estimates, and the full
unconfirmed‑value punch‑list.
