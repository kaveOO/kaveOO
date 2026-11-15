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

# name, url, note
MODULES = [
    ("rustorigin", "https://kaveo.dev/work/rustorigin/",       "anti-cheat for my own Rust servers. 318 bans in 30 days"),
    ("assaultcubedma", "https://github.com/kaveOO/AssaultCubeDMA", "reads game memory over a PCIe DMA card, not the OS"),
    ("kaveos", "https://github.com/kaveOO/kaveOS",         "x86 kernel from scratch in C and asm, no libc"),
    ("rustaveo", "https://kaveo.dev/work/rustaveo/",         "paid SaaS for Rust players, built and run alone"),
    ("arbor", "https://github.com/kaveOO/Arbor",          "booking engine, 1st on Track B at Codaro x Google"),
]

LINKS = [
    ("site",     "https://kaveo.dev",                         "kaveo.dev"),
    ("cv",       "https://kaveo.dev/Alban-Billiette-CV.pdf",  "kaveo.dev/cv.pdf"),
    ("mail",     "mailto:contact@kaveo.dev",                  "contact@kaveo.dev"),
    ("linkedin", "https://www.linkedin.com/in/kaveooo/",      "linkedin.com/in/kaveooo"),
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
        i = next(i for i, l in enumerate(lines) if ".lastevent" in l)
        return lines[i + 1:i + 3]
    except (OSError, StopIteration):
        return None


INTRO = ("I'm Alban, a developer at 42 Warsaw. I take apart anti-cheats, write Windows "
         "kernel drivers and build full-stack products. Open to full-time roles.")

P = "0:000&gt; "
out = []
w = out.append

# .lastevent: latest public activity on GitHub
try:
    ev = last_event()
except Exception as e:
    print(f"events API failed ({e}), keeping the previous .lastevent")
    ev = None
ev = ev or previous_last_event()
if ev:
    w(f"{P}<b>* last activity</b>")
    w(f"{P}.lastevent")
    out.extend(ev)
    w("")

# lm: projects as loaded modules
w(f"{P}<b>* projects</b>")
w(f"{P}lm")
w("start    end        module name")
base = 0x10000000
SIZES = [0x4e000, 0x1c000, 0x12000, 0x61000, 0x38000, 0x23000, 0x2a000, 0x19000]
for (name, url, note), size in zip(MODULES, SIZES):
    pad = " " * (17 - len(name))
    w(f"{base:08x} {base + size:08x}   <a href=\"{url}\">{name}</a>{pad}{escape(note)}")
    base += (size + 0xfffff) & ~0xfffff  # next 1 MiB boundary
w("")

# du: contact strings
w(f"{P}<b>* contact</b>")
w(f"{P}du kaveo!contact")
addr = 0x00405000
for k, url, label in LINKS:
    s = f"<a href=\"{url}\">{label}</a>" if url else label
    w(f"{addr:08x}  {k:<9}\"{s}\"")
    addr += 0x40

readme = (INTRO + "\n\n") + "<pre>\n" + "\n".join(out) + "\n</pre>\n"
# memory window drawn by gen_memory.py, docked under the session
# ?v=<content hash> so GitHub's image cache picks up every new version
def v(path):
    import hashlib
    try:
        return hashlib.sha1(open(path, "rb").read()).hexdigest()[:8]
    except OSError:
        return "0"

dark, light = "assets/memory-dark.svg", "assets/memory-light.svg"
readme += f"""
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{dark}?v={v(dark)}">
  <source media="(prefers-color-scheme: light)" srcset="{light}?v={v(light)}">
  <img src="{dark}?v={v(dark)}" width="100%" alt="GitHub contributions for the last 64 days as a hex dump, one byte per day">
</picture>
"""
open("README.md", "w").write(readme)
print(readme)
