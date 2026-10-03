"""Boot a patched image and dump suspicious log lines (invalid memory accesses etc)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
region = sys.argv[1] if len(sys.argv) > 1 else 'RMKE01'
with Dolphin(os.path.join(ROOT, 'work', 'test_%s.wbfs' % region), gc=True, wiimote=sys.argv[2] if len(sys.argv) > 2 else 'none', region=region) as d:
    d.wait_boot(40)
    print(d.kpad())
