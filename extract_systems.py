# -*- coding: utf-8 -*-

# Adapted from tathu/examples/query-example.py

import os
import sys


# To use local package
sys.path.append("../")

from tathu.io import spatialite, icsv


# Setup SpatiaLite extension
os.environ["PATH"] = (
    os.environ["PATH"] + ";../spatialite/mod_spatialite-4.3.0a-win-amd64"
)

# Setup informations to load systems from database
dbname = "data_in/tracking-20200112-20200114.sqlite"
table = "systems"

# Load database
db = spatialite.Loader(dbname, table)
# print(db)

# Get systems
# by name
names = db.loadNames()
# print(names)
# Save in csv
outputter = icsv.Outputter(
    "data_in/systems-20200112-20200114.csv",
    outputGeom=True,
    outputCentroid=True,
)
for name in names:
    family = db.load(name, ["count"])
    outputter.output(family.systems)
