import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
with Dolphin(os.path.join(ROOT, 'work', 'test_RMKE01.wbfs'), gc=True, wiimote='none') as d:
    d.wait_boot(50)
    d.gc.press('Z'); time.sleep(0.5)
    for i in range(8):
        b = d.peek(d.kpad_base(0), 0x688)
        print('hold %s dev %d err %d fmt %d flag641 %d ex60 %s' % (b[0:4].hex(), b[0x5c], b[0x5d], b[0x5f], b[0x641], b[0x60:0x68].hex()))
        time.sleep(0.15)
