"""Stock disc + the Gecko codes from codes/<ID>.ini (the non-disc install path): Wii Remote + GameCube pad."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
disc = [f for f in os.listdir(os.path.join(ROOT, 'games')) if f.endswith('.wbfs') and {'RMKE01': 'USA', 'RMKP01': 'Europe', 'RMKJ01': 'Japan'}[region] in f][0]
ini = open(os.path.join(ROOT, 'codes', region + '.ini')).read().split('\n', 1)[1]   # drop [Gecko]
with Dolphin(os.path.join(ROOT, 'games', disc), gc=True, wiimote='none', region=region, gecko=ini) as d:
    d.wait_boot(50)
    print('idle', d.kpad())
    for b in ('A', 'B', 'Start'):
        d.gc.press({'Start': 'START'}.get(b, b)); time.sleep(0.8)
        print(b, hex(d.kpad()['hold']), d.kpad()['dev'], flush=True)
        d.gc.release({'Start': 'START'}.get(b, b)); time.sleep(0.4)
