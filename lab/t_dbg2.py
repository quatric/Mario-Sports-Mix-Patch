import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
codes = '$' + open(os.path.join(ROOT, 'src', 'cc', 'RMKE01.txt')).read()
with Dolphin(os.path.join(ROOT, 'games', 'Mario Sports Mix (USA) (En,Fr,Es).wbfs'), wiimote='classic', gecko=codes) as d:
    for t in (10, 20, 30):
        d.wait_boot(10)
        print(t, 'handler', d.peek(0x80001800, 16).hex(), 'site', d.peek(0x8030CB94, 4).hex(), '0x800701C0', d.peek(0x800701C0,4).hex())
