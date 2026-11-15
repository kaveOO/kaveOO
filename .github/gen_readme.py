"""Builds README.md: a debugger session attached to kaveo.exe.

The hex dump is generated from the bio text, so every byte is the real
encoding of the ASCII column. Edit the data below and run:  python3 .github/gen_readme.py

The .lastevent block is filled from the GitHub public events API. Set
GITHUB_TOKEN to avoid rate limits. If the API fails, the block already in
README.md is kept as it is.
"""
import json
import os
import urllib.request
from datetime import datetime
from html import escape

USER = "kaveOO"
SKIP_REPOS = {f"{USER}/{USER}"}  # the README's own updates are not news

BIO = ("Alban Billiette, 42 Warsaw. I reverse anti-cheats, write "
       "Windows kernel drivers and ship full-stack products.")
BIO_ADDR = 0x00403000

# name, size, url, note
MODULES = [
    ("rustorigin",      0x4e000, "https://kaveo.dev/work/rustorigin/",       "anti-cheat for my own Rust servers. 318 bans in 30 days"),
    ("assaultcubedma",  0x1c000, "https://github.com/kaveOO/AssaultCubeDMA", "reads game memory over a PCIe DMA card, not the OS"),
    ("kaveos",          0x12000, "https://github.com/kaveOO/kaveOS",         "x86 kernel from scratch in C and asm, no libc"),
    ("rustaveo",        0x61000, "https://kaveo.dev/work/rustaveo/",         "paid SaaS for Rust players, built and run alone"),
    ("arbor",           0x38000, "https://github.com/kaveOO/Arbor",          "booking engine, 1st on Track B at Codaro x Google"),
    ("panomoche",       0x23000, "https://github.com/kaveOO/panomoche",      "sorts street pictures for Panoramax with ML"),
]

# most recent frame first, like a real stack
FRAMES = [
    ("codaro_google_hackathon", 0x1f2, "1st place, booking track   2026"),
    ("warsaw_hacks",            0x0a4, "most innovative idea       2026"),
    ("common_core_le_havre",    0x3c0, "42 Common Core done        2026"),
    ("main",                    0x02c, "first line of code     oct 2024"),
]

LINKS = [
    ("site",     "https://kaveo.dev",                         "kaveo.dev"),
    ("cv",       "https://kaveo.dev/Alban-Billiette-CV.pdf",  "kaveo.dev/cv.pdf"),
    ("mail",     "mailto:contact@kaveo.dev",                  "contact@kaveo.dev"),
    ("linkedin", "https://www.linkedin.com/in/kaveooo/",      "linkedin.com/in/kaveooo"),
    ("youtube",  "https://www.youtube.com/@Kaveo_o",          "youtube.com/@Kaveo_o"),
    ("discord",  None,                                        ".kaveo"),
]



def gh(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "gen-readme"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def link(url, text):
    return f'<a href="{url}">{escape(text)}</a>'


def clip(text, n):
    text = text.splitlines()[0].strip() if text else ""
    return text if len(text) <= n else text[:n - 3].rstrip() + "..."


def describe(ev):
    """One-line summary of a public event, or None if it is not worth showing."""
    repo, pl = ev["repo"]["name"], ev.get("payload", {})
    r = link(f"https://github.com/{repo}", repo)
    t = ev["type"]
    if t == "PushEvent":
        sha = pl.get("head")
        try:
            msg = clip(gh(f"repos/{repo}/commits/{sha}")["commit"]["message"], 34)
        except Exception:
            msg = ""
        head = link(f"https://github.com/{repo}/commit/{sha}", sha[:7]) if sha else "push"
        return f"push {head} to {r}" + (f' "{escape(msg)}"' if msg else "")
    if t == "ReleaseEvent" and pl.get("action") == "published":
        rel = pl["release"]
        return f"release {link(rel['html_url'], rel['tag_name'])} of {r}"
    if t == "CreateEvent":
        if pl.get("ref_type") == "repository":
            return f"created {r}"
        if pl.get("ref_type") == "tag":
            return f"tag {escape(pl['ref'])} in {r}"
    if t == "PublicEvent":
        return f"open-sourced {r}"
    if t == "PullRequestEvent" and pl.get("action") in ("opened", "closed"):
        n = pl.get("number")
        what = "merged" if pl.get("pull_request", {}).get("merged") else pl["action"]
        return f"{what} {link(f'https://github.com/{repo}/pull/{n}', f'#{n}')} in {r}"
    return None


def last_event():
    events = gh(f"users/{USER}/events/public?per_page=50")
    events.sort(key=lambda e: e["created_at"], reverse=True)
    for ev in events:
        if ev["repo"]["name"] in SKIP_REPOS:
            continue
        line = describe(ev)
        if line:
            when = datetime.strptime(ev["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            return [f"Last event: {line}",
                    f"  debugger time: {when:%a %b %d %H:%M:%S.000 %Y} (UTC + 0:00)"]
    return None


def previous_last_event():
    """The .lastevent lines already in README.md, kept when the API is down."""
    try:
        lines = open("README.md").read().split("\n")
        i = next(i for i, l in enumerate(lines) if "<b>.lastevent</b>" in l)
        return lines[i + 1:i + 3]
    except (OSError, StopIteration):
        return None


P = "0:000&gt; "
out = []
w = out.append

# db: bio as bytes, NUL terminated, int3 padding to the end of the line
data = BIO.encode("ascii") + b"\x00"
data += b"\xcc" * (-len(data) % 16)
w(f"{P}<b>db kaveo!bio</b>")
for off in range(0, len(data), 16):
    row = data[off:off + 16]
    hx = " ".join(f"{b:02x}" for b in row)
    hx = hx[:23] + "-" + hx[24:]  # WinDbg's mid-row dash
    asc = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
    w(f"{BIO_ADDR + off:08x}  {hx}  {escape(asc)}")
w("")

# .lastevent: latest public activity on GitHub
try:
    ev = last_event()
except Exception as e:
    print(f"events API failed ({e}), keeping the previous .lastevent")
    ev = None
ev = ev or previous_last_event()
if ev:
    w(f"{P}<b>.lastevent</b>")
    out.extend(ev)
    w("")

# lm: projects as loaded modules
w(f"{P}<b>lm</b>")
w("start    end        module name")
base = 0x10000000
for name, size, url, note in MODULES:
    pad = " " * (17 - len(name))
    w(f"{base:08x} {base + size:08x}   <a href=\"{url}\">{name}</a>{pad}{escape(note)}")
    base += (size + 0xfffff) & ~0xfffff  # next 1 MiB boundary
w("")

# k: history as a call stack
w(f"{P}<b>k</b>")
w(" # ChildEBP RetAddr")
ebp, ret = 0x0019fe60, 0x00401000
for i, (fn, disp, note) in enumerate(FRAMES):
    sym = f"kaveo!{fn}+0x{disp:x}"
    w(f"{i:02x} {ebp:08x} {ret + disp * 7:08x} {sym:<38}{escape(note)}")
    ebp += 0x5c
w(f"{len(FRAMES):02x} {ebp:08x} 00000000 ntdll!RtlUserThreadStart+0x2f")
w("")

# du: contact strings
w(f"{P}<b>du kaveo!contact</b>")
addr = 0x00405000
for k, url, label in LINKS:
    s = f"<a href=\"{url}\">{label}</a>" if url else label
    w(f"{addr:08x}  {k:<9}\"{s}\"")
    addr += 0x40
w("")
w(f"{P}<b>qd</b>")

readme = "<pre>\n" + "\n".join(out) + "\n</pre>\n"
open("README.md", "w").write(readme)
print(readme)
