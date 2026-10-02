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
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), wiimote='classic', region=region) as d:
    d.wait_boot(50)
    show('idle', newest(d))
    for tag, fn in (('lstick right', lambda: d.wii.axis('MAIN', 1.0, 0.5)), ('lstick up', lambda: d.wii.axis('MAIN', 0.5, 1.0)), ('rstick right', lambda: d.wii.axis('C', 1.0, 0.5)), ('rstick up', lambda: d.wii.axis('C', 0.5, 1.0))):
        fn(); time.sleep(0.8); show(tag, newest(d)); d.wii.axis('MAIN', 0.5, 0.5); d.wii.axis('C', 0.5, 0.5); time.sleep(0.5)
    d.wii.set1('L', 1.0); time.sleep(0.8); show('L analog', newest(d)); d.wii.set1('L', 0.0)
    d.wii.set1('R', 0.5); time.sleep(0.8); show('R half', newest(d)); d.wii.set1('R', 0.0)
