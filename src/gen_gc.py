"""Build the GameCube controller feature for one region from src/gc.c + src/gc_stub.s."""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
import asm
from layout import GC_BASE, GC_END
from ops import Feature, Hook
from sig import find_unique

# USA addresses (the other releases are found by signature search)
KPAD_EARLY = (0x8030FCF4, 8, 8)      # KPADRead: `lbz r0,0x17b(r21)`, "any samples queued?"
KPAD_LOCKED = (0x8030FD14, 8, 8)     # KPADRead: `lbz r18,0x17b(r21)`, right after OSDisableInterrupts
SI_SET_XY = (0x802B13E0, 0, 14)      # SISetXY: its `lis/addi` pair names the SDK's SI state struct
HOOKS = (('early', KPAD_EARLY, 0x8815017B, 'lbz 0,0x17b(21)', 0),     # lbz r0,0x17b(r21)
         ('locked', KPAD_LOCKED, 0x8A55017B, 'lbz 18,0x17b(21)', 1))   # lbz r18,0x17b(r21)
USA_DOL = None
EXTRA_DEFINES = {}                   # lab builds: {'DEBUG_COUNTERS': 0x80002FF0}


def _read(name):
    return open(os.path.join(HERE, name)).read()


def _word(dol, a):
    return struct.unpack('>I', dol.read(a, 4))[0]


def si_shadow(dol, set_xy):
    """Address of the SDK's copy of SIPOLL, from the `lis r5,hi; ...; addi r5,r5,lo; lwz r0,4(r5)` in SISetXY."""
    hi = lo = None
    for a in range(set_xy, set_xy + 0x30, 4):
        w = _word(dol, a)
        if (w >> 16) == 0x3CA0:                    # lis r5,X
            hi = w & 0xFFFF
        elif (w >> 16) == 0x38A5:                  # addi r5,r5,Y
            lo = w & 0xFFFF
            lo = lo - 0x10000 if lo & 0x8000 else lo
    if hi is None or lo is None:
        raise SystemExit('could not read the SI state address out of SISetXY')
    if _word(dol, set_xy + 0x2C) != 0x80050004:    # lwz r0,4(r5): the SIPOLL shadow is the struct's second word
        raise SystemExit('SISetXY does not look as expected')
    return ((hi << 16) + lo + 4) & 0xFFFFFFFF


def build(region, dol):
    usa = dol if region == 'RMKE01' else USA_DOL
    set_xy = SI_SET_XY[0] if region == 'RMKE01' else find_unique(usa, dol, *SI_SET_XY)
    shadow = si_shadow(dol, set_xy)
    ops, cur = [], GC_BASE
    for name, sig, orig, insn, mode in HOOKS:
        site = sig[0] if region == 'RMKE01' else find_unique(usa, dol, *sig)
        if _word(dol, site) != orig:
            raise SystemExit('%s: KPADRead site 0x%08X is 0x%08X' % (region, site, _word(dol, site)))
        blob = asm.words(asm.compile_hook(_read('gc.c'), _read('gc_stub.s').replace('@DISPLACED@', insn), cur,
                                          dict({'SHADOW': shadow, 'MODE': mode}, **EXTRA_DEFINES))) + [0]
        note = {'early': 'KPADRead, before the empty-ring bail-out: SI poller on; queue a pad sample if the remote sent none',
                'locked': 'KPADRead, interrupts off: rewrite the queued samples as Classic Controller samples'}[name]
        ops.append(Hook(site, orig, blob, cur, note=note))
        cur += (len(blob) * 4 + 15) & ~15
    if cur > GC_END:
        raise SystemExit('gc code overflows its window: 0x%X > 0x%X' % (cur, GC_END))
    return Feature('gc', 'GameCube controller', region, ops)
