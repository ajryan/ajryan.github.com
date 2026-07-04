#!/usr/bin/env python3
"""
Harmonic Tremolo Unit - file generator (single source of truth).

Emits, from one component/turret dataset so everything stays consistent:
  - bom.csv              human-readable bill of materials
  - bom_mouser.csv       Mouser BOM-import format (Mouser P/N, qty, customer ref)
  - turret-drill.csv     turret hole coordinate table (Hoffman custom-board format)
  - turret-drill.svg     dimensioned drill drawing (printable at 1:1)
  - layout.svg           populated turret-board layout (component placement)
  - harmonic-tremolo.diy DIYLC 6 project (verified to load in DIYLC 6.1.0)

Circuit: standalone tube harmonic tremolo, Fender 6G8-A (five-triode) harmonic
vibrato + added cathode-follower output + relay true-bypass + SS PSU.
See notes.md / schematic-trace.md for value provenance and flags.

Units: inches. Board grid = 0.250" (Hoffman stock). Turret hole = 3/32" (0.094").
"""

import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ----------------------------------------------------------------------------
# Board geometry (Hoffman turret-board stock)
# ----------------------------------------------------------------------------
BOARD_W = 6.250          # in  (compact; cf. Hoffman 6G15 unit 9.13", PR 11.5")
BOARD_H = 3.125          # in  (all Hoffman turret boards are 3.125" tall)
GRID = 0.250             # in  (Hoffman stock hole grid)
TURRET_HOLE_D = 0.094    # in  (3/32" - Hoffman turret lug hole)
MOUNT_HOLE_D = 0.150     # in  (#8 board mounting standoff clearance)
MARGIN = 0.375           # in  keep-out from board edge to first turret

# Board mounting holes (corners, inset)
# Placed near corners but offset clear of the 0.25" turret rows/columns.
MOUNT_HOLES = [
    ("MH1", 0.250, 0.250),
    ("MH2", BOARD_W - 0.250, 0.250),
    ("MH3", 0.250, BOARD_H - 0.250),
    ("MH4", BOARD_W - 0.250, BOARD_H - 0.250),
]

# ----------------------------------------------------------------------------
# Turret definitions:  id -> (x_in, y_in, net_label)
# Dense Hoffman-idiom matrix modeled on real Hoffman turret boards (6G15 Reverb
# Unit and Princeton Reverb): a compact 6.25 x 3.125" board, ~0.375" turret pitch,
# ground returns collected on a bottom ground BUSS and B+ distributed along a B+
# BUSS row, with sockets mounted above and pots/jacks below (chassis). Long
# vertical resistor runs from a stage down to the busses are normal on these
# boards (see the Princeton Reverb layout). Signal flows left->right by stage.
# ----------------------------------------------------------------------------
T = {}  # id -> (x, y, net)
def turret(tid, x, y, net):
    assert tid not in T, f"dup turret {tid}"
    for k, (px, py, _) in T.items():
        assert not (abs(px - x) < 1e-6 and abs(py - y) < 1e-6), f"{tid} overlaps {k} at {x},{y}"
    T[tid] = (round(x, 3), round(y, 3), net)

# Dense Hoffman-idiom matrix (cf. 6G15 unit + Princeton Reverb boards):
#   6 rows -> r1/r2 top = audio signal, r3/r4 = LFO, bp = B+ bus, gnd = ground buss
#   Signal flows L->R by stage; sockets mount above, pots/jacks below (chassis).
#   Ground returns collect on the bottom buss; B+ droppers + local B+ on the bp
#   row; long vertical resistor runs to the busses are normal on these boards.
r1, r2, r3, r4, bp, gnd = 2.850, 2.400, 1.920, 1.440, 0.940, 0.440

# --- Audio signal, rows r1 (plates/through) / r2 (grids/cathodes/coupling) ---
turret("T1",  0.400, r1, "IN")             # input jack tip
turret("T2",  0.775, r1, "V1a_G")          # V1a grid (after stopper)
turret("T3",  0.775, r2, "V1a_K")          # V1a cathode
turret("T4",  1.150, r1, "V1a_P")          # V1a plate
turret("T6",  1.525, r1, "DRV_OUT")        # driver coupling-out (jumper from T4)
turret("T17", 1.525, r2, "BIAS_HF")        # anti-phase LFO bias -> HF grid
turret("T7",  1.900, r1, "SPLIT")          # split node
turret("T8",  1.900, r2, "HF_G")           # HF modulator grid (high-pass)
turret("T12", 2.275, r1, "HF_P")           # HF modulator plate
turret("T9",  2.275, r2, "LF_G")           # LF modulator grid (low-pass)
turret("T13", 2.650, r1, "LF_P")           # LF modulator plate
turret("T18", 2.650, r2, "BIAS_LF")        # anti-phase LFO bias -> LF grid
turret("T15", 3.025, r1, "MIX")            # modulator plates summed
turret("T14", 3.025, r2, "MIX_K")          # shared modulator cathode
turret("T50", 3.400, r1, "IN")             # local IN (dry bypass tap; bus to T1)
turret("T33", 3.400, r2, "RLY_ENG")        # engaged signal -> VR1 top
turret("T48", 3.775, r1, "ENG_TRIM_W")     # VR1 wiper -> relay engaged contact
turret("T34", 3.775, r2, "RLY_BYP")        # dry bypass signal
turret("T29", 4.150, r1, "FOL_G")          # follower grid (relay common returns here)
turret("T30", 4.525, r1, "FOL_K")          # follower cathode = output
turret("T31", 4.900, r1, "FOL_OUT")        # output coupling -> LEVEL pot

# --- LFO, rows r3 (plates/grids) / r4 (cathodes/network) ---
turret("T19", 2.275, r3, "CATH_P")         # cathodyne plate (anti-phase A)
turret("T21", 2.275, r4, "CATH_K")         # cathodyne cathode (anti-phase B)
turret("T20", 2.650, r3, "CATH_G")         # cathodyne grid (from LFO)
turret("T22", 3.025, r3, "LFO_P")          # LFO plate
turret("T24", 3.025, r4, "LFO_K")          # LFO cathode
turret("T23", 3.400, r3, "LFO_G")          # LFO grid
turret("T25", 3.775, r3, "PS1")            # phase-shift node 1
turret("T26", 3.775, r4, "PS2")            # phase-shift node 2
turret("T27", 4.150, r3, "PS3")            # phase-shift node 3 (-> SPEED pot)

# --- B+ bus row (local B+ near each stage + doubler/12V chain) ---
turret("T49", 1.150, bp, "BPLUS3")         # local B+3 (driver) -> bus
turret("T52", 2.275, bp, "BPLUS1")         # local B+1 (cathodyne/follower) -> bus
turret("T10", 2.650, bp, "BPLUS2")         # local B+2 (modulators) -> bus
turret("T11", 3.400, bp, "BPLUS3")         # local B+3 (LFO) -> bus
turret("T43", 3.775, bp, "AC63")           # 6.3VAC tap in (12V doubler)
turret("T44", 4.150, bp, "DBL")            # doubler mid node
turret("T45", 4.525, bp, "V16")            # ~16VDC unregulated
turret("T46", 4.900, bp, "V12")            # 12VDC regulated
turret("T47", 5.275, bp, "LED_A")          # LED anode tie

