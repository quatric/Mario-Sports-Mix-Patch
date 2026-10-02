#!/usr/bin/env python3
"""Cut a release: check everything, tag it, push the tag; CI builds and attaches the downloads.

    python3 tools/release.py 1.0.0            # checks, tags v1.0.0, pushes main + the tag
    python3 tools/release.py 1.0.0 --dry-run  # checks only, changes nothing
    python3 tools/release.py 1.0.0 --local    # also zips codes/ and riivolution/ into dist/

The tag push starts .github/workflows/build-gui.yml, which builds the patcher for macOS, Linux and Windows and
attaches it, the Gecko codes and the Riivolution patches to a GitHub release with generated notes.
Needs a clean working tree on `main`.  Set RELEASE_SSH_KEY to push with a specific key.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PY = sys.executable


def run(*cmd, env=None, capture=False):
    r = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=capture)
    if r.returncode:
        sys.exit('failed: ' + ' '.join(cmd) + ('\n' + r.stdout + r.stderr if capture else ''))
    return r.stdout.strip() if capture else ''


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('version', help='x.y.z (the tag becomes vx.y.z)')
    ap.add_argument('--dry-run', action='store_true', help='run the checks, change nothing')
    ap.add_argument('--local', action='store_true', help='also zip the Gecko / Riivolution files into dist/')
    a = ap.parse_args()
    if not re.fullmatch(r'\d+\.\d+\.\d+', a.version):
        sys.exit('version must look like 1.2.3')
    tag = 'v' + a.version

    if run('git', 'rev-parse', '--abbrev-ref', 'HEAD', capture=True) != 'main':
        sys.exit('release from main')
    if run('git', 'status', '--porcelain', capture=True):
        sys.exit('working tree is not clean: commit or stash first')
    if run('git', 'tag', '--list', tag, capture=True):
        sys.exit('tag %s already exists' % tag)

    print('regenerating codes/ and riivolution/ ...')
    run(PY, 'tools/build.py')
    if run('git', 'status', '--porcelain', capture=True):
        sys.exit('generated files were stale: review, commit them, then release again')
    print('consistency checks ...')
    run(PY, 'tools/check.py')
    dols = os.environ.get('MSM_DOLS')
    if dols:
        print('retail DOL verification ...')
        run(PY, 'tools/verify.py')
    else:
        print('(set MSM_DOLS=<dir of retail main.dols> to also verify against the real games)')

    if a.local:
        out = os.path.join(ROOT, 'dist')
        os.makedirs(out, exist_ok=True)
        for name, d in (('Gecko-Codes', 'codes'), ('Riivolution', 'riivolution')):
            shutil.make_archive(os.path.join(out, 'MarioSportsMix-Patch-%s-%s' % (name, tag)), 'zip', ROOT, d)
        print('zips in', out)
    if a.dry_run:
        print('dry run: would tag and push', tag)
        return

    env = dict(os.environ)
    key = os.environ.get('RELEASE_SSH_KEY', os.path.expanduser('~/.ssh/id_ed25519_quatric'))
    if os.path.exists(key):
        env['GIT_SSH_COMMAND'] = 'ssh -i %s' % key
    run('git', 'tag', '-a', tag, '-m', 'Mario Sports Mix Patch ' + tag)
    run('git', 'push', 'origin', 'main', env=env)
    run('git', 'push', 'origin', tag, env=env)
    print('pushed %s: CI is building the release.' % tag)


if __name__ == '__main__':
    main()
