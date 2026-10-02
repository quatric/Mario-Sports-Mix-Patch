"""Boot the extracted USA disc with Vague Rant's Classic Controller codes and print the KPAD state."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import Dolphin, CC_PIPE
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
codes = open(os.path.join(ROOT, 'src', 'cc', 'RMKE01.txt')).read()
codes = '$' + codes   # first line is the title
with Dolphin(os.path.join(ROOT, 'work', 'test_RMKE01.wbfs'), wiimote='classic') as d:
    d.wait_boot(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
    print('idle', d.kpad())
    for b in ('A', 'B', 'X', 'Y', 'ZL', 'ZR', '+', '-', 'Up', 'Down', 'Left', 'Right'):
        d.wii.press(CC_PIPE[b]); time.sleep(0.7)
        k = d.kpad(); print('%-5s hold=%08X dev=%d' % (b, k['hold'], k['dev']), flush=True)
        d.wii.release(CC_PIPE[b]); time.sleep(0.4)
