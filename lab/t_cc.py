"""Classic Controller check on a patched image: every button, both sticks."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin, CC_PIPE
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
EXPECT = {'A': 0x800, 'B': 0x80, 'X': 0xC00, 'Y': 0x40, 'ZL': 0x2000, 'ZR': 0x400, '+': 0x10, '-': 0x1000,
          'Up': 8, 'Down': 4, 'Left': 1, 'Right': 2}
bad = 0
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), wiimote='classic', region=region) as d:
    d.wait_boot(50)
    print('idle', d.kpad())
    for b, want in EXPECT.items():
        d.wii.press(CC_PIPE[b]); time.sleep(0.8)
        k = d.kpad(); ok = (k['hold'] & 0xFFFF) == want; bad += not ok
        print('%-5s hold=%08X want=%04X dev=%d %s' % (b, k['hold'], want, k['dev'], 'ok' if ok else 'FAIL'), flush=True)
        d.wii.release(CC_PIPE[b]); time.sleep(0.4)
    d.wii.axis('MAIN', 1.0, 0.5); time.sleep(0.8); print('left stick right', d.kpad()['ls'], d.kpad()['ptr'])
    d.wii.axis('MAIN', 0.5, 1.0); time.sleep(0.8); print('left stick up   ', d.kpad()['ls'])
    d.wii.axis('MAIN', 0.5, 0.5)
    d.wii.axis('C', 1.0, 0.5); time.sleep(0.8); print('right stick right', d.kpad()['rs'], d.kpad()['ptr'])
print('FAILED' if bad else 'ok')
