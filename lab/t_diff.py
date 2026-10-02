"""Which KPAD struct bytes change when the left / right stick moves (Classic Controller)."""
import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
def snap(d): return d.peek(d.kpad_base(0), 0x688)
def diff(a, b):
    out = []
    for o in range(0, 0x688, 4):
        if a[o:o+4] != b[o:o+4] and not (0x180 <= o < 0x5a0):
            fa, fb = struct.unpack('>f', a[o:o+4])[0], struct.unpack('>f', b[o:o+4])[0]
            out.append('+%03X %s -> %s (%.3f -> %.3f)' % (o, a[o:o+4].hex(), b[o:o+4].hex(), fa, fb))
    return out
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), wiimote='classic', region=region) as d:
    d.wait_boot(50)
    base = snap(d)
    for name, axis, xy in (('left right', 'MAIN', (1.0, 0.5)), ('left up', 'MAIN', (0.5, 1.0)), ('right right', 'C', (1.0, 0.5)), ('right up', 'C', (0.5, 1.0))):
        d.wii.axis(axis, *xy); time.sleep(1.0)
        print('==', name); print('\n'.join(diff(base, snap(d)))); d.wii.axis(axis, 0.5, 0.5); time.sleep(0.7)
