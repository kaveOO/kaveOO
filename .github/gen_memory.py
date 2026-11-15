"""Draws recent GitHub activity as a hex editor memory view.

The last 64 days, in order, 16 bytes per row. Each byte is that day's
contribution count (capped at 0xff), and the row label is the date of its
first byte. The ASCII column is what those bytes would spell, like in any
hex editor. Writes assets/memory-{dark,light}.svg.

Text is IBM Plex Mono (bytes) and Host Grotesk (labels), the fonts of
kaveo.dev. GitHub shows the SVG as an image, which cannot load web fonts, so
every character is drawn from the outlines in fonts/glyphs.json.

Needs GITHUB_TOKEN (GraphQL requires auth). If the query fails, the SVGs
already in assets/ are left alone.
"""
import json
import os
import sys
import urllib.request
from datetime import date

USER = "kaveOO"
OUT = "assets"
ROWS, COLS = 4, 16

QUERY = """{user(login:"%s"){contributionsCollection{contributionCalendar{
  weeks{contributionDays{date contributionCount}}}}}}""" % USER

THEMES = {
    "dark":  dict(fg="#e6edf3",
                  mute="#7d8590", zero="#484f58", heat="163,113,247"),
    "light": dict(fg="#1f2328",
                  mute="#656d76", zero="#afb8c1", heat="130,80,223"),
}
FONTS = json.load(open(os.path.join(os.path.dirname(__file__), "fonts", "glyphs.json")))


class Text:
    """Draws strings from glyph outlines, each glyph defined once and reused."""

    def __init__(self):
        self.used = {}

    def width(self, s, font, size):
        f = FONTS[font]
        return sum(f["glyphs"][ch][0] for ch in s) * size / f["upm"]

    def __call__(self, s, font, size, x, y, fill, anchor="start", cls=""):
        f = FONTS[font]
        if anchor == "end":
            x -= self.width(s, font, size)
        elif anchor == "middle":
            x -= self.width(s, font, size) / 2
        k = size / f["upm"]
        uses, pen = [], 0
        for ch in s:
            adv, d = f["glyphs"][ch]
            if d:
                gid = f"{font[0]}{font[-1]}{ord(ch):x}"
                self.used[gid] = d
                # each glyph starts on a whole pixel: outlines have no hinting,
                # so this is what keeps small text sharp on 1x screens
                gx = round(x + pen * k)
                uses.append(f'<use href="#{gid}" transform="translate({gx} {round(y)}) scale({k:.5f})"/>')
            pen += adv
        c = f' class="{cls}"' if cls else ""
        return f'<g{c} fill="{fill}">' + "".join(uses) + "</g>"

    def defs(self):
        return "<defs>" + "".join(f'<path id="{g}" d="{d}"/>' for g, d in self.used.items()) + "</defs>"


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "User-Agent": "gen-memory"})
    with urllib.request.urlopen(req, timeout=20) as r:
        weeks = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return days[-ROWS * COLS:]


def svg(theme, days):
    c = THEMES[theme]
    # exactly GitHub's README column on desktop (846px from 1280px windows up),
    # so it fills the width and is shown 1:1 instead of resampled; every edge
    # and baseline sits on a whole pixel
    W = 846
    CW, RH = 36, 30                   # byte cell width, row height
    AX = 0                            # date column
    HX = AX + 84                      # first byte
    CHW = 9.6                         # Plex Mono advance (600/1000) at 16px
    SX = W - COLS * CHW - 1           # ascii column, flush right
    TOP = 28                          # below the header line
    H = TOP + 34 + ROWS * RH + 4

    active = sorted(n for _, n in days if n)
    cuts = [active[int(p * (len(active) - 1))] for p in (.25, .5, .75)] if active else [0, 0, 0]
    shade = lambda n: (0, .14, .3, .5, .78)[0 if not n else 1 + sum(n > k for k in cuts)]

    T = Text()
    e = []
    a = e.append
    a(T("Memory", "sans_medium", 17, AX, 19, c["fg"]))
    a(T("kaveo!activity", "mono", 16, AX + 80, 19, c["mute"]))
    a(T("1 byte = contributions that day", "sans", 16, W - AX, 19, c["mute"], "end"))

    hy = TOP + 22
    for i in range(COLS):
        a(T(f"{i:02X}", "mono", 15, HX + i * CW + CW / 2, hy, c["zero"], "middle"))

    for r in range(ROWS):
        y = TOP + 34 + r * RH
        row = days[r * COLS:(r + 1) * COLS]
        if not row:
            break
        label = date.fromisoformat(row[0][0]).strftime("%b %d").lower()
        a(T(label, "sans", 16, AX, y + 20, c["mute"]))
        asc = ""
        for i, (d, n) in enumerate(row):
            x = HX + i * CW
            if n:
                a(f'<rect x="{x + 1}" y="{y + 3}" width="{CW - 2}" height="{RH - 6}" '
                  f'fill="rgb({c["heat"]})" fill-opacity="{shade(n)}"/>')
            a(T(f"{min(n, 255):02X}", "mono", 16, x + CW / 2, y + 20,
                c["fg"] if n else c["zero"], "middle"))
            asc += chr(n) if 0x21 <= n < 0x7f else "."
        a(T(asc, "mono_light", 16, SX, y + 20, c["mute"]))
        if (r + 1) * COLS >= len(days):  # caret under today's byte
            x = HX + (len(row) - 1) * CW
            a(f'<rect class="k" x="{x + 7}" y="{y + RH - 4}" width="{CW - 14}" height="2" fill="{c["fg"]}"/>')
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="GitHub contributions for the last {len(days)} days as a hex dump, '
            f'one byte per day"><title>GitHub contributions, last {len(days)} days</title>'
            f'<style>.k{{animation:k 1.06s steps(1) infinite}}@keyframes k{{50%{{opacity:0}}}}'
            f'@media (prefers-reduced-motion:reduce){{.k{{animation:none}}}}</style>' + T.defs())
    e.insert(0, head)
    a('</svg>\n')
    return "".join(e)


def main():
    try:
        days = fetch()
    except Exception as e:
        print(f"GraphQL failed ({e}), keeping the previous memory view")
        return 0
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        with open(f"{OUT}/memory-{th}.svg", "w") as f:
            f.write(svg(th, days))
    print(f"{len(days)} days, {days[0][0]} to {days[-1][0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
