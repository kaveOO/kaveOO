<pre>
0:000&gt; <b>db kaveo!bio</b>
00403000  41 6c 62 61 6e 20 42 69-6c 6c 69 65 74 74 65 2e  Alban Billiette.
00403010  20 53 79 73 74 65 6d 73-20 70 72 6f 67 72 61 6d   Systems program
00403020  6d 65 72 20 66 72 6f 6d-20 46 72 61 6e 63 65 2c  mer from France,
00403030  20 6c 69 76 69 6e 67 20-69 6e 20 57 61 72 73 61   living in Warsa
00403040  77 2c 20 73 74 75 64 79-69 6e 67 20 61 74 20 34  w, studying at 4
00403050  32 2e 20 49 20 72 65 76-65 72 73 65 2d 65 6e 67  2. I reverse-eng
00403060  69 6e 65 65 72 20 61 6e-74 69 2d 63 68 65 61 74  ineer anti-cheat
00403070  73 2c 20 77 72 69 74 65-20 57 69 6e 64 6f 77 73  s, write Windows
00403080  20 6b 65 72 6e 65 6c 20-64 72 69 76 65 72 73 20   kernel drivers 
00403090  61 6e 64 20 62 75 69 6c-64 20 66 75 6c 6c 2d 73  and build full-s
004030a0  74 61 63 6b 20 70 72 6f-64 75 63 74 73 2e 00 cc  tack products...

0:000&gt; <b>lm</b>
start    end        module name
10000000 1004e000   <a href="https://kaveo.dev/work/rustorigin/">rustorigin</a>       anti-cheat for my own Rust servers. 318 bans in 30 days
10100000 1011c000   <a href="https://github.com/kaveOO/AssaultCubeDMA">assaultcubedma</a>   reads game memory over a PCIe DMA card, not the OS
10200000 10212000   <a href="https://github.com/kaveOO/kaveOS">kaveos</a>           x86 kernel from scratch. GDT, IDT, keyboard, shell
10300000 10361000   <a href="https://kaveo.dev/work/rustaveo/">rustaveo</a>         paid SaaS for Rust players, built and run alone
10400000 10438000   <a href="https://github.com/kaveOO/Arbor">arbor</a>            booking engine that pivots on one JSON file
10500000 1050f000   <a href="https://github.com/kaveOO/42WarsawHacks">warsawhacks</a>      42 campus dashboard, written solo in 30 hours
10600000 10623000   <a href="https://github.com/kaveOO/panomoche">panomoche</a>        sorts street pictures for Panoramax, says why
10700000 10703000   <a href="https://github.com/kaveOO/ReadWriteKernel">readwritekernel</a>  my first driver. RPM/WPM from ring 0
10800000 10802000   <a href="https://github.com/kaveOO/ThreadHijacking">threadhijacking</a>  shellcode run on another process&#x27;s main thread

0:000&gt; <b>dt kaveo!_STACK @esi</b>
   +0x000 kernel    : "C, C++, x86-64 asm, WDK, QEMU"
   +0x004 reversing : "IDA, x64dbg, Cheat Engine, MemProcFS"
   +0x008 security  : "anti-cheat internals, BattlEye, EAC, DMA"
   +0x00c web       : "TypeScript, React, Fastify, FastAPI, Go, Postgres"

0:000&gt; <b>k</b>
 # ChildEBP RetAddr
00 0019fe60 00401d9e kaveo!codaro_google_hackathon+0x1f2   1st place, booking track   2026
01 0019febc 0040147c kaveo!warsaw_hacks+0xa4               most innovative idea       2026
02 0019ff18 00402a40 kaveo!common_core_le_havre+0x3c0      42 Common Core done        2026
03 0019ff74 004017bd kaveo!first_kernel_driver+0x11b       ring 0 for the first time  2025
04 0019ffd0 00401134 kaveo!main+0x2c                       first line of code     oct 2024
05 001a002c 00000000 ntdll!RtlUserThreadStart+0x2f

0:000&gt; <b>du kaveo!contact</b>
00405000  site     "<a href="https://kaveo.dev">kaveo.dev</a>"
00405040  notes    "<a href="https://kaveo.dev/notes/">kaveo.dev/notes</a>"
00405080  cv       "<a href="https://kaveo.dev/Alban-Billiette-CV.pdf">kaveo.dev/cv.pdf</a>"
004050c0  mail     "<a href="mailto:contact@kaveo.dev">contact@kaveo.dev</a>"
00405100  linkedin "<a href="https://www.linkedin.com/in/kaveooo/">linkedin.com/in/kaveooo</a>"
00405140  youtube  "<a href="https://www.youtube.com/@Kaveo_o">youtube.com/@Kaveo_o</a>"
00405180  discord  ".kaveo"

0:000&gt; <b>qd</b>
quit:
Detached. kaveo.exe is still running.
</pre>
