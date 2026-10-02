#!/usr/bin/env python3
"""Disassemble a range of a main.dol with devkitPPC's objdump.

    python3 tools/disasm.py dumps/RMKE01.dol 0x8030CB00 0x8030CD00
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dol import Dol
from asm import DKP


def disasm(dol, start, end):
    data = dol.read(start, end - start)
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        f.write(data)
    try:
        out = subprocess.run([os.path.join(DKP, 'bin', 'powerpc-eabi-objdump'), '-D', '-EB', '-b', 'binary', '-m', 'powerpc:750',
                              '--adjust-vma=0x%X' % start, f.name], capture_output=True, text=True, check=True).stdout
    finally:
        os.unlink(f.name)
    return '\n'.join(l.replace('\t', ' ') for l in out.splitlines() if re.match(r'\s*[0-9a-f]+:\t', l))


if __name__ == '__main__':
    print(disasm(Dol(sys.argv[1]), int(sys.argv[2], 0), int(sys.argv[3], 0)))
