# Test image: Bentheimer sandstone, 200 x 200 x 200 voxels

`Bentheimer200.raw.gz` is the first 200 x 200 x 200 voxels (x, y and z from 0 to 199) of the segmented micro-CT image of
Bentheimer sandstone published in the Digital Porous Media Portal:

> Muljadi, B. (2015). *Bentheimer Sandstone Dataset*. Digital Porous Media Portal. https://doi.org/10.17612/P77P49
> (image: https://web.corral.tacc.utexas.edu/digitalporousmedia/DRP-11/Bentheimer/Bentheimer%20image/bentheimer.raw)

* Original: 1000 x 1000 x 1000 voxels, 8 bit, segmented (0: pore, 255: solid), voxel size 3.0035 micrometre, little endian.
* Crop: 8 MB raw (206 KB gzipped, `.raw` read by the codes through the header written by the test), porosity 0.1938,
  made with [`crop_bentheimer.py`](crop_bentheimer.py): `./crop_bentheimer.py bentheimer.raw Bentheimer200.raw.gz`.
* Please cite the dataset above when using this image or results of the tests.
