"""Build the Classic Controller feature: Vague Rant's Gecko codes, as ops.

The codes in src/cc/<ID>.txt are his (see README credits); this only parses
them into Patch/Hook ops so the same data can become a patched DOL, a Gecko
list or a Riivolution patch.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from layout import CC_BASE, CC_END
from ops import Feature, Hook, Patch


def parse(text):
    lines = [l.split()[:2] for l in text.splitlines() if l.strip() and not l.lstrip().startswith(('*', '$', '#'))
             and len(l.split()[0]) == 8 and all(c in '0123456789ABCDEFabcdef' for c in l.split()[0])]
    i, out = 0, []
    while i < len(lines):
        a, b = lines[i]
        kind, addr = int(a[:2], 16), 0x80000000 | (int(a[2:], 16) & 0x01FFFFFF)
        if kind == 0x04:
            out.append(('04', addr, [int(b, 16)]))
            i += 1
        elif kind == 0x06:
            n = int(b, 16)
            nl = (n + 7) // 8
            raw = b''.join(bytes.fromhex(x) for ln in lines[i + 1:i + 1 + nl] for x in ln)
            out.append(('06', addr, raw[:n]))
            i += 1 + nl
        elif kind == 0xC2:
            n = int(b, 16)
            ws = [int(x, 16) for ln in lines[i + 1:i + 1 + n] for x in ln]
            out.append(('C2', addr, ws))
            i += 1 + n
        else:
            raise ValueError('unsupported code line: %s %s' % (a, b))
    return out


HOOK_NOTES = ['controller check: accept a Classic Controller (extension 2) where a Nunchuk is expected',
              'controller check: count the Classic Controller as a Nunchuk',
              'calc_dpd_variable: right stick -> IR pointer (HOME Menu cursor)',
              'read_kpad_ext: left stick -> Nunchuk stick fields',
              'read_kpad_button: Classic Controller buttons -> Wii Remote bits']
PATCH_NOTES = {0x28040003: 'controller check: allow extension types up to 3',
               0x28050003: 'controller check: allow extension types up to 3',
               0x7FC3F378: 'read_kpad_ext: keep the channel in r3 across the stick call'}


def build(region, dol):
    text = open(os.path.join(HERE, 'cc', region + '.txt')).read()
    ops, cur = [], CC_BASE
    notes = list(HOOK_NOTES)
    for kind, addr, body in parse(text):
        if kind == '04':
            new = struct.pack('>I', body[0])
            ops.append(Patch(addr, new, dol.read(addr, 4), note=PATCH_NOTES.get(body[0], '')))
        elif kind == '06':
            ops.append(Patch(addr, body, dol.read(addr, len(body)), note=''))
        else:
            orig = struct.unpack('>I', dol.read(addr, 4))[0]
            assert body[-1] == 0
            ops.append(Hook(addr, orig, body, cur, note=notes.pop(0)))
            cur += (len(body) * 4 + 15) & ~15
    if cur > CC_END:
        raise SystemExit('cc code overflows its window: 0x%X > 0x%X' % (cur, CC_END))
    return Feature('cc', 'Classic Controller', region, ops)
