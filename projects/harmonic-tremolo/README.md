# Harmonic Tremolo Unit — build package

Standalone tube **harmonic tremolo**, based on the **Fender 6G8‑A (five‑triode)
harmonic vibrato**, with an added cathode‑follower output, relay true‑bypass, and
a self‑contained solid‑state power supply. Targeted at a Hoffman Amplifiers
chassis + turret board.

- **Tubes:** 3× 12AX7 (9‑pin noval, chassis mount)
- **Controls:** SPEED, INTENSITY, OUTPUT LEVEL
- **I/O:** input jack, output jack, footswitch TRS, IEC inlet, fuse, power switch, LED
- **Bypass:** DPDT signal relay (Takamisawa NA12W‑K), 12 VDC, latching footswitch
- **Power:** Hammond 269EX, ~258 V B+, SS rectifier, 3 filter nodes, elevated heaters

## ⚠️ Read first
Some 6G8‑A component values **could not be confirmed from a schematic image** in
the session that generated this (archive sites blocked automated fetch). Those are
flagged **[P]** in `schematic-trace.md` and listed as a punch‑list in
`notes.md §3`. **Reconcile them against your copy of the 6G8‑A schematic before
final ordering** (especially SPEED/INTENSITY pots, phase‑shift caps, mixer
grid resistors, and the LPF cap). Confirmed values: 250 pF HPF cap, 220 k split.

## Files

| File | What it is |
|------|-----------|
| `schematic-trace.md` | Stage‑by‑stage circuit + every value with a confidence flag |
| `notes.md` | Polarity verification, B+ node estimates, unconfirmed‑value punch‑list, PT/relay/blend justifications |
| `bom.csv` | Bill of materials — RefDes, value, rating, Mouser P/N, connection, notes |
| `bom_mouser.csv` | Mouser BOM‑import format (Mouser P/N, qty, customer ref) — upload directly |
| `turret-drill.csv` | Turret hole coordinate table (Hoffman custom‑board format, inch grid) |
| `turret-drill.svg` | Dimensioned drill drawing — **print at 1:1 (96 dpi)** as a drill template |
| `layout.svg` | Populated board layout (component/connectivity view) |
| `harmonic-tremolo.diy` | DIYLC v4 project (open in DIYLC 4.x; see caveat in `notes.md §5`) |
| `generate.py` | Single source of truth — regenerates every file above |

Regenerate everything after editing the design:
```bash
python3 generate.py
```

> **On the Mouser part numbers:** they are **representative, best‑effort**
> selections (correct series/rating for the value) chosen without a live Mouser
> lookup in this session. Verify each in your Mouser cart before ordering —
> confirm stock, exact value tolerance/voltage, and lead spacing. `TBD` = pick to
> taste (mostly the pots, whose values are still being confirmed anyway).

## Hardware choices (from Hoffman / vendor data)

- **Chassis:** Hoffman **Stout Chassis V2** — 12″ W × 6.5″ D × 2.5″ H, 0.090″
  aluminum; it already carries **3× nine‑pin socket holes**, matching the 3× 12AX7
  exactly. Sockets in a row; PT (T101) mounted at the far end from the input jack;
  LFO tube (V3) nearest the PT, away from the input. (The V2 chassis also has 3
  octal holes; for a purpose‑built unit you can instead order a plain drilled
  aluminum chassis of the same footprint from Hoffman to avoid the unused holes.)
- **Turret board:** Hoffman stock — **3.125″ tall**, this design **8.0″ wide**
  (Hoffman go up to ~9″), **0.250″ hole grid**, **3/32″ turret lug holes** — all
  matching Hoffman stock. 47 turrets + 4 mounting holes; see `turret-drill.csv`.
- **PT:** Hammond **269EX** (380 VCT @ 71 mA, 6.3 V @ 2.5 A) — center‑tapped
  full‑wave rectified (see `notes.md §4a` for why not a bridge).
- **Relay:** Takamisawa/Fujitsu **NA12W‑K** — DPDT, 12 VDC, 1028 Ω coil (12 mA).

## Layout rules honored
- Tube sockets in a row; PT at the opposite end from the input jack.
- LFO tube envelope (V3) isolated from audio tubes (V1, V2) and sited by the PT.
- LFO wiring kept off the audio path; heaters twisted, artificial‑CT, DC‑elevated
  ~+80 V, run in a chassis corner.
- Relay fails to **dry bypass** (coil de‑energized = clean).

## Signal chain & polarity (summary)
Bypass = **0 inversions**; engaged = **2 inversions** (driver + mixers, follower
adds none). Both even ⇒ **identical polarity, no phase flip on switching.** Full
derivation in `notes.md §1`.

## Sources
- Fender 6G8/6G8‑A harmonic vibrato topology & the confirmed 250 pF / 220 k split:
  TDPRI "Exploring Fender's Harmonic Tremolo", Ampwares Blonde Twin, Amp Garage.
- Hoffman turret board / chassis specs: hoffmanamps.com.
- Hammond 269EX datasheet: hammfg.com.
- Takamisawa NA12W‑K datasheet.
