"""Dump the KPAD channel-0 fields the GameCube hook trusts (sample ring pointer / counts), with and without a remote."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1]; wm = None if sys.argv[2] == 'off' else sys.argv[2]
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), gc=True, wiimote=wm, region=region) as d:
    d.wait_boot(40)
    for c in range(4):
        b = d.peek(d.kpad_base(c), 0x688)
        print(c, 'dev', b[0x5C], 'write', b[0x17A], 'cnt', b[0x17B], 'xring', b[0x5A0:0x5A4].hex(), 'xcount', b[0x5A4])
