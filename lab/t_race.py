import os, sys, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import gen_gc, features, json
from dol import Dol
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
gen_gc.EXTRA_DEFINES = {'DEBUG_COUNTERS': 0x80002F00}
import mkimage, patcher
f = gen_gc.build('RMKE01', Dol(ROOT + '/dumps/RMKE01.dol'))
# patch: apply this feature object together with cc
import ops
d = Dol(ROOT + '/dumps/RMKE01.dol'); cc = features.load('cc', 'RMKE01'); ops.apply_static(d, [cc, f]); d.save(ROOT + '/work/disc_RMKE01/sys/main.dol')
import subprocess; subprocess.run(['wit', 'copy', ROOT + '/work/disc_RMKE01', '--dest', ROOT + '/work/test_dbg.wbfs', '--wbfs', '--overwrite', '-q'], check=True)
