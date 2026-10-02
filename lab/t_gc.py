"""GameCube pad check on a patched image: every button, both sticks, with a plain Wii Remote (no extension) connected."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
EXPECT = {'A': 0x800, 'B': 0x80, 'X': 0xC00, 'Y': 0x40, 'Z': 0x2000, 'R': 0x400, 'L': 0x4001, 'Start': 0x10,
          'Up': 8, 'Down': 4, 'Left': 1, 'Right': 2}
bad = 0
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), gc=True, wiimote='none', region=region) as d:
    d.wait_boot(50)
    print('SIPOLL shadow', d.peek(0x804A5444, 4).hex())
    print('idle', d.kpad())
    for b, want in EXPECT.items():
        d.gc.press({'Start': 'START', 'Up': 'D_UP', 'Down': 'D_DOWN', 'Left': 'D_LEFT', 'Right': 'D_RIGHT'}.get(b, b)); time.sleep(0.8)
        k = d.kpad(); ok = (k['hold'] & 0xFFFF) == want; bad += not ok
        print('%-5s hold=%08X want=%04X dev=%d %s' % (b, k['hold'], want, k['dev'], 'ok' if ok else 'FAIL'), flush=True)
        d.gc.release({'Start': 'START', 'Up': 'D_UP', 'Down': 'D_DOWN', 'Left': 'D_LEFT', 'Right': 'D_RIGHT'}.get(b, b)); time.sleep(0.4)
    d.gc.axis('MAIN', 1.0, 0.5); time.sleep(0.8); print('stick right', d.kpad()['ls'], 'raw', d.peek(d.kpad_base(0) + 0x60, 8).hex())
    d.gc.axis('MAIN', 0.5, 1.0); time.sleep(0.8); print('stick up   ', d.peek(d.kpad_base(0) + 0x60, 8).hex())
    d.gc.axis('MAIN', 0.5, 0.5)
    d.gc.axis('C', 1.0, 0.5); time.sleep(0.8); print('C right', d.kpad()['rs'], d.kpad()['ptr'])
print('FAILED' if bad else 'ok')