# --- PSU main filter + rectifier + heater elevation (right / PT end) ---
turret("T39", 4.900, r2, "RECT_AC1")       # rectifier AC in 1 (190V)
turret("T40", 5.275, r2, "RECT_AC2")       # rectifier AC in 2 (190V)
turret("T36", 4.525, r3, "BPLUS1")         # B+1 reservoir (main)
turret("T37", 4.900, r3, "BPLUS2")         # B+2 (main)
turret("T38", 5.275, r3, "BPLUS3")         # B+3 (main)
turret("T41", 5.650, r3, "HTR_CT")         # heater DC-elevation reference

# --- Ground buss (bottom edge; all returns collect here, tied by buss wire) ---
turret("T5",  0.400, gnd, "GND_1")         # driver ground
turret("T16", 1.900, gnd, "GND_2")         # modulator ground
turret("T28", 2.650, gnd, "GND_3")         # LFO ground
turret("T55", 3.400, gnd, "GND_7")         # 12V reg ground
turret("T35", 3.775, gnd, "GND_5")         # relay/bleed ground
turret("T32", 4.150, gnd, "GND_4")         # follower grid ground
turret("T51", 4.525, gnd, "GND_6")         # follower cathode ground
turret("T42", 5.275, gnd, "GND_PSU")       # PSU ground / CT return
turret("T54", 5.650, gnd, "GND_8")         # heater elevation ground
turret("T56", 3.025, gnd, "GND_9")         # buss drop under modulator + LFO cathodes

# ----------------------------------------------------------------------------
# Component list. Each: ref, kind, value, rating, mouser, from_turret, to_turret, note
# mouser="" means not confirmed / builder-select. kind drives BOM category + DIYLC glyph.
# ----------------------------------------------------------------------------
# Confidence markers in notes: [C] confirmed from 6G8-A schematic, [P] probable,
# [D] design addition (not a 6G8-A value). See schematic-trace.md / notes.md.
C = []
def comp(ref, kind, value, rating, mouser, a, b, note=""):
    C.append(dict(ref=ref, kind=kind, value=value, rating=rating,
                  mouser=mouser, a=a, b=b, note=note))

# ---- Resistors ----
comp("R1", "R", "68k",  "1/2W CF", "594-5083NW68K000J", "T1",  "T2",  "V1a grid stopper")
comp("R2", "R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T2",  "T5",  "V1a grid leak")
comp("R3", "R", "100k", "1/2W CF", "594-5083NW100K00J", "T4",  "T49", "V1a driver plate load [D]; to local B+3")
comp("R4", "R", "1.5k", "1/2W CF", "594-5083NW1K5000J", "T3",  "T5",  "V1a cathode (*)")
comp("R5", "R", "220k", "1/2W CF", "594-5083NW220K00J", "T7",  "T9",  "LPF series (split) [C] confirmed on 6G8-A")
comp("R6", "R", "220k", "1/2W CF", "594-5083NW220K00J", "T8",  "T16", "HF grid reference [P]")
comp("R7", "R", "100k", "1/2W 5%", "594-5063JD100K0J",  "T12", "T10", "HF modulator plate load - 100k 5% matched [C]; to local B+2")
comp("R8", "R", "100k", "1/2W 5%", "594-5063JD100K0J",  "T13", "T10", "LF modulator plate load - 100k 5% matched [C]; to local B+2")
comp("R9", "R", "4.7k", "1/2W CF", "594-5083NW4K7000J", "T14", "T56", "modulator shared cathode 4700 [C]")
comp("R10","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T17", "T8",  "HF modulator grid resistor 1M [C]; LFO arrives via 10M INTENSITY")
comp("R11","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T18", "T9",  "LF modulator grid resistor 1M [C]; LFO arrives via 10M INTENSITY")
comp("R12","R", "470k", "1/2W CF", "594-5083NW470K00J", "T12", "T15", "HF plate mixing resistor 470k [C]")
comp("R13","R", "470k", "1/2W CF", "594-5083NW470K00J", "T13", "T15", "LF plate mixing resistor 470k [C]")
comp("R14","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T20", "T28", "cathodyne grid leak [D]")
comp("R15","R", "470k", "1/2W CF", "594-5083NW470K00J", "T22", "T11", "LFO plate load 470k [C]; to local B+3")
comp("R16","R", "4.7k", "1/2W CF", "594-5083NW4K7000J", "T24", "T56", "LFO cathode 4700 [C]")
comp("R17","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T23", "T25", "phase-shift R1 - 1M [C]")
comp("R18","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T25", "T26", "phase-shift R2 - 1M [C]")
comp("R19","R", "4.7M", "1/2W CF", "594-5083NW4M7000J", "T26", "T27", "phase-shift feedback R - 4.7M [C]")
comp("R20","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T29", "T32", "follower grid leak (grid at 0V DC)")
comp("R21","R", "22k",  "1/2W CF", "594-5083NW22K000J", "T30", "T51", "follower cathode load / output tap")
comp("R22","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T34", "T35", "bypass-node bleed (pop supp)")
comp("R31","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T33", "T35", "engaged-node bleed (pop supp)")
comp("R33","R", "100k", "1/2W CF", "594-5083NW100K00J", "T19", "T52", "cathodyne plate load [D] (equal to cathode); to local B+1")
comp("R34","R", "100k", "1/2W CF", "594-5083NW100K00J", "T21", "T28", "cathodyne cathode load [D] (equal to plate for balance)")
comp("R23","R", "4.7k", "1W  MO",  "71-CMF60-4.7K-E3",  "T36", "T37", "B+1->B+2 dropper")
comp("R24","R", "10k",  "1W  MO",  "71-CMF60-10K-E3",   "T37", "T38", "B+2->B+3 dropper")
comp("R25","R", "220k", "1/2W CF", "594-5083NW220K00J", "T36", "T41", "heater elevation divider top")
comp("R26","R", "100k", "1/2W CF", "594-5083NW100K00J", "T41", "T54", "heater elevation divider bot")
comp("R27","R", "1k",   "1/2W CF", "594-5083NW1K0000J", "T46", "T47", "LED series (12V -> LED anode T47 -> panel LED)")
comp("R28","R", "220k", "1W  MO",  "71-CMF60-220K-E3",  "T36", "T42", "safety bleeder across B+1 (drains B+ at power-off)")
comp("R29","R", "100",  "1/2W CF", "594-5083NW100R00J", "HTR_A", "HTR_CT", "heater artificial-CT / elevation tie")
comp("R30","R", "100",  "1/2W CF", "594-5083NW100R00J", "HTR_B", "HTR_CT", "heater artificial-CT / elevation tie")

