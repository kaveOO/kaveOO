"""Draws the contribution calendar as a WinDbg memory window.

Each byte is one day's contribution count (capped at 0xff), one row per
weekday, one column per week, shaded by value like a hex editor. The caret
sits on today. Writes assets/memory-{dark,light}.svg.

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

QUERY = """{user(login:"%s"){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}""" % USER

THEMES = {
    "dark":  dict(bg="#0d1117", panel="#161b22", line="#30363d", fg="#e6edf3",
                  mute="#7d8590", zero="#3b424b", heat="110,149,255", caret="#e6edf3"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", line="#d0d7de", fg="#1f2328",
                  mute="#656d76", zero="#c3cad2", heat="61,107,255", caret="#1f2328"),
}
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SP = "\u00a0" * 4  # SVG collapses normal spaces
DAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "User-Agent": "gen-memory"})
    with urllib.request.urlopen(req, timeout=20) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def level(n, cuts):
    """0 for no contributions, else 1..4 by quartile of the active days."""
    if n == 0:
        return 0
    return 1 + sum(n > c for c in cuts)


def svg(theme, total, weeks):
    c = THEMES[theme]
    CW, CH = 21, 20             # cell size
    LX, TY = 64, 78             # grid origin
    W = LX + len(weeks) * CW + 24
    H = TY + 7 * CH + 46

    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"]
                    if d["contributionCount"])
    q = lambda p: counts[int(p * (len(counts) - 1))] if counts else 0
    cuts = (q(.25), q(.5), q(.75))
    alpha = {1: .16, 2: .32, 3: .52, 4: .78}

    first = weeks[0]["contributionDays"][0]["date"]
    last = weeks[-1]["contributionDays"][-1]["date"]
    fmt = lambda s: date.fromisoformat(s).strftime("%b %d %Y")
    active = len(counts)

    e = []
    a = e.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'xml:space="preserve" role="img" aria-label="Contribution calendar shown as a memory dump: {total} contributions '
      f'from {fmt(first)} to {fmt(last)}">')
    a(f'<title>{total} contributions, {fmt(first)} to {fmt(last)}</title>')
    a(f'<style>text{{font-family:{MONO};font-size:11px;fill:{c["mute"]}}}'
      f'.v{{fill:{c["fg"]};text-anchor:middle}}.z{{fill:{c["zero"]};text-anchor:middle}}'
      f'.h{{fill:{c["fg"]}}}.t{{font-size:13px}}.c{{animation:b 1.1s steps(1) infinite}}'
      f'@keyframes b{{50%{{opacity:0}}}}'
      f'@media (prefers-reduced-motion:reduce){{.c{{animation:none}}}}</style>')
    a(f'<rect width="{W}" height="{H}" rx="6" fill="{c["bg"]}"/>')
    a(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="5.5" fill="none" stroke="{c["line"]}"/>')
    # title bar, like a docked WinDbg memory window
    a(f'<rect x="1" y="1" width="{W-2}" height="34" rx="5" fill="{c["panel"]}"/>')
    a(f'<rect x="1" y="34" width="{W-2}" height="1" fill="{c["line"]}"/>')
    a(f'<text x="16" y="23" class="h t">Memory</text>')
    a(f'<text x="84" y="23" class="t">Address: kaveo!contributions{SP}Display format: Byte{SP}'
      f'Columns: {len(weeks)}</text>')
    a(f'<text x="{W-16}" y="23" class="t" text-anchor="end">{fmt(first)} .. {fmt(last)}</text>')

    # month labels over the first week that starts in that month
    prev = None
    for i, w in enumerate(weeks):
        m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b").lower()
        if m != prev and i < len(weeks) - 1:
            a(f'<text x="{LX + i*CW + 2}" y="{TY - 12}">{m}</text>')
        prev = m

    for d in range(7):
        a(f'<text x="16" y="{TY + d*CH + 14}">+{d} {DAYS[d]}</text>')

    for i, w in enumerate(weeks):
        for day in w["contributionDays"]:
            n, d = day["contributionCount"], day["weekday"]
            x, y = LX + i * CW, TY + d * CH
            lv = level(n, cuts)
            if lv:
                a(f'<rect x="{x+1}" y="{y+1}" width="{CW-2}" height="{CH-2}" rx="2" '
                  f'fill="rgb({c["heat"]})" fill-opacity="{alpha[lv]}"/>')
            cls = "v" if n else "z"
            a(f'<text x="{x + CW/2}" y="{y + 14}" class="{cls}">{min(n, 255):02x}</text>')
            if day["date"] == last:  # caret on today
                a(f'<rect class="c" x="{x+1}" y="{y + CH - 3}" width="{CW-2}" height="2" fill="{c["caret"]}"/>')

    fy = TY + 7 * CH + 28
    a(f'<text x="16" y="{fy}" class="t">1 byte = 1 day{SP}{total:,} contributions{SP}'
      f'{active} active days{SP}max 0x{counts[-1] if counts else 0:02x}</text>')
    # legend
    lx = W - 24 - 5 * 26 - 30
    a(f'<text x="{lx - 8}" y="{fy}" text-anchor="end">00</text>')
    for k in range(5):
        x = lx + k * 26
        if k:
            a(f'<rect x="{x}" y="{fy - 12}" width="20" height="16" rx="2" fill="rgb({c["heat"]})" '
              f'fill-opacity="{alpha[k]}"/>')
        else:
            a(f'<rect x="{x+.5}" y="{fy - 11.5}" width="19" height="15" rx="2" fill="none" stroke="{c["line"]}"/>')
    a(f'<text x="{lx + 5*26 + 2}" y="{fy}">ff</text>')
    a('</svg>\n')
    return "".join(e)


def main():
    try:
        total, weeks = fetch()
    except Exception as e:
        print(f"GraphQL failed ({e}), keeping the previous memory window")
        return 0
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        with open(f"{OUT}/memory-{th}.svg", "w") as f:
            f.write(svg(th, total, weeks))
    print(f"{total} contributions over {len(weeks)} weeks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
