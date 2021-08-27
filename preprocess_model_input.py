# -*- coding: utf-8 -*-
# Normalizing arrays values according to satellite band

from glob import glob
import pickle

import numpy as np
from sklearn.preprocessing import MinMaxScaler


# Opening pickles
files = glob(
    "misc/term_project-aga5926/data/imgs_*.pickle"
)
# print(files)

with open(files[0], "rb") as input:
    imgs_random_band = pickle.load(input)
imgs_random_band = [item for sublist in imgs_random_band for item in sublist]
with open(files[1], "rb") as input:
    imgs_band = pickle.load(input)
imgs_band = [item for sublist in imgs_band for item in sublist]
with open(files[2], "rb") as input:
    imgs_mask = pickle.load(input)
imgs_mask = [item for sublist in imgs_mask for item in sublist]
with open(files[3], "rb") as input:
    imgs_nomask = pickle.load(input)
imgs_nomask = [item for sublist in imgs_nomask for item in sublist]
with open(files[4], "rb") as input:
    imgs_random = pickle.load(input)
imgs_random = [item for sublist in imgs_random for item in sublist]

# Normalize values according to band
ranges = {
    "C02": np.full((150, 150), np.repeat([0.0, 1.3], 75)).transpose(),
    "C11": np.full((150, 150), np.repeat([127.69, 341.30], 75)).transpose(),
    "C13": np.full((150, 150), np.repeat([89.62, 341.27], 75)).transpose(),
    "C14": np.full((150, 150), np.repeat([96.19, 341.28], 75)).transpose(),
    "C15": np.full((150, 150), np.repeat([97.38, 341.28], 75)).transpose(),
}

# Testing function
# scaler = MinMaxScaler(copy=False)
# test = scaler.fit(ranges["C02"])
# print(scaler.data_min_)
# test2 = scaler.transform(np.array([0.1, 0.5, 1, 0.0, 1.3]).reshape(-1, 1))
# print(test2)

# Masked/unmasked images
norm_mask = []
norm_nomask = []
for i in range(len(imgs_band)):
    # Get band
    band = imgs_band[i]
    # Create scaler for normalization
    scaler = MinMaxScaler(copy=False)
    model_fit = scaler.fit(ranges[band])
    # Check if shape is valid, skip if isn't
    if imgs_mask[i].shape == (150, 150):
        # Transform data
        norm_mask.append(scaler.transform(imgs_mask[i]))
    # Check if shape is valid, skip if isn't
    if imgs_nomask[i].shape == (150, 150):
        # Transform data
        norm_nomask.append(scaler.transform(imgs_nomask[i]))
    del scaler, model_fit
# Add in pickle
with open(
    "misc/term_project-aga5926/data/norm_mask.pickle",
    "wb",
) as output:
    pickle.dump(norm_mask, output, pickle.HIGHEST_PROTOCOL)
with open(
    "misc/term_project-aga5926/data/norm_nomask.pickle",
    "wb",
) as output:
    pickle.dump(norm_nomask, output, pickle.HIGHEST_PROTOCOL)

print("Masked/unmasked images done!")

# Random images
norm_random = []
for i in range(len(imgs_random_band)):
    # Get band
    band = imgs_random_band[i]
    # Create scaler for normalization
    scaler = MinMaxScaler(copy=False)
    model_fit = scaler.fit(ranges[band])
    # Check if shape is valid, skip if isn't
    if imgs_random[i].shape == (150, 150):
        # Transform data
        norm_random.append(scaler.transform(imgs_random[i]))
    del scaler, model_fit
# Add in pickle
with open(
    "misc/term_project-aga5926/data/norm_random.pickle",
    "wb",
) as output:
    pickle.dump(norm_random, output, pickle.HIGHEST_PROTOCOL)
print("Random images done!")

