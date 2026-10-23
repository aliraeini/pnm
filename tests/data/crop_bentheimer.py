#!/usr/bin/env python3
"""Creates Bentheimer200.raw.gz, the test image of this folder, from the segmented Bentheimer sandstone image of the
Digital Porous Media Portal (https://doi.org/10.17612/P77P49, B. Muljadi, 2015): 1000 x 1000 x 1000 voxels of 8 bit
(0: pore, 255: solid), voxel size 3.0035 micrometre, little endian, x fastest.

Usage:  crop_bentheimer.py  bentheimer.raw  [Bentheimer200.raw.gz]  [n=200]

The first n x n x n voxels are kept (x, y and z from 0 to n-1). The gzip header is written without a time stamp, so
repeating the crop gives an identical file.
"""
import gzip
import sys

import numpy as np

NFULL = 1000

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else "Bentheimer200.raw.gz"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 200

vol = np.memmap(src, dtype=np.uint8, mode="r", shape=(NFULL, NFULL, NFULL))  # (z, y, x)
crop = np.ascontiguousarray(vol[:n, :n, :n])
with gzip.GzipFile(dst, "wb", compresslevel=9, mtime=0) as f:
    f.write(crop.tobytes())
print(f"{dst}: {n}^3 voxels, porosity (value 0): {(crop == 0).mean():.5f}")
