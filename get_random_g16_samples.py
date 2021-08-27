# -*- coding: utf-8 -*-

# Adapted from TATHU output examples

import os
import sys
from glob import glob
import pickle
import random

import numpy as np
import matplotlib.pyplot as plt

from osgeo import gdal


# To use local package
sys.path.append("../")

from tathu.constants import LAT_LON_WGS84, KM_PER_DEGREE
from tathu.utils import file2timestamp, getExtent
from tathu.satellite import goes16


def read_sample_g16(file, timestamp):
    """
    This function:

    - Reads GOES-16 data and convert to grid
    - Get random samples with same array size

    Returning two lists of data arrays and band info
    """

    # Read data and map channel to 2km
    print("Reading grid")
    extent = [-85.0, -60.0, -30.0, 15.0]
    grid = goes16.sat2grid(
        file, extent, 2.0, LAT_LON_WGS84, "HDF5", progress=None
    )
    img_band = file[42:45]
    # print(img_band)
    # print(type(grid))
    # Quick plot
    # plt.imshow(grid.ReadAsArray())

    # Create array by random sample
    print("Creating random arrays")
    imgs_random = []
    imgs_band = []
    # Create lat/lon grid for random centroid sample
    sizex = int(((extent[2] - extent[0]) * KM_PER_DEGREE) / 2.0)
    sizey = int(((extent[3] - extent[1]) * KM_PER_DEGREE) / 2.0)
    gridlat, gridlon = np.mgrid[
        extent[1] : extent[3] : complex(0, sizey),
        extent[0] : extent[2] : complex(0, sizex),
    ]
    # print(sizex, sizey)
    sizearray = 150
    center_lons = random.sample(range(75, sizex - 75), k=3)
    center_lats = random.sample(range(75, sizey - 75), k=3)
    for plon, plat in zip(center_lons, center_lats):
        # Subset grid
        subgrid = gdal.Translate(
            "/vsimem/in_memory_output.tif",
            grid,
            projWin=[
                gridlon[0, int(plon - sizearray / 2)],
                gridlat[int(plat + sizearray / 2), 0],
                gridlon[0, int(plon + sizearray / 2)],
                gridlat[int(plat - sizearray / 2), 0],
            ],
        ).ReadAsArray()
        # print(subgrid.shape)

        # Quick plot
        # plt.imshow(subgrid)
        # plt.colorbar()

        # Append images
        imgs_random.append(subgrid)
        imgs_band.append(img_band)

    print("Done! " + str(timestamp) + " - " + img_band)

    del grid, subgrid

    return imgs_random, imgs_band


# Setup SpatiaLite extension
os.environ["PATH"] = (
    os.environ["PATH"] + ";../spatialite/mod_spatialite-4.3.0a-win-amd64"
)

# Get files and timestamps
files = glob("misc/term_project-aga5926/data/*.nc")
timestamps = [
    file2timestamp(file, yearpos=59, format="%Y%j%H%M%S") for file in files
]
# print(len(timestamps))

# Get random arrays by date
imgs_random = []
imgs_band = []

# Populating arrays
for file, timestamp in zip(files, timestamps):
    grid_random, band = read_sample_g16(file, timestamp)
    imgs_random.append(grid_random)
    imgs_band.append(band)

# See total length of final list
# count = 0
# for step in imgs_band:
#     count += len(step)
# print("Total of systems:", count)

# Save arrays in pickle objects
with open(
    "misc/term_project-aga5926/data/imgs_random.pickle", "wb"
) as output:
    pickle.dump(imgs_random, output, protocol=pickle.HIGHEST_PROTOCOL)
with open(
    "misc/term_project-aga5926/data/imgs_random_band.pickle", "wb"
) as output:
    pickle.dump(imgs_band, output, protocol=pickle.HIGHEST_PROTOCOL)

