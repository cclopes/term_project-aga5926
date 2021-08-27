# -*- coding: utf-8 -*-

# Adapted from TATHU output examples

import os
import sys
from glob import glob
import pickle
import math

import numpy as np
import matplotlib.pyplot as plt

from osgeo import gdal


# To use local package
sys.path.append("../")

from tathu.io import spatialite
from tathu.constants import LAT_LON_WGS84
from tathu.utils import file2timestamp, getExtent
from tathu.satellite import goes16


def read_mask_g16(file, db, timestamp):
    """
    This function:

    - Reads GOES-16 data and convert to grid
    - Get polygons of systems identified by TATHU
    - Creates mask from polygon raster
    - Creates subgrid of the same size as the mask
    - Applies mask

    Returning 3 lists of masked and unmasked data arrays and band info
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

    # Select systems by timestamp
    print("Loading systems")
    systems = db.loadByDate("%Y-%m-%d %H:%M:%S", str(timestamp), [])

    # Create mask by raster
    print("Creating masked/unmasked arrays")
    imgs_nomask = []
    imgs_mask = []
    imgs_band = []
    sizearray = 150
    for sys in systems:
        # sys = systems[0]
        # print(dir(sys))

        # Get polygon
        poly = sys.raster
        # print(np.min(poly), np.max(poly))
        poly_centroid = sys.getCentroid()
        # Normalizing size
        padx = abs(sizearray - poly.shape[0])
        pady = abs(sizearray - poly.shape[1])
        # print("padx,y", padx, pady)
        if padx % 2 == 0:
            lpad = int(padx / 2)
            rpad = int(padx / 2)
            if pady % 2 == 0:
                upad = int(pady / 2)
                dpad = int(pady / 2)
                poly = np.pad(
                    poly,
                    ((lpad, rpad), (upad, dpad)),
                    "constant",
                    constant_values=(-999,),
                )
            else:
                upad = math.floor(pady / 2)
                dpad = math.ceil(pady / 2)
                # print("u,dpad", upad, dpad)
                poly = np.pad(
                    poly,
                    ((lpad, rpad), (upad, dpad)),
                    "constant",
                    constant_values=(-999,),
                )
        else:
            lpad = math.floor(padx / 2)
            rpad = math.ceil(padx / 2)
            # print("l,rpad", lpad, rpad)
            if pady % 2 == 0:
                upad = int(pady / 2)
                dpad = int(pady / 2)
                poly = np.pad(
                    poly,
                    ((lpad, rpad), (upad, dpad)),
                    "constant",
                    constant_values=(-999,),
                )
            else:
                upad = math.floor(pady / 2)
                dpad = math.ceil(pady / 2)
                # print(upad, dpad)
                poly = np.pad(
                    poly,
                    ((lpad, rpad), (upad, dpad)),
                    "constant",
                    constant_values=(-999,),
                )
        poly = np.in1d(poly, -999).reshape(poly.shape)
        poly_mask = np.ma.getmaskarray(poly)

        poly_extent = getExtent(sys.geotransform, poly.shape)
        # print(poly_mask.shape)
        # print(poly_extent)
        # Quick plot
        # plt.imshow(poly_mask)
        # plt.colorbar()

        # Subset grid
        subgrid = gdal.Translate(
            "/vsimem/in_memory_output.tif",
            grid,
            projWin=[
                poly_extent[0],
                poly_extent[3],
                poly_extent[2],
                poly_extent[1],
            ],
        ).ReadAsArray()
        # print(subgrid.shape)

        # Mask grid
        subgrid_masked = np.ma.array(subgrid, mask=poly_mask)
        # print(subgrid_masked)

        # Quick plot
        # plt.imshow(subgrid_masked)
        # plt.colorbar()

        # Append images
        imgs_nomask.append(subgrid)
        imgs_mask.append(subgrid_masked)
        imgs_band.append(img_band)

    print("Done! " + str(timestamp) + " - " + img_band)

    del grid, systems

    return imgs_nomask, imgs_mask, imgs_band


# Setup SpatiaLite extension
os.environ["PATH"] = (
    os.environ["PATH"] + ";../spatialite/mod_spatialite-4.3.0a-win-amd64"
)

# Get files and timestamps
files = glob("/mnt/d/Data/g16/aga5926/*.nc")
timestamps = [
    file2timestamp(file, yearpos=59, format="%Y%j%H%M%S") for file in files
]
# print(len(timestamps))

# Setup information to load systems from database
dbname = "misc/term_project-aga5926/data/tracking-20200112-20200114.sqlite"
table = "systems"

# Load database
db = spatialite.Loader(dbname, table)
# print(db)

# Get masked and unmasked arrays by date
imgs_nomask = []
imgs_mask = []
imgs_band = []

# Open arrays in pickle objects (IF NECESSARY)
# with open("misc/term_project-aga5926/data/imgs_nomask.pickle", "rb") as input:
#     imgs_nomask = pickle.load(input)
# with open("misc/term_project-aga5926/data/imgs_mask.pickle", "rb") as input:
#     imgs_mask = pickle.load(input)
# with open("misc/term_project-aga5926/data/imgs_band.pickle", "rb") as input:
#     imgs_band = pickle.load(input)

# Populating arrays
for file, timestamp in zip(files, timestamps):
    nomask, mask, band = read_mask_g16(file, db, timestamp)
    imgs_nomask.append(nomask)
    imgs_mask.append(mask)
    imgs_band.append(band)

# See total length of final list
# count = 0
# for step in imgs_band:
#     count += len(step)
# print("Total of systems:", count)

# Save arrays in pickle objects
with open(
    "misc/term_project-aga5926/data/imgs_nomask.pickle", "wb"
) as output:
    pickle.dump(imgs_nomask, output, protocol=pickle.HIGHEST_PROTOCOL)
with open(
    "misc/term_project-aga5926/data/imgs_mask.pickle", "wb"
) as output:
    pickle.dump(imgs_mask, output, protocol=pickle.HIGHEST_PROTOCOL)
with open(
    "misc/term_project-aga5926/data/imgs_band.pickle", "wb"
) as output:
    pickle.dump(imgs_band, output, protocol=pickle.HIGHEST_PROTOCOL)