# ---- Capacitors ----
comp("C1",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T6",  "T7",  "V1a output coupling")
comp("C2",  "Cf", "250pF",   "500V mica", "80-DM15FD251JO3",   "T7",  "T8",  "HPF to HF mixer - CONFIRMED")
comp("C3",  "Cf", "0.005uF", "630V film", "80-R82DC3470DQ50J", "T7",  "T9",  "LPF to LF modulator - .005 [C] confirmed on 6G8-A")
comp("C4",  "Ce", "2uF",     "25V elec",  "667-EEU-FR1E2R2",   "T14", "T56", "modulator shared cathode bypass (4700//2uF) [C]")
comp("C5",  "Ce", "25uF",    "25V elec",  "667-EEU-FR1E250",   "T24", "T56", "LFO cathode bypass (4700//25uF) [C]")
comp("C6",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T15", "T33", "modulator MIX -> engaged trim top (DC block)")
comp("C7",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T50", "T34", "dry -> relay bypass coupling (dry tap near relay)")
comp("C8",  "Cf", "0.1uF",   "630V film", "80-R82IC3100DQ50J", "T30", "T31", "follower cathode -> output coupling")
comp("C9",  "Cf", "0.02uF",  "630V film", "80-R82DC3200DQ50J", "T22", "T20", "LFO->cathodyne coupling (*)")
comp("C10", "Cf", "0.01uF",  "630V film", "80-R82DC3100DQ50J", "T23", "T25", "phase-shift C1 - .01 [C] (graduated network)")
comp("C11", "Cf", "0.02uF",  "630V film", "80-R82DC3200DQ50J", "T25", "T26", "phase-shift C2 - .02 [C] (graduated network)")
comp("C12", "Cf", "0.033uF", "630V film", "80-R82EC3330DK50J", "T26", "T27", "phase-shift C3 - .03 [C] (nearest E-series to stock .03)")
comp("C13", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T36", "T42", "B+1 reservoir")
comp("C14", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T37", "T42", "B+2 filter")
comp("C15", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T38", "T42", "B+3 filter")
comp("C16", "Ce", "0.1uF",   "630V film", "80-R82IC3100DQ50J", "T41", "T54", "heater elevation bypass")
comp("C17", "Ce", "100uF",   "35V elec",  "667-EEU-FR1V101",   "T43", "T44", "doubler C1")
comp("C18", "Ce", "100uF",   "35V elec",  "667-EEU-FR1V101",   "T44", "T45", "doubler C2")
comp("C19", "Ce", "100uF",   "25V elec",  "667-EEU-FR1E101",   "T46", "T55", "12V reg output cap")

# ---- Diodes / rectifier / regulator ----
comp("D1", "D", "1N4007", "1000V 1A", "512-1N4007", "T39", "T36", "HV rectifier + (CT full-wave)")
comp("D2", "D", "1N4007", "1000V 1A", "512-1N4007", "T40", "T36", "HV rectifier - (CT full-wave)")
comp("D3", "D", "1N4007", "1000V 1A", "512-1N4007", "T43", "T44", "doubler diode 1")
comp("D4", "D", "1N4007", "1000V 1A", "512-1N4007", "T44", "T45", "doubler diode 2")
comp("U1", "IC","78L12",  "TO-92 12V", "511-L78L12ACZ",  "T45", "T46", "12V linear regulator")
comp("D5", "D", "1N4007", "1000V 1A", "512-1N4007", "RLY_COIL+", "RLY_COIL-", "relay coil flyback diode (at relay)")

# ---- Trimmer: engaged-leg unity-match attenuator (bench set-and-forget) ----
# 3-terminal cermet trimmer as a divider on the DC-blocked engaged signal.
# Top=T33 (from C6), wiper=T48 -> relay engaged contact, bottom=T35 (gnd).
# Set on the bench with INTENSITY at minimum so engaged level = unity bypass level.
comp("VR1","trim","1M lin","board trimmer","652-3386P-1-105LF","T33","T35","ENGAGED trim atten; wiper=T48 -> relay engaged in. Set at INTENSITY-min to match bypass [D]")

# ----------------------------------------------------------------------------
# Off-board chassis parts (tube sockets, pots, jacks, transformer, relay, sw)
# Position (x,y) is chassis-layout coordinate in inches; not on the turret board.
# ----------------------------------------------------------------------------
CHASSIS = [
    dict(ref="V1", kind="socket", value="12AX7", mouser="534-8206",
         desc="9-pin noval: V1a input driver, V1b cathode follower", x=2.5, y=2.0),
    dict(ref="V2", kind="socket", value="12AX7", mouser="534-8206",
         desc="9-pin noval: V2a HF mixer, V2b LF mixer", x=5.0, y=2.0),
    dict(ref="V3", kind="socket", value="12AX7", mouser="534-8206",
         desc="9-pin noval: V3a LFO oscillator, V3b cathodyne splitter", x=7.5, y=2.0),
    dict(ref="P1", kind="pot", value="3M reverse-audio (RA)", mouser="",
         desc="SPEED - 6G8-A stock 3M-RA [C] (RA taper; substitute 2M/2.5M linear if 3M-RA unavailable)", x=3.0, y=0.9),
    dict(ref="P2", kind="pot", value="10M reverse-audio (RA)", mouser="",
         desc="INTENSITY - 6G8-A stock 10M-RA [C] (RA taper; 10M is a specialty value - see notes)", x=5.0, y=0.9),
    dict(ref="P3", kind="pot", value="1M audio", mouser="588-P1M-A",
         desc="OUTPUT LEVEL", x=7.0, y=0.9),
    dict(ref="J1", kind="jack", value="1/4 mono", mouser="568-NMJ4HCD2",
         desc="INPUT jack", x=0.6, y=0.9),
    dict(ref="J2", kind="jack", value="1/4 mono", mouser="568-NMJ4HCD2",
         desc="OUTPUT jack", x=9.4, y=0.9),
    dict(ref="J3", kind="jack", value="1/4 TRS", mouser="568-NMJ6HCD2",
         desc="FOOTSWITCH TRS (relay drive + LED return)", x=8.5, y=0.9),
    dict(ref="T101", kind="transformer", value="Hammond 269EX", mouser="546-269EX",
         desc="PT: 380VCT@71mA, 6.3V@2.5A (CT full-wave rectified)", x=10.8, y=3.0),
    dict(ref="K1", kind="relay", value="NA12W-K", mouser="769-NA12W-K",
         desc="DPDT signal relay, 12VDC true-bypass", x=6.5, y=3.5),
    dict(ref="SW1", kind="switch", value="DPST", mouser="612-MRA106-A",
         desc="Mains power switch", x=10.8, y=0.9),
    dict(ref="F1", kind="fuse", value="0.5A slow", mouser="576-0217.500HXP",
         desc="Mains fuse (5x20mm slo-blo) + holder", x=11.2, y=1.6),
    dict(ref="IEC1", kind="inlet", value="IEC C14", mouser="161-R30144-E",
         desc="IEC mains inlet w/ integral fuse holder", x=11.4, y=3.0),
    dict(ref="LED1", kind="led", value="3mm", mouser="604-WP710A10ID",
         desc="Effect-engaged indicator LED", x=8.0, y=0.5),
]

# ----------------------------------------------------------------------------
# Jumper / bus wires: same-net turrets NOT already joined by a component.
# type "power" -> red in layout.svg (B+ busses + ground buss);
# type "signal" -> yellow (dry-bypass tap, driver plate tie).
# ----------------------------------------------------------------------------
JUMPERS = [
    ("W1", "T4",  "T6",  "signal"),   # V1a plate node == coupling-out tie
    ("W2", "T1",  "T50", "signal"),   # IN -> dry-bypass tap near relay
    ("W3", "T52", "T36", "power"),    # B+1 bus (local -> reservoir)
    ("W4", "T10", "T37", "power"),    # B+2 bus
    ("W5", "T49", "T11", "power"),    # B+3 bus segment
    ("W6", "T11", "T38", "power"),    # B+3 bus segment
]
_GBUSS = ["T5", "T16", "T28", "T56", "T55", "T35", "T32", "T51", "T42", "T54"]
for _i in range(len(_GBUSS) - 1):     # ground buss along bottom edge
    JUMPERS.append((f"WG{_i+1}", _GBUSS[_i], _GBUSS[_i+1], "power"))

# ============================================================================
#  EMITTERS
# ============================================================================
def net_of(tid):
    return T[tid][2] if tid in T else tid

def emit_bom():
    rows = []
    kindname = {"R": "Resistor", "Cf": "Capacitor (film/mica)", "Ce": "Capacitor (electrolytic)",
                "D": "Diode", "IC": "Regulator", "trim": "Trimmer", "socket": "Tube socket", "pot": "Potentiometer",
                "jack": "Jack", "transformer": "Transformer", "relay": "Relay",
                "switch": "Switch", "fuse": "Fuse", "inlet": "Mains inlet", "led": "LED"}
    for c in C:
        rows.append([c["ref"], kindname.get(c["kind"], c["kind"]), c["value"], c["rating"],
                     c["mouser"] or "TBD", f'{net_of(c["a"])} - {net_of(c["b"])}', c["note"]])
    for c in CHASSIS:
        rows.append([c["ref"], kindname.get(c["kind"], c["kind"]), c["value"], "-",
                     c["mouser"] or "TBD", "chassis-mount", c["desc"]])
    with open("bom.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["RefDes", "Category", "Value", "Rating", "Mouser P/N", "Connection", "Notes"])
        w.writerows(rows)
    return len(rows)

def emit_mouser():
    # Mouser BOM upload format: Mouser Part Number, Quantity, Customer Part Number, Description
    agg = {}   # mouser_pn -> [qty, refs, desc]
    for c in C + CHASSIS:
        pn = c.get("mouser") or ""
        if not pn:
            continue
        desc = c.get("note") or c.get("desc") or c["value"]
        key = pn
        if key not in agg:
            agg[key] = [0, [], f'{c["value"]} {desc}']
        agg[key][0] += 1
        agg[key][1].append(c["ref"])
    with open("bom_mouser.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Mouser Part Number", "Quantity 1", "Customer Part Number", "Description"])
        for pn, (qty, refs, desc) in sorted(agg.items()):
            w.writerow([pn, qty, ",".join(refs), desc])
    return len(agg)

def emit_drill_csv():
    with open("turret-drill.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# Hoffman custom turret board - drill coordinate table"])
        w.writerow(["# Origin = lower-left corner of board. Units = inches. Grid = 0.250\""])
        w.writerow([f"# Board size = {BOARD_W:.3f} W x {BOARD_H:.3f} H", "", "", "", ""])
        w.writerow([f"# Turret hole dia = {TURRET_HOLE_D:.3f}\" (3/32\")",
                    f"Mount hole dia = {MOUNT_HOLE_D:.3f}\"", "", "", ""])
        w.writerow(["Hole ID", "X (in)", "Y (in)", "Dia (in)", "Net / Purpose"])
        for tid in sorted(T, key=lambda k: int(k[1:])):
            x, y, net = T[tid]
            w.writerow([tid, f"{x:.3f}", f"{y:.3f}", f"{TURRET_HOLE_D:.3f}", net])
        for mid, x, y in MOUNT_HOLES:
            w.writerow([mid, f"{x:.3f}", f"{y:.3f}", f"{MOUNT_HOLE_D:.3f}", "board mounting hole"])
    return len(T) + len(MOUNT_HOLES)

def emit_drill_svg():
    scale = 96.0  # px per inch (SVG user units at 96dpi -> 1:1 print)
    pad = 0.6
    W = (BOARD_W + 2 * pad) * scale
    Hh = (BOARD_H + 2 * pad) * scale
    def X(x): return (x + pad) * scale
    def Y(y): return (BOARD_H - y + pad) * scale  # flip: y-up -> svg y-down
    e = []
    e.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{Hh:.0f}" '
             f'viewBox="0 0 {W:.0f} {Hh:.0f}">')
    e.append('<rect width="100%" height="100%" fill="white"/>')
    # board outline
    e.append(f'<rect x="{X(0):.1f}" y="{Y(BOARD_H):.1f}" width="{BOARD_W*scale:.1f}" '
             f'height="{BOARD_H*scale:.1f}" fill="none" stroke="#333" stroke-width="1.5"/>')
    # grid dots
    x = MARGIN
    while x <= BOARD_W - MARGIN + 1e-6:
        yy = MARGIN
        while yy <= BOARD_H - MARGIN + 1e-6:
            e.append(f'<circle cx="{X(x):.1f}" cy="{Y(yy):.1f}" r="0.8" fill="#ddd"/>')
            yy += GRID
        x += GRID
    # mounting holes
    for mid, mx, my in MOUNT_HOLES:
        r = MOUNT_HOLE_D / 2 * scale
        e.append(f'<circle cx="{X(mx):.1f}" cy="{Y(my):.1f}" r="{r:.1f}" fill="none" stroke="#c00" stroke-width="1.2"/>')
        e.append(f'<text x="{X(mx):.1f}" y="{Y(my)-r-2:.1f}" font-family="monospace" font-size="8" '
                 f'text-anchor="middle" fill="#c00">{mid}</text>')
    # turrets
    for tid, (tx, ty, net) in T.items():
        r = TURRET_HOLE_D / 2 * scale
        e.append(f'<circle cx="{X(tx):.1f}" cy="{Y(ty):.1f}" r="{r:.1f}" fill="none" stroke="#06c" stroke-width="1.3"/>')
        e.append(f'<circle cx="{X(tx):.1f}" cy="{Y(ty):.1f}" r="1.1" fill="#06c"/>')
        e.append(f'<text x="{X(tx)+r+1:.1f}" y="{Y(ty)-2:.1f}" font-family="monospace" font-size="7" fill="#06c">{tid}</text>')
    # dimension labels
    e.append(f'<text x="{X(BOARD_W/2):.1f}" y="{Y(BOARD_H)+11:.1f}" font-family="sans-serif" '
             f'font-size="10" text-anchor="middle" fill="#333">{BOARD_W:.3f}" (W)</text>')
    e.append(f'<text x="{X(0)-6:.1f}" y="{Y(BOARD_H/2):.1f}" font-family="sans-serif" font-size="10" '
             f'text-anchor="middle" fill="#333" transform="rotate(-90 {X(0)-6:.1f} {Y(BOARD_H/2):.1f})">{BOARD_H:.3f}" (H)</text>')
    e.append(f'<text x="{X(0):.1f}" y="{Hh-6:.1f}" font-family="sans-serif" font-size="8" fill="#888">'
             f'Turret 3/32" (blue) - Mount holes (red) - grid 0.250" - print at 1:1 (96dpi)</text>')
    e.append('</svg>')
    with open("turret-drill.svg", "w") as f:
        f.write("\n".join(e))

def emit_layout_svg():
    scale = 96.0
    pad = 0.6
    W = (BOARD_W + 2 * pad) * scale
    Hh = (BOARD_H + 2 * pad) * scale
    def X(x): return (x + pad) * scale
    def Y(y): return (BOARD_H - y + pad) * scale
    e = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{Hh:.0f}" viewBox="0 0 {W:.0f} {Hh:.0f}">']
    e.append('<rect width="100%" height="100%" fill="#fbfbf7"/>')
    e.append(f'<rect x="{X(0):.1f}" y="{Y(BOARD_H):.1f}" width="{BOARD_W*scale:.1f}" '
             f'height="{BOARD_H*scale:.1f}" fill="#f3ead6" stroke="#333" stroke-width="1.5"/>')
    colors = {"R": "#8a5a2b", "Cf": "#1f6feb", "Ce": "#0a7", "D": "#333", "IC": "#333"}
    for c in C:
        if c["a"] not in T or c["b"] not in T:
            continue
        x1, y1, _ = T[c["a"]]; x2, y2, _ = T[c["b"]]
        col = colors.get(c["kind"], "#555")
        e.append(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" '
                 f'stroke="{col}" stroke-width="2.4" opacity="0.8"/>')
        mx, my = (X((x1+x2)/2)), (Y((y1+y2)/2))
        e.append(f'<text x="{mx:.1f}" y="{my-3:.1f}" font-family="monospace" font-size="7" '
                 f'text-anchor="middle" fill="{col}">{c["ref"]}</text>')
        e.append(f'<text x="{mx:.1f}" y="{my+6:.1f}" font-family="monospace" font-size="6" '
                 f'text-anchor="middle" fill="#666">{c["value"]}</text>')
    # jumper / bus wires: red = power (B+ + ground buss), yellow = signal
    jcol = {"power": "#d00000", "signal": "#e0a800"}
    for jn, a, b, jt in JUMPERS:
        if a not in T or b not in T:
            continue
        x1, y1, _ = T[a]; x2, y2, _ = T[b]
        e.append(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" '
                 f'stroke="{jcol[jt]}" stroke-width="3.4" stroke-linecap="round" opacity="0.95"/>')
    for tid, (tx, ty, net) in T.items():
        e.append(f'<circle cx="{X(tx):.1f}" cy="{Y(ty):.1f}" r="3" fill="#b8860b" stroke="#5a4300"/>')
    for mid, mx, my in MOUNT_HOLES:
        e.append(f'<circle cx="{X(mx):.1f}" cy="{Y(my):.1f}" r="5" fill="none" stroke="#999" stroke-width="1.2"/>')
    # legend for jumper colors
    ly = Hh - 20
    e.append(f'<line x1="{X(0.4):.1f}" y1="{ly:.1f}" x2="{X(0.85):.1f}" y2="{ly:.1f}" stroke="#d00000" stroke-width="3.4" stroke-linecap="round"/>')
    e.append(f'<text x="{X(0.95):.1f}" y="{ly+3:.1f}" font-family="sans-serif" font-size="8" fill="#a00000">power jumper (B+ / ground buss)</text>')
    e.append(f'<line x1="{X(3.4):.1f}" y1="{ly:.1f}" x2="{X(3.85):.1f}" y2="{ly:.1f}" stroke="#e0a800" stroke-width="3.4" stroke-linecap="round"/>')
    e.append(f'<text x="{X(3.95):.1f}" y="{ly+3:.1f}" font-family="sans-serif" font-size="8" fill="#b0860a">signal jumper</text>')
    e.append(f'<text x="{X(BOARD_W/2):.1f}" y="{Hh-8:.1f}" font-family="sans-serif" font-size="8" '
             f'text-anchor="middle" fill="#888">Populated layout - signal flows L-&gt;R - ground buss + B+ buss along bottom</text>')
    e.append('</svg>')
    with open("layout.svg", "w") as f:
        f.write("\n".join(e))

def emit_diylc():
    """Real DIYLC 6.x (.diy) project. Structure/field-templated verbatim from
    DIYLC's own regression .diy files (a Doug Hoffman turret board + pedal
    projects), so it deserializes in DIYLC 6.1.0. Root is org.diylc.core.Project,
    fileVersion 3.46. The turret board carries on-board parts (R/C/D/trimmer) plus
    bus/ground JUMPERS; chassis parts are REAL DIYLC components you can wire from
    the board - tube sockets (B9A) above, pots/jacks/relay(DIL-8)/switch/fuse/LED
    below (PT and IEC are labels). DIYLC y-axis is top-down, so board-y is flipped
    from the drill drawing and offset below the sockets."""
    SU = 'class="org.diylc.core.measures.SizeUnit"'
    RU = 'class="org.diylc.core.measures.ResistanceUnit"'
    CU = 'class="org.diylc.core.measures.CapacitanceUnit"'
    BY0 = 1.60                                        # board top offset (room for sockets above)
    def dy(tid): return BY0 + BOARD_H - T[tid][1]     # flip + offset to DIYLC top-down
    def dx(tid): return T[tid][0]
    def col(tag, r, g, b, a=255):
        return (f"<{tag}><red>{r}</red><green>{g}</green><blue>{b}</blue>"
                f"<alpha>{a}</alpha></{tag}>")
    def size(tag, v):
        return f'<{tag}><value>{v}</value><unit {SU}>in</unit></{tag}>'
    def jpt(x, y):
        return f'<java.awt.Point x="{x:.4f}" y="{y:.4f}"/>'
    def font(sz=14.0, family="Dialog"):
        return ("<font><attributes>"
                "<entry><awt-text-attribute>posture</awt-text-attribute><null/></entry>"
                f"<entry><awt-text-attribute>family</awt-text-attribute><string>{family}</string></entry>"
                "<entry><awt-text-attribute>tracking</awt-text-attribute><null/></entry>"
                "<entry><awt-text-attribute>width</awt-text-attribute><null/></entry>"
                "<entry><awt-text-attribute>transform</awt-text-attribute><null/></entry>"
                "<entry><awt-text-attribute>superscript</awt-text-attribute><null/></entry>"
                f"<entry><awt-text-attribute>size</awt-text-attribute><float>{sz}</float></entry>"
                "<entry><awt-text-attribute>weight</awt-text-attribute><null/></entry>"
                "</attributes></font>")

    def res_value(s):
        s = s.strip()
        if s.endswith(("k", "K")): return s[:-1], "K"
        if s.endswith("M"): return s[:-1], "M"
        return s, "R"
    def cap_value(s):
        s = s.strip()
        if s.lower().endswith("pf"): return s[:-2], "pF"
        if s.lower().endswith("uf"): return s[:-2], "uF"
        if s.lower().endswith("nf"): return s[:-2], "nF"
        return s, "uF"
    VOLTS = [16, 25, 63, 100, 160, 250, 300, 350, 400, 500, 630]
    def cap_voltage(rating):
        n = "".join(ch for ch in rating.split("V")[0] if ch.isdigit() or ch == ".")
        try: rv = float(n)
        except ValueError: rv = 630
        for v in VOLTS:
            if v >= rv: return f"_{v}V"
        return "_630V"

    out = []
    def w(s): out.append(s)
    w('<?xml version="1.0" encoding="UTF-8" ?>')
    w('<org.diylc.core.Project>')
    w('<fileVersion><major>3</major><minor>46</minor><build>0</build></fileVersion>')
    w('<title>Harmonic Tremolo (6G8-A) - Turret Board</title>')
    w('<author>generated</author>')
    w('<description>Standalone tube harmonic tremolo - see notes.md / schematic-trace.md</description>')
    w(f'<width><value>{BOARD_W + 1.5}</value><unit {SU}>in</unit></width>')
    w(f'<height><value>{1.60 + BOARD_H + 1.6}</value><unit {SU}>in</unit></height>')
    w(f'<gridSpacing><value>0.125</value><unit {SU}>in</unit></gridSpacing>')
    w('<components>')

    # --- Board ---
    w('<org.diylc.components.boards.BlankBoard>')
    w('<name>Board1</name><alpha>127</alpha><value></value>')
    w(f'<controlPoints>{jpt(0,BY0)}{jpt(BOARD_W, BY0+BOARD_H)}</controlPoints>')
    w(f'<firstPoint x="0.0" y="{BY0:.4f}"/><secondPoint x="{BOARD_W:.4f}" y="{BY0+BOARD_H:.4f}"/>')
    w(col("boardColor", 204, 204, 204))
    w(col("borderColor", 173, 164, 125))
    w(col("coordinateColor", 182, 182, 182))
    w('<drawCoordinates>true</drawCoordinates><type>SQUARE</type>')
    w('</org.diylc.components.boards.BlankBoard>')

    # --- Turrets ---
    for tid in sorted(T, key=lambda k: int(k[1:])):
        x, y, net = dx(tid), dy(tid), T[tid][2]
        w('<org.diylc.components.connectivity.Turret>')
        w(f'<name>{tid}</name>')
        w(size("size", 0.16))
        w(size("holeSize", round(TURRET_HOLE_D, 4)))
        w(col("color", 224, 192, 76))
        w(f'<point x="{x:.4f}" y="{y:.4f}"/>')
        w(f'<value>{tid} {net}</value>')
        w('</org.diylc.components.connectivity.Turret>')

    # --- Mounting holes as DrillHole components (so they round-trip) ---
    for mid, mx, my in MOUNT_HOLES:
        w('<org.diylc.components.electromechanical.DrillHole>')
        w(f'<name>{mid}</name><alpha>127</alpha>')
        w(size("diameter", round(MOUNT_HOLE_D, 4)))
        w(col("color", 160, 160, 160))
        w(f'<point x="{mx:.4f}" y="{BY0 + BOARD_H - my:.4f}"/>')
        w('</org.diylc.components.electromechanical.DrillHole>')

    # --- On-board components (both endpoints on turrets) ---
    for c in C:
        a, b, kind = c["a"], c["b"], c["kind"]
        if kind == "trim":
            if a not in T or b not in T or "T48" not in T:
                continue
            rv, ru = res_value(c["value"].split()[0])
            w('<org.diylc.components.passive.TrimmerPotentiometer>')
            w(f'<name>{c["ref"]}</name><alpha>127</alpha>')
            w(f'<controlPoints>{jpt(dx(a),dy(a))}{jpt(dx("T48"),dy("T48"))}{jpt(dx(b),dy(b))}</controlPoints>')
            w(f'<resistance><value>{rv}</value><unit {RU}>{ru}</unit></resistance>')
            w('<orientation>DEFAULT</orientation><taper>LIN</taper>')
            w(col("bodyColor", 255, 255, 224)); w(col("borderColor", 142, 142, 56))
            w('<display>NAME</display><type>FLAT_SMALL</type>')
            w('</org.diylc.components.passive.TrimmerPotentiometer>')
            continue
        if a not in T or b not in T:
            continue                      # off-board (relay coil, heater legs)
        p1, p2 = jpt(dx(a), dy(a)), jpt(dx(b), dy(b))
        if kind == "R":
            rv, ru = res_value(c["value"])
            w('<org.diylc.components.passive.Resistor>')
            w(f'<name>{c["ref"]}</name><alpha>88</alpha>')
            w(size("length", 0.25)); w(size("width", 0.09))
            w(f'<points>{p1}{p2}</points>')
            w(col("bodyColor", 130, 207, 253)); w(col("borderColor", 91, 144, 177))
            w(col("labelColor", 0, 0, 0)); w(col("leadColor", 204, 204, 204))
            w('<display>BOTH</display><flipStanding>false</flipStanding>')
            w(f'<value><value>{rv}</value><unit {RU}>{ru}</unit></value>')
            w('<power>HALF</power><colorCode>NONE</colorCode><shape>Tubular</shape>')
            w('</org.diylc.components.passive.Resistor>')
        elif kind in ("Cf", "Ce"):
            cv, cu = cap_value(c["value"])
            volt = cap_voltage(c["rating"])
            is_elec = "elec" in c["rating"].lower()
            if is_elec:
                w('<org.diylc.components.passive.RadialElectrolytic>')
                w(f'<name>{c["ref"]}</name><alpha>88</alpha>')
                w(size("length", 0.2))
                w(f'<points>{p1}{p2}</points>')
                w(col("bodyColor", 107, 109, 206)); w(col("borderColor", 74, 76, 144))
                w(col("labelColor", 0, 0, 0)); w(col("leadColor", 204, 204, 204))
                w('<display>BOTH</display><flipStanding>false</flipStanding>')
                w(size("pinSpacing", 0.1))
                w(f'<value><value>{cv}</value><unit {CU}>{cu}</unit></value>')
                w(f'<voltage>{volt}</voltage>')
                w(col("markerColor", 140, 172, 234)); w(col("tickColor", 255, 255, 255))
                w('<polarized>true</polarized><folded>false</folded>')
                w(size("height", 0.4)); w('<invert>false</invert>')
                w('</org.diylc.components.passive.RadialElectrolytic>')
            else:
                w('<org.diylc.components.passive.RadialFilmCapacitor>')
                w(f'<name>{c["ref"]}</name><alpha>88</alpha>')
                w(size("length", 0.25)); w(size("width", 0.09))
                w(f'<points>{p1}{p2}</points>')
                w(col("bodyColor", 255, 128, 0)); w(col("borderColor", 178, 89, 0))
                w(col("labelColor", 0, 0, 0)); w(col("leadColor", 204, 204, 204))
                w('<display>BOTH</display><flipStanding>false</flipStanding>')
                w(size("pinSpacing", 0.1))
                w(f'<value><value>{cv}</value><unit {CU}>{cu}</unit></value>')
                w(f'<voltage>{volt}</voltage>')
                w('</org.diylc.components.passive.RadialFilmCapacitor>')
        elif kind == "D":
            w('<org.diylc.components.semiconductors.DiodePlastic>')
            w(f'<name>{c["ref"]}</name><alpha>88</alpha>')
            w(size("length", 0.22)); w(size("width", 0.1))
            w(f'<points>{p1}{p2}</points>')
            w(col("bodyColor", 64, 64, 64)); w(col("borderColor", 44, 44, 44))
            w(col("labelColor", 0, 0, 0)); w(col("leadColor", 204, 204, 204))
            w('<display>NAME</display><flipStanding>false</flipStanding><value></value>')
            w(col("markerColor", 221, 221, 221))
            w('</org.diylc.components.semiconductors.DiodePlastic>')
        elif kind == "IC":     # 78L12 TO-92 (3-pin) - annotate as label at midpoint
            mx, my = (dx(a) + dx(b)) / 2, (dy(a) + dy(b)) / 2
            _label(w, font, f'{c["ref"]} {c["value"]}', mx, my, 12.0)

    # --- Jumper / bus wires (same-net turrets) ---
    jlead = {"power": (255, 0, 0), "signal": (210, 175, 0)}
    for jn, a, b, jt in JUMPERS:
        if a not in T or b not in T:
            continue
        w('<org.diylc.components.connectivity.Jumper>')
        w(f'<name>{jn}</name><alpha>127</alpha>')
        w(f'<points>{jpt(dx(a), dy(a))}{jpt(dx(b), dy(b))}</points>')
        w(col("bodyColor", 255, 255, 255)); w(col("borderColor", 0, 0, 0))
        w(col("labelColor", 0, 0, 0)); w(col("leadColor", *jlead[jt]))
        w('<display>NAME</display><flipStanding>false</flipStanding>')
        w('</org.diylc.components.connectivity.Jumper>')

    # --- Chassis-mounted parts as real DIYLC components (wire from board) ---
    # Sockets mount ABOVE the board, pots/jacks BELOW - standard Hoffman convention.
    yb = BY0 + BOARD_H + 0.60
    POS = {
        "V1": (1.15, 0.80), "V2": (2.55, 0.80), "V3": (3.55, 0.80),
        "J1": (0.55, yb), "P1": (1.70, yb), "P2": (2.70, yb), "P3": (3.70, yb),
        "J3": (4.70, yb), "J2": (5.45, yb),
        "LED1": (5.10, BY0 + BOARD_H + 0.25), "K1": (3.95, BY0 + BOARD_H + 0.35),
        "SW1": (5.95, BY0 + BOARD_H + 0.35), "F1": (6.20, BY0 + BOARD_H + 0.05),
        "T101": (5.05, 0.60), "IEC1": (6.00, 0.95),
    }
    SOCK = [(0, 0), (0.24, -0.335), (0.39, -0.13), (0.39, 0.125), (0.24, 0.33),
            (0, 0.41), (-0.245, 0.33), (-0.395, 0.125), (-0.395, -0.13), (-0.245, -0.335)]
    POT = [(0, 0), (-0.2, 0), (-0.4, 0)]
    JACK = [(0, 0), (-0.2, 0.4), (-0.9, 0.3)]
    DIP8 = [(0, 0), (0, 0.1), (0, 0.2), (0, 0.3), (0.3, 0), (0.3, 0.1), (0.3, 0.2), (0.3, 0.3)]
    SW6 = [(0, 0), (0, 0.2), (0, 0.4), (0.2, 0), (0.2, 0.2), (0.2, 0.4)]
    FUSE = [(0, 0), (0, 0.2)]
    def cp(cx, cy, offs): return "".join(jpt(cx + ox, cy + oy) for ox, oy in offs)
    for c in CHASSIS:
        ref, kind, val = c["ref"], c["kind"], c["value"]
        cx, cy = POS.get(ref, (0.3, yb + 0.7))
        if kind == "socket":
            w('<org.diylc.components.tube.TubeSocket>')
            w(f'<name>{ref}</name><alpha>127</alpha><base>B9A</base><type></type><angle>180</angle>')
            w(col("color", 247, 247, 239))
            w(f'<controlPoints>{cp(cx, cy, SOCK)}</controlPoints>')
            w('</org.diylc.components.tube.TubeSocket>')
        elif kind == "pot":
            rv, ru = res_value(val.split()[0])
            w('<org.diylc.components.passive.PotentiometerPanel>')
            w(f'<name>{ref}</name><alpha>127</alpha>')
            w(f'<controlPoints>{cp(cx, cy, POT)}</controlPoints>')
            w(f'<resistance><value>{rv}</value><unit {RU}>{ru}</unit></resistance>')
            w('<orientation>_180</orientation><taper>LOG</taper>')
            w(f'<bodyDiameter><value>16.0</value><unit {SU}>mm</unit></bodyDiameter>')
            w(size("spacing", 0.2)); w(size("lugDiameter", 0.15))
            w(col("bodyColor", 192, 192, 192)); w(col("borderColor", 128, 128, 128))
            w(col("nutColor", 203, 213, 219)); w(col("waferColor", 205, 133, 0))
            w('<type>ThroughHole</type><showShaft>false</showShaft>')
            w('</org.diylc.components.passive.PotentiometerPanel>')
        elif kind == "jack":
            typ = "STEREO" if "TRS" in val else "MONO"
            w('<org.diylc.components.electromechanical.OpenJack1__4>')
            w(f'<name>{ref}</name><alpha>127</alpha><value></value>')
            w(f'<controlPoints>{cp(cx, cy, JACK)}</controlPoints>')
            w(f'<orientation>_90</orientation><type>{typ}</type><showLabels>true</showLabels>')
            w('</org.diylc.components.electromechanical.OpenJack1__4>')
        elif kind == "relay":
            w('<org.diylc.components.semiconductors.DIL__IC>')
            w(f'<name>{ref}</name><alpha>88</alpha><value></value><orientation>DEFAULT</orientation>')
            w('<pinCount>_8</pinCount>')
            w(size("pinSpacing", 0.1)); w(size("rowSpacing", 0.3))
            w(f'<controlPoints>{cp(cx, cy, DIP8)}</controlPoints>')
            w('<display>BOTH</display>')
            w(col("bodyColor", 128, 128, 128)); w(col("borderColor", 89, 89, 89))
            w(col("labelColor", 0, 0, 0)); w(col("indentColor", 89, 89, 89))
            w('<displayNumbers>NO</displayNumbers>')
            w('</org.diylc.components.semiconductors.DIL__IC>')
        elif kind == "switch":
            w('<org.diylc.components.electromechanical.MiniToggleSwitch>')
            w(f'<name>{ref}</name><alpha>127</alpha>')
            w(f'<controlPoints>{cp(cx, cy, SW6)}</controlPoints>')
            w('<switchType>DPDT</switchType><orientation>VERTICAL</orientation>')
            w(size("spacing", 0.2))
            w(col("bodyColor", 50, 153, 204)); w(col("borderColor", 35, 107, 142))
            w('</org.diylc.components.electromechanical.MiniToggleSwitch>')
        elif kind == "fuse":
            w('<org.diylc.components.electromechanical.FuseHolderPanel>')
            w(f'<name>{ref}</name><alpha>127</alpha><value></value><orientation>VERTICAL</orientation>')
            w('<hasFuse>false</hasFuse><display>VALUE</display>')
            w(f'<controlPoints>{cp(cx, cy, FUSE)}</controlPoints>')
            w(col("bodyColor", 85, 85, 85)); w(col("borderColor", 59, 59, 59)); w(col("labelColor", 0, 0, 0))
            w('</org.diylc.components.electromechanical.FuseHolderPanel>')
        elif kind == "led":
            w('<org.diylc.components.semiconductors.LED>')
            w(f'<name>{ref}</name><alpha>127</alpha>')
            w(f'<length><value>5.0</value><unit {SU}>mm</unit></length>')
            w(f'<width><value>5.0</value><unit {SU}>mm</unit></width>')
            w(f'<points>{jpt(cx, cy)}{jpt(cx - 0.2, cy)}</points>')
            w(col("bodyColor", 93, 252, 10)); w(col("borderColor", 65, 176, 7))
            w(col("labelColor", 0, 0, 0)); w(col("leadColor", 204, 204, 204))
            w('<display>NAME</display><flipStanding>false</flipStanding><value></value>')
            w('</org.diylc.components.semiconductors.LED>')
        else:                                  # transformer, IEC inlet -> label glyph
            _label(w, font, f'{ref} {val}', cx, cy, 11.0)

    # --- Lead wires: off-board component pins -> board turrets (HookupWire) ---
    # 12AX7 (B9A): pin1/2/3 = plate/grid/cathode of triode-1, pin6/7/8 = triode-2,
    # pins 4/5/9 = heaters. TubeSocket control-point index == pin number.
    OFF = {"socket": SOCK, "pot": POT, "jack": JACK, "relay": DIP8, "led": [(0, 0), (-0.2, 0)]}
    kind_of = {c["ref"]: c["kind"] for c in CHASSIS}

    def pinxy(spec):
        who, idx = spec
        if who == "T":
            return dx(idx), dy(idx)
        cx0, cy0 = POS[who]
        ox, oy = OFF[kind_of[who]][idx]
        return cx0 + ox, cy0 + oy

    def hookup(name, a, b, hexcol):
        (x1, y1), (x2, y2) = pinxy(a), pinxy(b)
        pts = [(x1, y1), (x1 + (x2 - x1) / 3, y1 + (y2 - y1) / 3),
               (x1 + 2 * (x2 - x1) / 3, y1 + 2 * (y2 - y1) / 3), (x2, y2)]
        w('<org.diylc.components.connectivity.HookupWire>')
        w(f'<name>{name}</name><alpha>127</alpha>')
        w('<controlPoints2>' + ''.join(f'<point x="{px:.4f}" y="{py:.4f}"/>' for px, py in pts) + '</controlPoints2>')
        w(f'<color hex="{hexcol}"/>')
        w('<pointCount>FOUR</pointCount><style>SOLID</style><smooth>true</smooth>')
        w('<lastUpdatePointIndex>-1</lastUpdatePointIndex><gauge>_22</gauge>')
        w('<striped>false</striped><stripeColor hex="ffff00"/>')
        w('</org.diylc.components.connectivity.HookupWire>')

    PL, GR, KA, HT, GN, SG, RL = "cc4400", "1f6feb", "555555", "0a8a0a", "000000", "8a5a2b", "8000c0"
    #                pin(idx)         turret/pin        color   note
    WIRES = [
        # V1  (V1a driver = triode1 -> pins1/2/3 ; V1b follower = triode2 -> pins6/7/8)
        ("wV1a_p", ("V1", 1), ("T", "T4"),  PL), ("wV1a_g", ("V1", 2), ("T", "T2"),  GR), ("wV1a_k", ("V1", 3), ("T", "T3"),  KA),
        ("wV1b_p", ("V1", 6), ("T", "T52"), PL), ("wV1b_g", ("V1", 7), ("T", "T29"), GR), ("wV1b_k", ("V1", 8), ("T", "T30"), KA),
        # V2  (HF modulator = triode1 ; LF modulator = triode2 ; shared cathode T14)
        ("wV2h_p", ("V2", 1), ("T", "T12"), PL), ("wV2h_g", ("V2", 2), ("T", "T8"),  GR), ("wV2h_k", ("V2", 3), ("T", "T14"), KA),
        ("wV2l_p", ("V2", 6), ("T", "T13"), PL), ("wV2l_g", ("V2", 7), ("T", "T9"),  GR), ("wV2l_k", ("V2", 8), ("T", "T14"), KA),
        # V3  (LFO oscillator = triode1 ; cathodyne = triode2)
        ("wV3o_p", ("V3", 1), ("T", "T22"), PL), ("wV3o_g", ("V3", 2), ("T", "T23"), GR), ("wV3o_k", ("V3", 3), ("T", "T24"), KA),
        ("wV3c_p", ("V3", 6), ("T", "T19"), PL), ("wV3c_g", ("V3", 7), ("T", "T20"), GR), ("wV3c_k", ("V3", 8), ("T", "T21"), KA),
        # Heaters: pins 4 & 5 chained V1-V2-V3 (twisted pair -> 6.3VAC winding)
        ("wH4a", ("V1", 4), ("V2", 4), HT), ("wH4b", ("V2", 4), ("V3", 4), HT),
        ("wH5a", ("V1", 5), ("V2", 5), HT), ("wH5b", ("V2", 5), ("V3", 5), HT),
        # Jacks
        ("wJ1t", ("J1", 0), ("T", "T1"),  SG), ("wJ1s", ("J1", 1), ("T", "T5"),  GN),
        ("wJ2s", ("J2", 1), ("T", "T51"), GN),
        # OUTPUT LEVEL pot P3: lug1=in(FOL_OUT), wiper=out(->J2 tip), lug3=gnd
        ("wP3a", ("P3", 0), ("T", "T31"), SG), ("wP3w", ("P3", 1), ("J2", 0), SG), ("wP3g", ("P3", 2), ("T", "T51"), GN),
        # SPEED pot P1 [verify mechanization]: variable R in the phase-shift network
        ("wP1a", ("P1", 0), ("T", "T27"), SG), ("wP1w", ("P1", 1), ("T", "T23"), SG),
        # INTENSITY pot P2 [verify]: LFO depth into the cathodyne
        ("wP2a", ("P2", 0), ("T", "T22"), SG), ("wP2w", ("P2", 1), ("T", "T20"), SG), ("wP2g", ("P2", 2), ("T", "T28"), GN),
        # LED
        ("wLEDa", ("LED1", 0), ("T", "T47"), PL), ("wLEDk", ("LED1", 1), ("T", "T51"), GN),
        # Relay K1 (DIL-8) [VERIFY against NA12W-K datasheet pinout]:
        ("wK1cA", ("K1", 0), ("T", "T46"), RL),  # coil+ <- 12V
        ("wK1cm", ("K1", 1), ("T", "T29"), SG),  # pole-1 common -> follower grid
        ("wK1nc", ("K1", 2), ("T", "T34"), SG),  # pole-1 NC -> bypass (dry)
        ("wK1no", ("K1", 3), ("T", "T48"), SG),  # pole-1 NO -> engaged (trim wiper)
        ("wK1cB", ("K1", 7), ("T", "T55"), GN),  # coil- -> gnd (through footswitch)
        # Footswitch TRS J3: tip = switched 12V to coil, sleeve = gnd
        ("wJ3t", ("J3", 0), ("T", "T46"), RL), ("wJ3s", ("J3", 1), ("T", "T5"), GN),
    ]
    for nm, a, b, hx in WIRES:
        try:
            hookup(nm, a, b, hx)
        except (KeyError, IndexError):
            pass   # skip if a referenced part/turret isn't present

    _label(w, font, "sockets above / pots+jacks below (chassis-mounted)", 0.2, yb + 0.5, 10.0)

    w('</components>')
    w('<groups/>')
    w('<lockedLayers><int>2</int></lockedLayers>')
    w('<hiddenLayers/>')
    w(font(14.0, "Lucida Console"))
    w('</org.diylc.core.Project>')
    with open("harmonic-tremolo.diy", "w") as f:
        f.write("\n".join(out) + "\n")


def _label(w, font, text, x, y, sz):
    w('<org.diylc.components.misc.Label>')
    w(f'<name>{text}</name>')
    w(f'<point x="{x:.4f}" y="{y:.4f}"/>')
    w(f'<text>{text}</text>')
    w(font(sz))
    w('<color><red>0</red><green>0</green><blue>0</blue><alpha>255</alpha></color>')
    w('<center>false</center><horizontalAlignment>LEFT</horizontalAlignment>')
    w('<verticalAlignment>CENTER</verticalAlignment><orientation>DEFAULT</orientation>')
    w('</org.diylc.components.misc.Label>')

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    n_bom = emit_bom()
    n_mou = emit_mouser()
    n_holes = emit_drill_csv()
    emit_drill_svg()
    emit_layout_svg()
    emit_diylc()
    print(f"BOM rows:            {n_bom}")
    print(f"Mouser line items:   {n_mou}")
    print(f"Drill holes:         {n_holes} ({len(T)} turrets + {len(MOUNT_HOLES)} mounting)")
    print(f"Board:               {BOARD_W}\" x {BOARD_H}\", grid {GRID}\", turret {TURRET_HOLE_D}\"")
    print("Wrote: bom.csv, bom_mouser.csv, turret-drill.csv, turret-drill.svg, layout.svg, harmonic-tremolo.diy")
