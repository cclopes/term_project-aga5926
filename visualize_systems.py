# -*- coding: utf-8 -*-

# Adapted from tathu/examples/tracking-analysis/visualize-centroids.py
#%%

import pickle

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import shapely.wkt


# All centroids plot
# Read dataset
# df = pd.read_csv("data/systems-20200112-20200114.csv", parse_dates=["timestamp"])
# geometry = df["centroid"].map(shapely.wkt.loads)
# crs = {"init": "epsg:4326"}
# gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
# # Adding shapefiles
# world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
# countries = world[world["continent"] == "South America"]
# # Main plot
# base = countries.plot(linewidth=0.25, edgecolor="darkgrey", color="lightgrey")
# gdf.plot(ax=base, marker=".", markersize=0.1, color="k")
# plt.xlabel("Lon (°)")
# plt.ylabel("Lat (°)")
# plt.title("Total Centroids = " + str(len(df["centroid"])))
# plt.show()
# plt.clf()

# Mask example
with open("data/imgs_mask.pickle", "rb") as input:
    imgs_mask = pickle.load(input)
with open("data/imgs_nomask.pickle", "rb") as input:
    imgs_nomask = pickle.load(input)
with open("data/imgs_random.pickle", "rb") as input:
    imgs_random = pickle.load(input)
# with open("data/imgs_band.pickle", "rb") as input:
#     imgs_band = pickle.load(input)
# with open("data/imgs_random_band.pickle", "rb") as input:
#     imgs_random_band = pickle.load(input)

# print(imgs_random_band[400])

fig, axs = plt.subplots(nrows=1, ncols=2)
im = axs[0].imshow(imgs_nomask[80][0], cmap="Greys", vmin=90, vmax=320, aspect=1)
# im = axs[1].imshow(imgs_mask[80][0], cmap="Greys", vmin=90, vmax=320, aspect=1)
im = axs[1].imshow(imgs_random[400][2], cmap="Greys", vmin=90, vmax=320, aspect=1)
# fig.subplots_adjust(right=0.85)
# cbar_ax = fig.add_axes([0.9, 0.15, 0.05, 0.7])
fig.colorbar(im, ax=axs.ravel().tolist(), aspect=7, shrink=0.55)
# plt.show()
plt.savefig(
    "nomask_random.png", dpi=300, bbox_inches="tight",
)

# %%
