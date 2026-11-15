"""Builds README.md: a debugger session attached to kaveo.exe.

The hex dump is generated from the bio text, so every byte is the real
encoding of the ASCII column. Edit the data below and run:  python3 .github/gen_readme.py
"""
from html import escape

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
