#!/usr/bin/env python3
"""
Reverse tool: regenerate the turret DRILL drawing + coordinate table FROM a
(hand-edited) DIYLC .diy file.

Workflow:
  - generate.py is the master for the FIRST draft (it writes the .diy + drill
    files + BOM from the component dataset).
  - Once you open harmonic-tremolo.diy in DIYLC and DRAG turrets around, the .diy
    becomes the master for turret POSITIONS. Run this tool to refresh
    turret-drill.csv / turret-drill.svg so the drill pattern matches the board you
    actually laid out:

        python3 diy_to_drill.py [harmonic-tremolo.diy]

  - BOM values (bom.csv) still come from generate.py; positions do not affect them.

It reads Turret lugs (hole positions) and DrillHole components (mounting holes)
straight out of the .diy, un-flips DIYLC's top-down Y back to a bottom-left
origin, and writes the same CSV + SVG format generate.py produces.
"""
import xml.etree.ElementTree as ET
import csv
import os
import sys

DIY = sys.argv[1] if len(sys.argv) > 1 else "harmonic-tremolo.diy"
DEFAULT_HOLE = 0.094


def _num(s):
    return float(s)


def load(diy_path):
    root = ET.parse(diy_path).getroot()
    board = root.find(".//org.diylc.components.boards.BlankBoard")
    if board is None:
        raise SystemExit("No BlankBoard found in %s" % diy_path)
    fp, sp = board.find("firstPoint"), board.find("secondPoint")
    x0, y0 = _num(fp.get("x")), _num(fp.get("y"))
    BW = _num(sp.get("x")) - x0
    BH = _num(sp.get("y")) - y0

    turrets = []
    for t in root.findall(".//org.diylc.components.connectivity.Turret"):
        name = (t.findtext("name") or "?").strip()
        pt = t.find("point")
        x = _num(pt.get("x")) - x0
        y = BH - (_num(pt.get("y")) - y0)          # un-flip Y (DIYLC is top-down)
        hs = t.findtext("holeSize/value")
        d = float(hs) if hs else DEFAULT_HOLE
        val = (t.findtext("value") or "").strip()
        net = val.split(None, 1)[1] if " " in val else val   # "T7 SPLIT" -> "SPLIT"
        turrets.append((name, x, y, d, net))

    mounts = []
    for m in root.findall(".//org.diylc.components.electromechanical.DrillHole"):
        name = (m.findtext("name") or "MH").strip()
        pt = m.find("point")
        x = _num(pt.get("x")) - x0
        y = BH - (_num(pt.get("y")) - y0)
        d = float(m.findtext("diameter/value") or 0.15)
        mounts.append((name, x, y, d))

    def tkey(n):
        try:
            return int(n[1:])
        except ValueError:
            return 9999
    turrets.sort(key=lambda r: tkey(r[0]))
    return turrets, mounts, BW, BH


def write_csv(turrets, mounts, BW, BH, src):
    with open("turret-drill.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# Hoffman custom turret board - drill coordinate table"])
        w.writerow(["# Extracted from %s (DIYLC is master for positions)" % src])
        w.writerow(["# Origin = lower-left corner. Units = inches.", "", "", "", ""])
        w.writerow(["# Board size = %.3f W x %.3f H" % (BW, BH), "", "", "", ""])
        w.writerow(["Hole ID", "X (in)", "Y (in)", "Dia (in)", "Net / Purpose"])
        for n, x, y, d, net in turrets:
            w.writerow([n, "%.3f" % x, "%.3f" % y, "%.3f" % d, net])
        for n, x, y, d in mounts:
            w.writerow([n, "%.3f" % x, "%.3f" % y, "%.3f" % d, "board mounting hole"])


def write_svg(turrets, mounts, BW, BH):
    scale, pad = 96.0, 0.6
    W = (BW + 2 * pad) * scale
    Hh = (BH + 2 * pad) * scale

    def X(x): return (x + pad) * scale
    def Y(y): return (BH - y + pad) * scale

    e = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{Hh:.0f}" '
         f'viewBox="0 0 {W:.0f} {Hh:.0f}">', '<rect width="100%" height="100%" fill="white"/>']
    e.append(f'<rect x="{X(0):.1f}" y="{Y(BH):.1f}" width="{BW*scale:.1f}" '
             f'height="{BH*scale:.1f}" fill="none" stroke="#333" stroke-width="1.5"/>')
    for n, x, y, d in mounts:
        r = d / 2 * scale
        e.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r:.1f}" fill="none" stroke="#c00" stroke-width="1.2"/>')
        e.append(f'<text x="{X(x):.1f}" y="{Y(y)-r-2:.1f}" font-family="monospace" font-size="8" '
                 f'text-anchor="middle" fill="#c00">{n}</text>')
    for n, x, y, d, net in turrets:
        r = d / 2 * scale
        e.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r:.1f}" fill="none" stroke="#06c" stroke-width="1.3"/>')
        e.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="1.1" fill="#06c"/>')
        e.append(f'<text x="{X(x)+r+1:.1f}" y="{Y(y)-2:.1f}" font-family="monospace" font-size="7" fill="#06c">{n}</text>')
    e.append(f'<text x="{X(BW/2):.1f}" y="{Y(BH)+11:.1f}" font-family="sans-serif" font-size="10" '
             f'text-anchor="middle" fill="#333">{BW:.3f}" (W)</text>')
    e.append(f'<text x="{X(0):.1f}" y="{Hh-6:.1f}" font-family="sans-serif" font-size="8" fill="#888">'
             f'Turret (blue) - Mount holes (red) - extracted from .diy - print at 1:1 (96dpi)</text>')
    e.append('</svg>')
    with open("turret-drill.svg", "w") as f:
        f.write("\n".join(e))


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    turrets, mounts, BW, BH = load(DIY)
    write_csv(turrets, mounts, BW, BH, os.path.basename(DIY))
    write_svg(turrets, mounts, BW, BH)
    print("Refreshed turret-drill.csv + turret-drill.svg from %s" % os.path.basename(DIY))
    print("  %d turrets + %d mounting holes, board %.3f x %.3f in" % (len(turrets), len(mounts), BW, BH))
