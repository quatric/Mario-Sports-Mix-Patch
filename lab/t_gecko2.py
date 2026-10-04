import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ini = open(os.path.join(ROOT, 'codes', 'RMKE01.ini')).read().split('\n', 1)[1]
which = sys.argv[1]
if which == 'gc':
    ini = '$GameCube controller' + ini.split('$GameCube controller')[1]
if which == 'cc':   # classic codes only
    ini = ini.split('$GameCube controller')[0]
disc = [f for f in os.listdir(os.path.join(ROOT, 'games')) if 'USA' in f][0]
with Dolphin(os.path.join(ROOT, 'games', disc), gc=True, wiimote=sys.argv[2], gecko=ini) as d:
    d.wait_boot(50)
    print('cc site', d.peek(0x8006FFD0, 4).hex(), 'site1', d.peek(0x8030FCF4, 8).hex(), 'site2', d.peek(0x8030FD14, 8).hex())
    print(d.kpad())
