"""Print the newest raw WPAD sample (the Classic Controller's wire format) for a few stick/button states."""
import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
def newest(d):
    b = d.peek(d.kpad_base(0), 0x188 + 0x42 * 16)
    i = (b[0x17A] - 1) % 16
    return b[0x180 + i * 0x42:0x180 + (i + 1) * 0x42]
def show(tag, s):
    print('%-14s btn=%s acc=%s dpd=%s ext[28..]=%s fmt=%02X | %s' % (tag, s[0:2].hex(), s[2:8].hex(), s[8:0x28].hex(), s[0x28:0x42].hex(), s[0x40], ''))
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), wiimote='nunchuk', region=region) as d:
    d.wait_boot(50)
    show('idle', newest(d))
    k=d.peek(d.kpad_base(0), 0x688); print('dev', k[0x5c], 'fmt', k[0x5f], 'flag641', k[0x641])
