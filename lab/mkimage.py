#!/usr/bin/env python3
"""Build a patched test image: patch a region's retail main.dol, drop it into the
extracted disc folder and rebuild a .wbfs with wit.

    python3 lab/mkimage.py RMKE01 cc gc      ->  work/test_RMKE01.wbfs
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import patcher
from dol import Dol


def make(region, which, out=None):
    disc = os.path.join(ROOT, 'work', 'disc_' + region)
    if not os.path.isdir(disc):
        src = [f for f in os.listdir(os.path.join(ROOT, 'games')) if f.endswith('.wbfs') and region in subprocess.run(
            ['wit', 'dump', os.path.join(ROOT, 'games', f)], capture_output=True, text=True).stdout][0]
        subprocess.run(['wit', 'extract', os.path.join(ROOT, 'games', src), '--dest', disc, '--psel', 'data', '-q'], check=True)
    d = Dol(os.path.join(ROOT, 'dumps', region + '.dol'))
    patcher.patch(d, region, which)
    d.save(os.path.join(disc, 'sys', 'main.dol'))
    out = out or os.path.join(ROOT, 'work', 'test_%s.wbfs' % region)
    subprocess.run(['wit', 'copy', disc, '--dest', out, '--wbfs', '--overwrite', '-q'], check=True)
    shutil.copyfile(os.path.join(ROOT, 'dumps', region + '.dol'), os.path.join(disc, 'sys', 'main.dol'))
    return out


if __name__ == '__main__':
    print(make(sys.argv[1], sys.argv[2:]))
