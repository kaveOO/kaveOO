"""Turns the fonts into glyphs.json: one SVG path per printable ASCII character.

gen_memory.py draws text from these paths, because GitHub shows the SVG as an
image and an image cannot load web fonts. Only needed when changing fonts:

    pip install fonttools
    python .github/fonts/build_glyphs.py IBMPlexMono-Medium.ttf IBMPlexMono-Regular.ttf \
        HostGrotesk-Regular.ttf HostGrotesk-Medium.ttf

Host Grotesk ships as a variable font; make static weights with
    fonttools varLib.instancer "HostGrotesk[wght].ttf" wght=400 -o HostGrotesk-Regular.ttf
Both fonts are under the SIL Open Font License, see the OFL-*.txt files here.
"""
import json
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

NAMES = ["mono", "mono_light", "sans", "sans_medium"]
out = {}
for name, path in zip(NAMES, sys.argv[1:]):
    f = TTFont(path)
    upm = f["head"].unitsPerEm
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    glyphs = {}
    for code in range(0x20, 0x7f):
        g = cmap[code]
        pen = SVGPathPen(gs, ntos=lambda v: str(round(v)))
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))  # y down, baseline at 0
        glyphs[chr(code)] = [hmtx[g][0], pen.getCommands()]
    out[name] = {"upm": upm, "glyphs": glyphs}

dest = Path(__file__).with_name("glyphs.json")
dest.write_text(json.dumps(out, separators=(",", ":")))
print(f"wrote {dest} ({dest.stat().st_size // 1024} KB)")
