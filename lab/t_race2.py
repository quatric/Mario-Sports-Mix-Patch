import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
with Dolphin(os.path.join(ROOT, 'work', 'test_dbg.wbfs'), gc=True, wiimote='none') as d:
    d.wait_boot(50)
    d.gc.press('R'); time.sleep(0.3)
    bad = 0
    for i in range(30):
        try:
            k = d.kpad(); c = struct.unpack('>8I', d.peek(0x80002F00, 32))
        except ValueError:
            d.g.drain(1.0); continue
        if k['dev'] != 2 or not (k['hold'] & 0x400): bad += 1; print(i, 'BAD', k['dev'], hex(k['hold']), 'cnt(early calls,invalid,-,-, locked calls,invalid)=', c)
        time.sleep(0.2)
    print('bad', bad, 'counters', c)
