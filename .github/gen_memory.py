"""Draws recent GitHub activity as a hex editor memory view.

The last 64 days, in order, 16 bytes per row. Each byte is that day's
contribution count (capped at 0xff), and the row label is the date of its
first byte. The ASCII column is what those bytes would spell, like in any
hex editor. Writes assets/memory-{dark,light}.svg.

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
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


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
    CW, RH = 34, 30                   # byte cell width, row height
    AX = 2                            # date column
    HX = AX + 92                      # first byte
    SX = HX + COLS * CW + 22          # ascii column
    CHW = 9.6                         # ascii char width at 16px
    TOP = 26                          # below the header line
    W = int(SX + COLS * CHW + AX)
    H = TOP + 34 + ROWS * RH + 4

    active = sorted(n for _, n in days if n)
    cuts = [active[int(p * (len(active) - 1))] for p in (.25, .5, .75)] if active else [0, 0, 0]
    shade = lambda n: (0, .14, .3, .5, .78)[0 if not n else 1 + sum(n > k for k in cuts)]

    e = []
    a = e.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="GitHub contributions for the last {len(days)} days as a hex dump, '
      f'one byte per day">')
    a(f'<style>text{{font-family:{MONO};font-size:16px;fill:{c["mute"]}}}'
      f'.b{{fill:{c["fg"]};text-anchor:middle}}.z{{fill:{c["zero"]};text-anchor:middle}}'
      f'.s{{font-size:14px}}.f{{fill:{c["fg"]}}}'
      f'.k{{animation:k 1.06s steps(1) infinite}}@keyframes k{{50%{{opacity:0}}}}'
      f'@media (prefers-reduced-motion:reduce){{.k{{animation:none}}}}</style>')
    a(f'<text x="{AX}" y="18" class="s f">Memory</text>')
    a(f'<text x="{AX + 76}" y="18" class="s">kaveo!activity</text>')
    a(f'<text x="{W - AX}" y="18" class="s" text-anchor="end">1 byte = contributions that day</text>')

    hy = TOP + 22
    for i in range(COLS):
        a(f'<text x="{HX + i*CW + CW/2}" y="{hy}" class="z">{i:02X}</text>')

    for r in range(ROWS):
        y = TOP + 34 + r * RH
        row = days[r * COLS:(r + 1) * COLS]
        if not row:
            break
        label = date.fromisoformat(row[0][0]).strftime("%b %d").lower()
        a(f'<text x="{AX}" y="{y + 20}">{label}</text>')
        asc = []
        for i, (d, n) in enumerate(row):
            x = HX + i * CW
            if n:
                a(f'<rect x="{x + 1}" y="{y + 3}" width="{CW - 2}" height="{RH - 6}" '
                  f'fill="rgb({c["heat"]})" fill-opacity="{shade(n)}"/>')
            a(f'<text x="{x + CW/2}" y="{y + 20}" class="{"b" if n else "z"}">{min(n, 255):02X}</text>')
            ch = chr(n) if 0x21 <= n < 0x7f else "."
            asc.append(ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        a(f'<text x="{SX}" y="{y + 20}" textLength="{len(row) * CHW:.1f}" '
          f'lengthAdjust="spacing">{"".join(asc)}</text>')
        if (r + 1) * COLS >= len(days):  # caret after today's byte
            x = HX + (len(row) - 1) * CW
            a(f'<rect class="k" x="{x + 6}" y="{y + RH - 4}" width="{CW - 12}" height="2" fill="{c["fg"]}"/>')
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
