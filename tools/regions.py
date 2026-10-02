"""The three retail releases of Mario Sports Mix and where their pieces moved.

All three are disc version 0.  The KPAD input library is the same code in each,
shifted by a small constant, which is what lets one set of signatures find every
site in every release.
"""
REGIONS = {
    'RMKE01': dict(label='Mario Sports Mix (USA)', short='USA', version=0),
    'RMKP01': dict(label='Mario Sports Mix (Europe)', short='Europe', version=0),
    'RMKJ01': dict(label='Mario Sports Mix (Japan)', short='Japan', version=0),
}

# retail DOL sizes, to give a clear error on someone else's modified dump
DOL_SIZES = {'RMKE01': 4991776, 'RMKJ01': 4995392, 'RMKP01': 4995680}
