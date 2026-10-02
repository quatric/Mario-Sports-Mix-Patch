import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
with Dolphin(os.path.join(ROOT, 'games', 'Mario Sports Mix (USA) (En,Fr,Es).wbfs'), wiimote='classic') as d:
    d.wait_boot(50)
    def ring():
        b = d.peek(d.kpad_base(0), 0x188 + 0x42*16)
        return b, [struct.unpack('>H', b[0x180+i*0x42+0x2a:0x180+i*0x42+0x2c])[0] for i in range(16)]
    print('idle', ring()[1])
    d.wii.press('A'); time.sleep(1.0)
    b, r = ring(); print('A', r, 'hold', b[:4].hex(), 'dev', b[0x5c])
    for i in range(3):
        time.sleep(0.3); b, r = ring(); print('A', r, 'hold', b[:4].hex())
    d.wii.release('A')
