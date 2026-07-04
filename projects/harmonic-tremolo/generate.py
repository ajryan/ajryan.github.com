#!/usr/bin/env python3
"""
Harmonic Tremolo Unit - file generator (single source of truth).

Emits, from one component/turret dataset so everything stays consistent:
  - bom.csv              human-readable bill of materials
  - bom_mouser.csv       Mouser BOM-import format (Mouser P/N, qty, customer ref)
  - turret-drill.csv     turret hole coordinate table (Hoffman custom-board format)
  - turret-drill.svg     dimensioned drill drawing (printable at 1:1)
  - layout.svg           populated turret-board layout (component placement)
  - harmonic-tremolo.diy DIYLC v4 project (best-effort; verify in DIYLC 4.x)

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
BOARD_W = 8.000          # in  (Hoffman boards up to ~9" long)
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
# Rows (y): 2.750 top, 2.250, 1.750, 1.250, 0.750, 0.375(PSU rail)
# Laid out left->right by signal flow; PSU + relay supply on bottom rail.
# ----------------------------------------------------------------------------
R_TOP, R_2, R_3, R_4, R_5, R_PSU = 2.750, 2.250, 1.750, 1.250, 0.750, 0.375

T = {}  # id -> (x, y, net)
def turret(tid, x, y, net):
    assert tid not in T, f"dup turret {tid}"
    T[tid] = (round(x, 3), round(y, 3), net)

# --- Input / V1a driver stage (left end, nearest input jack) ---
turret("T1",  0.500, R_TOP, "IN")          # from input jack tip (engaged in) / relay
turret("T2",  0.500, R_2,   "V1a_G")       # V1a grid node (after grid stopper)
turret("T3",  0.500, R_4,   "V1a_K")       # V1a cathode
turret("T4",  1.000, R_TOP, "V1a_P")       # V1a plate
turret("T5",  1.000, R_4,   "GND_1")       # ground bus (cathode bypass rtn)
turret("T6",  1.500, R_TOP, "DRV_OUT")     # V1a plate coupling out

# --- HPF / LPF audio split ---
turret("T7",  2.000, R_TOP, "SPLIT")       # split node
turret("T8",  2.000, R_2,   "HF_G")        # to HF mixer grid (high-pass)
turret("T9",  2.000, R_3,   "LF_G")        # to LF mixer grid (low-pass)

# --- Mixer / modulator triodes V2a (HF), V2b (LF) ---
turret("T10", 2.500, R_2,   "HF_G")        # HF mixer grid tie
turret("T11", 2.500, R_3,   "LF_G")        # LF mixer grid tie
turret("T12", 3.000, R_TOP, "HF_P")        # V2a plate
turret("T13", 3.000, R_3,   "LF_P")        # V2b plate
turret("T14", 2.500, R_4,   "MIX_K")       # shared mixer cathode
turret("T15", 3.500, R_TOP, "MIX")         # mixer plates combined -> follower
turret("T16", 2.500, R_5,   "GND_2")       # ground bus

# --- LFO bias injection to mixer grids (from cathodyne, via Intensity) ---
turret("T17", 3.000, R_4,   "BIAS_HF")     # antiphase bias to HF grid
turret("T18", 3.000, R_5,   "BIAS_LF")     # antiphase bias to LF grid

# --- Cathodyne phase splitter V3b + LFO oscillator V3a (right-center) ---
turret("T19", 4.000, R_TOP, "CATH_P")      # cathodyne plate (antiphase A)
turret("T20", 4.000, R_2,   "CATH_G")      # cathodyne grid (from LFO)
turret("T21", 4.000, R_3,   "CATH_K")      # cathodyne cathode (antiphase B)
turret("T22", 4.500, R_TOP, "LFO_P")       # LFO oscillator plate
turret("T23", 4.500, R_2,   "LFO_G")       # LFO oscillator grid
turret("T24", 4.500, R_4,   "LFO_K")       # LFO oscillator cathode
turret("T25", 5.000, R_2,   "PS1")         # phase-shift network node 1
turret("T26", 5.000, R_3,   "PS2")         # phase-shift network node 2
turret("T27", 5.000, R_4,   "PS3")         # phase-shift network node 3 (-> Speed pot)
turret("T28", 4.000, R_5,   "GND_3")       # ground bus

# --- Cathode follower output V1b (right of mixers) ---
turret("T29", 5.500, R_TOP, "FOL_G")       # follower grid (relay-selected signal)
turret("T30", 6.000, R_TOP, "FOL_K")       # follower cathode = output
turret("T31", 6.000, R_2,   "FOL_OUT")     # follower output coupling -> level pot
turret("T32", 5.500, R_3,   "GND_4")       # ground bus

# --- Relay true-bypass board tie points (relay is chassis/socket mounted) ---
turret("T33", 6.500, R_TOP, "RLY_ENG")     # relay common: engaged (=MIX)
turret("T34", 6.500, R_2,   "RLY_BYP")     # relay common: bypass (=IN dry)
turret("T35", 6.500, R_3,   "GND_5")       # ground bus / pop-suppression bleed return

# --- PSU filter nodes + rectifier (bottom rail, PT end / right) ---
turret("T36", 7.000, R_TOP, "BPLUS1")      # reservoir node B+1
turret("T37", 7.000, R_2,   "BPLUS2")      # B+2 (mixer plates)
turret("T38", 7.000, R_3,   "BPLUS3")      # B+3 (driver + LFO)
turret("T39", 7.500, R_TOP, "RECT_AC1")    # rectifier AC in 1 (190V)
turret("T40", 7.500, R_2,   "RECT_AC2")    # rectifier AC in 2 (190V)
turret("T41", 7.500, R_3,   "HTR_CT")      # heater DC-elevation reference
turret("T42", 7.000, R_5,   "GND_PSU")     # PSU ground / CT return

# --- 12V relay supply (heater-derived doubler + regulator), bottom rail ---
turret("T43", 5.500, R_PSU, "AC63")        # 6.3VAC tap in
turret("T44", 6.000, R_PSU, "DBL")         # voltage-doubler mid node
turret("T45", 6.500, R_PSU, "V16")         # ~16VDC unregulated
turret("T46", 7.000, R_PSU, "V12")         # 12VDC regulated (relay + LED)
turret("T47", 7.500, R_PSU, "LED_A")       # LED anode tie (wires to panel LED)

# ----------------------------------------------------------------------------
# Component list. Each: ref, kind, value, rating, mouser, from_turret, to_turret, note
# mouser="" means not confirmed / builder-select. kind drives BOM category + DIYLC glyph.
# ----------------------------------------------------------------------------
# NOTE ON VALUES: entries flagged (*) in `note` are NOT confirmed against a
# verified 6G8-A schematic image - see notes.md. They use well-documented
# harmonic-vibrato values and must be checked against the user's schematic.
C = []
def comp(ref, kind, value, rating, mouser, a, b, note=""):
    C.append(dict(ref=ref, kind=kind, value=value, rating=rating,
                  mouser=mouser, a=a, b=b, note=note))

# ---- Resistors ----
comp("R1", "R", "68k",  "1/2W CF", "594-5083NW68K000J", "T1",  "T2",  "V1a grid stopper")
comp("R2", "R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T2",  "T5",  "V1a grid leak")
comp("R3", "R", "100k", "1/2W CF", "594-5083NW100K00J", "T4",  "T38", "V1a plate load (*)")
comp("R4", "R", "1.5k", "1/2W CF", "594-5083NW1K5000J", "T3",  "T5",  "V1a cathode (*)")
comp("R5", "R", "220k", "1/2W CF", "594-5083NW220K00J", "T7",  "T9",  "LPF series (split) - CONFIRMED")
comp("R6", "R", "220k", "1/2W CF", "594-5083NW220K00J", "T8",  "T16", "HF grid reference (*)")
comp("R7", "R", "100k", "1/2W CF", "594-5083NW100K00J", "T12", "T37", "V2a (HF) plate load (*)")
comp("R8", "R", "100k", "1/2W CF", "594-5083NW100K00J", "T13", "T37", "V2b (LF) plate load (*)")
comp("R9", "R", "1.5k", "1/2W CF", "594-5083NW1K5000J", "T14", "T16", "mixer shared cathode (*)")
comp("R10","R", "3.3M", "1/2W CF", "594-5083NW3M3000J", "T17", "T10", "HF grid LFO-inject / leak (*)")
comp("R11","R", "3.3M", "1/2W CF", "594-5083NW3M3000J", "T18", "T11", "LF grid LFO-inject / leak (*)")
comp("R12","R", "100k", "1/2W CF", "594-5083NW100K00J", "T19", "T36", "cathodyne plate load (*)")
comp("R13","R", "100k", "1/2W CF", "594-5083NW100K00J", "T21", "T28", "cathodyne cathode load (*)")
comp("R14","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T20", "T28", "cathodyne grid leak (*)")
comp("R15","R", "220k", "1/2W CF", "594-5083NW220K00J", "T22", "T38", "LFO plate load (*)")
comp("R16","R", "2.2k", "1/2W CF", "594-5083NW2K2000J", "T24", "T28", "LFO cathode (*)")
comp("R17","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T23", "T25", "phase-shift R1 (*)")
comp("R18","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T25", "T26", "phase-shift R2 (*)")
comp("R19","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T26", "T27", "phase-shift R3 (*)")
comp("R20","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T29", "T35", "follower grid leak (grid at 0V DC)")
comp("R21","R", "22k",  "1/2W CF", "594-5083NW22K000J", "T30", "T42", "follower cathode load / output tap")
comp("R22","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T34", "T35", "bypass-node bleed (pop supp)")
comp("R31","R", "1M",   "1/2W CF", "594-5083NW1M0000J", "T33", "T35", "engaged-node bleed (pop supp)")
comp("R23","R", "4.7k", "1W  MO",  "71-CMF60-4.7K-E3",  "T36", "T37", "B+1->B+2 dropper")
comp("R24","R", "10k",  "1W  MO",  "71-CMF60-10K-E3",   "T37", "T38", "B+2->B+3 dropper")
comp("R25","R", "220k", "1/2W CF", "594-5083NW220K00J", "T36", "T41", "heater elevation divider top")
comp("R26","R", "100k", "1/2W CF", "594-5083NW100K00J", "T41", "T42", "heater elevation divider bot")
comp("R27","R", "1k",   "1/2W CF", "594-5083NW1K0000J", "T46", "LED_A", "LED series (12V -> LED anode)")
comp("R28","R", "220k", "1W  MO",  "71-CMF60-220K-E3",  "T36", "T42", "safety bleeder across B+1 (drains B+ at power-off)")
comp("R29","R", "100",  "1/2W CF", "594-5083NW100R00J", "HTR_A", "HTR_CT", "heater artificial-CT / elevation tie")
comp("R30","R", "100",  "1/2W CF", "594-5083NW100R00J", "HTR_B", "HTR_CT", "heater artificial-CT / elevation tie")

# ---- Capacitors ----
comp("C1",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T6",  "T7",  "V1a output coupling")
comp("C2",  "Cf", "250pF",   "500V mica", "80-DM15FD251JO3",   "T7",  "T8",  "HPF to HF mixer - CONFIRMED")
comp("C3",  "Cf", "0.005uF", "630V film", "80-R82DC3470DQ50J", "T7",  "T9",  "LPF to LF mixer (*)")
comp("C4",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T12", "T15", "HF mixer output coupling")
comp("C5",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T13", "T15", "LF mixer output coupling")
comp("C6",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T15", "T33", "mixer -> relay engaged coupling")
comp("C7",  "Cf", "0.022uF", "630V film", "80-R82EC3220DQ60J", "T1",  "T34", "dry -> relay bypass coupling")
comp("C8",  "Cf", "0.1uF",   "630V film", "80-R82IC3100DQ50J", "T31", "T33", "follower output coupling")
comp("C9",  "Cf", "0.02uF",  "630V film", "80-R82DC3200DQ50J", "T22", "T20", "LFO->cathodyne coupling (*)")
comp("C10", "Cf", "0.01uF",  "630V film", "80-R82DC3100DQ50J", "T23", "T25", "phase-shift C1 (*)")
comp("C11", "Cf", "0.01uF",  "630V film", "80-R82DC3100DQ50J", "T25", "T26", "phase-shift C2 (*)")
comp("C12", "Cf", "0.01uF",  "630V film", "80-R82DC3100DQ50J", "T26", "T27", "phase-shift C3 (*)")
comp("C13", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T36", "T42", "B+1 reservoir")
comp("C14", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T37", "T42", "B+2 filter")
comp("C15", "Ce", "22uF",    "450V elec", "80-PEG124KG422QL",  "T38", "T42", "B+3 filter")
comp("C16", "Ce", "0.1uF",   "630V film", "80-R82IC3100DQ50J", "T41", "T42", "heater elevation bypass")
comp("C17", "Ce", "100uF",   "35V elec",  "667-EEU-FR1V101",   "T43", "T44", "doubler C1")
comp("C18", "Ce", "100uF",   "35V elec",  "667-EEU-FR1V101",   "T44", "T45", "doubler C2")
comp("C19", "Ce", "100uF",   "25V elec",  "667-EEU-FR1E101",   "T46", "T42", "12V reg output cap")

# ---- Diodes / rectifier / regulator ----
comp("D1", "D", "1N4007", "1000V 1A", "512-1N4007", "T39", "T36", "HV rectifier + (CT full-wave)")
comp("D2", "D", "1N4007", "1000V 1A", "512-1N4007", "T40", "T36", "HV rectifier - (CT full-wave)")
comp("D3", "D", "1N4007", "1000V 1A", "512-1N4007", "T43", "T44", "doubler diode 1")
comp("D4", "D", "1N4007", "1000V 1A", "512-1N4007", "T44", "T45", "doubler diode 2")
comp("U1", "IC","78L12",  "TO-92 12V", "511-L78L12ACZ",  "T45", "T46", "12V linear regulator")
comp("D5", "D", "1N4007", "1000V 1A", "512-1N4007", "RLY_COIL+", "RLY_COIL-", "relay coil flyback diode (at relay)")

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
    dict(ref="P1", kind="pot", value="5M audio", mouser="",
         desc="SPEED (LFO phase-shift) (*)", x=3.0, y=0.9),
    dict(ref="P2", kind="pot", value="1M audio", mouser="588-P1M-A",
         desc="INTENSITY (LFO depth to mixers) (*)", x=5.0, y=0.9),
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

# ============================================================================
#  EMITTERS
# ============================================================================
def net_of(tid):
    return T[tid][2] if tid in T else tid

def emit_bom():
    rows = []
    kindname = {"R": "Resistor", "Cf": "Capacitor (film/mica)", "Ce": "Capacitor (electrolytic)",
                "D": "Diode", "IC": "Regulator", "socket": "Tube socket", "pot": "Potentiometer",
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
    for tid, (tx, ty, net) in T.items():
        e.append(f'<circle cx="{X(tx):.1f}" cy="{Y(ty):.1f}" r="3" fill="#b8860b" stroke="#5a4300"/>')
    for mid, mx, my in MOUNT_HOLES:
        e.append(f'<circle cx="{X(mx):.1f}" cy="{Y(my):.1f}" r="5" fill="none" stroke="#999" stroke-width="1.2"/>')
    e.append(f'<text x="{X(BOARD_W/2):.1f}" y="{Hh-8:.1f}" font-family="sans-serif" font-size="8" '
             f'text-anchor="middle" fill="#888">Populated layout - signal flows L-&gt;R - PSU/relay-supply on bottom rail</text>')
    e.append('</svg>')
    with open("layout.svg", "w") as f:
        f.write("\n".join(e))

def emit_diylc():
    """Best-effort DIYLC v4 (.diy) XML. Open in DIYLC 4.x and verify/adjust.
    Coordinates in inches; DIYLC point coords may need rescale on import."""
    PPI = 1.0  # write inches directly; DIYLC grid set to 0.25in below
    proj = ET.Element("project")
    fv = ET.SubElement(proj, "fileVersion")
    for tag, val in (("major", "4"), ("minor", "27"), ("build", "0")):
        ET.SubElement(fv, tag).text = val
    ET.SubElement(proj, "title").text = "Harmonic Tremolo Unit (6G8-A based)"
    ET.SubElement(proj, "author").text = "generated"
    ET.SubElement(proj, "description").text = "Standalone tube harmonic tremolo - see notes.md"
    w = ET.SubElement(proj, "width"); w.set("value", "12.0"); w.set("unit", "in")
    h = ET.SubElement(proj, "height"); h.set("value", "8.0"); h.set("unit", "in")
    gs = ET.SubElement(proj, "gridSpacing"); gs.set("value", "0.25"); gs.set("unit", "in")
    ET.SubElement(proj, "dotSpacing").text = "1"
    comps = ET.SubElement(proj, "components")

    def pt(parent, x, y):
        p = ET.SubElement(parent, "point"); p.set("x", f"{x:.4f}"); p.set("y", f"{y:.4f}")

    # Turret board
    tb = ET.SubElement(comps, "org.diylc.components.boards.TurretBoard")
    ET.SubElement(tb, "name").text = "Board1"
    pts = ET.SubElement(tb, "controlPoints")
    pt(pts, 0.4, 0.4); pt(pts, 0.4 + BOARD_W, 0.4 + BOARD_H)
    ET.SubElement(tb, "boardWidth").text = f"{BOARD_W}"
    ET.SubElement(tb, "boardHeight").text = f"{BOARD_H}"

    # Turret lugs
    for tid, (tx, ty, net) in T.items():
        tl = ET.SubElement(comps, "org.diylc.components.connectivity.TurretLug")
        ET.SubElement(tl, "name").text = tid
        p = ET.SubElement(tl, "controlPoints"); pt(p, 0.4 + tx, 0.4 + (BOARD_H - ty))

    # Passive/active two-terminal components
    clsmap = {
        "R":  "org.diylc.components.passive.Resistor",
        "Cf": "org.diylc.components.passive.AxialFilmCapacitor",
        "Ce": "org.diylc.components.passive.RadialElectrolytic",
        "D":  "org.diylc.components.semiconductors.Diode",
        "IC": "org.diylc.components.semiconductors.TransistorTO92",
    }
    for c in C:
        if c["a"] not in T or c["b"] not in T:
            continue
        cls = clsmap.get(c["kind"], "org.diylc.components.passive.Resistor")
        el = ET.SubElement(comps, cls)
        ET.SubElement(el, "name").text = c["ref"]
        ET.SubElement(el, "value").text = c["value"]
        x1, y1, _ = T[c["a"]]; x2, y2, _ = T[c["b"]]
        p = ET.SubElement(el, "controlPoints")
        pt(p, 0.4 + x1, 0.4 + (BOARD_H - y1)); pt(p, 0.4 + x2, 0.4 + (BOARD_H - y2))

    # Tube sockets, pots, jacks, transformer (chassis area, offset below board)
    for c in CHASSIS:
        kind = c["kind"]; ox = c["x"]; oy = 0.4 + BOARD_H + 1.5 + (8.0 - 0.9 - c["y"]) * 0.0
        yy = 0.4 + BOARD_H + 1.2 + (3.5 - c["y"])
        if kind == "socket":
            el = ET.SubElement(comps, "org.diylc.components.tube.TubeSocket")
        elif kind == "pot":
            el = ET.SubElement(comps, "org.diylc.components.electromechanical.PotentiometerPanel")
        elif kind == "jack":
            el = ET.SubElement(comps, "org.diylc.components.electromechanical.OpenJack1__4")
        elif kind == "transformer":
            el = ET.SubElement(comps, "org.diylc.components.electromechanical.PowerTransformer")
        elif kind == "relay":
            el = ET.SubElement(comps, "org.diylc.components.semiconductors.DIL__IC")
        else:
            el = ET.SubElement(comps, "org.diylc.components.misc.Label")
        ET.SubElement(el, "name").text = c["ref"]
        ET.SubElement(el, "value").text = c["value"]
        p = ET.SubElement(el, "controlPoints"); pt(p, c["x"], yy)

    ET.SubElement(proj, "groups")
    ET.SubElement(proj, "lockedLayers")
    ET.SubElement(proj, "hiddenLayers")
    rough = ET.tostring(proj, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    with open("harmonic-tremolo.diy", "w") as f:
        f.write(pretty)

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
