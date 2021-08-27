# -*- coding: utf-8 -*-
#
#  Copyright (C) 2021 National Institute For Space Research (INPE) - Brazil.
#
#  This file is part of Tathu - Tracking and Analysis of Thunderstorms.
#
#  Tathu is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  Tathu is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Tathu. See LICENSE. If not, write to Tathu team at <tathu@inpe.br>.

__author__ = "Douglas Uba"
__email__ = "douglas.uba@inpe.br"

import argparse
import configparser
import datetime
import glob
import os
import sys

# Setup SpatiaLite extension
os.environ["PATH"] = (
    os.environ["PATH"] + ";../spatialite/mod_spatialite-4.3.0a-win-amd64"
)

# To use local package
# sys.path.append('../')

# Tathu imports
from tathu.constants import KM_PER_DEGREE, LAT_LON_WGS84
from tathu.io import spatialite
from tathu.satellite import goes16
from tathu.tracking import descriptors
from tathu.tracking import detectors
from tathu.utils import file2timestamp, Timer
from tathu.tracking import trackers

# Third-party imports
from osgeo import gdal


def get_datetime(str):
    """This function converts date string to datetime object."""
    year = str[0:4]
    month = str[4:6]
    day = str[6:8]
    return datetime.datetime.strptime(year + month + day, "%Y%m%d")


def get_days(start, end):
    """This function returns all-days between given two dates."""
    d1 = get_datetime(start)
    d2 = get_datetime(end)
    delta = d2 - d1
    days = []
    for i in range(delta.days + 1):
        days.append(d1 + datetime.timedelta(i))
    return days


def get_files(basedir, days):
    files = []
    for d in days:
        y = d.strftime("%Y")
        jd = d.strftime("%j")
        search = basedir + "OR_ABI-L2-CMIPF-M6C13_G16_*_c" + y + jd + "*.nc"
        print("Searching files", search)
        files += glob.glob(search)
    return sorted(files)


def extract_periods(files, timeout):
    previous_time = None
    result = []
    period = []
    for path in files:
        # Get current date/time
        current_time = file2timestamp(path, yearpos=59, format="%Y%j%H%M%S")

        # Initialize, if necessary
        if previous_time is None:
            previous_time = current_time

        # Compute elapsed time
        elapsed_time = current_time - previous_time

        if elapsed_time.seconds > timeout * 60:
            result.append(period)
            period = []
            previous_time = None
        else:
            period.append(path)
            previous_time = current_time

    result.append(period)

    return result


def detect(
    path,
    extent,
    resolution,
    threshold,
    minarea,
    stats,
    compute_cc,
    threshold_cc,
    minarea_cc,
):
    with Timer():
        # Extract file timestamp
        timestamp = file2timestamp(path, yearpos=59, format="%Y%j%H%M%S")

        print("Searching for systems at:", timestamp)

        # Remap channel to 2km
        grid = goes16.sat2grid(
            path, extent, resolution, LAT_LON_WGS84, "HDF5", progress=None
        )

        # Create detector
        detector = detectors.ThresholdDetector(
            threshold, detectors.ThresholdOp.LESS_THAN, minarea
        )

        # Searching for systems
        systems = detector.detect(grid)

        # Adjust timestamp
        for s in systems:
            s.timestamp = timestamp

        # Create statistical descriptor
        descriptor = descriptors.StatisticalDescriptor(
            stats=stats, rasterOut=True
        )

        # Describe systems (stats)
        systems = descriptor.describe(grid, systems)

        if compute_cc:
            # Create convective cell descriptor
            descriptor = descriptors.ConvectiveCellsDescriptor(
                threshold_cc, minarea_cc
            )
            # Describe systems (convective cell)
            descriptor.describe(grid, systems)

        grid = None

        return systems


def track(
    files,
    extent,
    resolution,
    threshold,
    minarea,
    stats,
    compute_cc,
    threshold_cc,
    minarea_cc,
    areaoverlap,
    outputter,
    current=None,
):
    try:
        img = 0
        if current is None:
            # Detect first systems
            current = detect(
                files[img],
                extent,
                resolution,
                threshold,
                minarea,
                stats,
                compute_cc,
                threshold_cc,
                minarea_cc,
            )
            # Save to output
            outputter.output(current)
            img = img + 1

        # Prepare tracking...
        previous = current

        # Create overlap area strategy
        strategy = trackers.RelativeOverlapAreaStrategy(areaoverlap)

        # for each image file
        for i in range(img, len(files)):
            # Detect current systems
            current = detect(
                files[i],
                extent,
                resolution,
                threshold,
                minarea,
                stats,
                compute_cc,
                threshold_cc,
                minarea_cc,
            )

            # Let's track!
            t = trackers.OverlapAreaTracker(previous, strategy=strategy)
            t.track(current)

            # Save to output
            outputter.output(current)

            # Prepare next iteration
            previous = current

    except Exception as e:
        print("Unexpected error:", e, sys.exc_info()[0])


def main():
    # Setup NetCDF driver
    gdal.SetConfigOption("GDAL_NETCDF_BOTTOMUP", "NO")

    # Parser line-arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--start", help="Start date (yyyymmdd)", type=str)
    group.add_argument(
        "-db", "--database", help="Path to an existing database", type=str
    )
    parser.add_argument(
        "-e", "--end", help="End date (yyyymmdd)", type=str, required=True
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Config tracking file location",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    # Read config file and extract infos
    config = configparser.ConfigParser()
    config.read(args.config)

    # Get extent
    extent = [float(i) for i in config.get("Grid", "extent").split(",")]

    # Get resolution
    resolution = float(config.get("Grid", "resolution"))

    # Get tracking parameters
    repository = config.get("TrackingParameters", "repository")
    timeout = float(config.get("TrackingParameters", "timeout"))
    threshold = float(config.get("TrackingParameters", "threshold"))
    minarea = float(config.get("TrackingParameters", "minarea"))
    areaoverlap = float(config.get("TrackingParameters", "areaoverlap"))
    stats = [i for i in config.get("TrackingParameters", "stats").split(",")]

    # Get tracking parameters related with convective cells
    compute_cc = config.getboolean("TrackingParameters", "compute_cc")
    threshold_cc = float(config.get("TrackingParameters", "threshold_cc"))
    minarea_cc = float(config.get("TrackingParameters", "minarea_cc"))

    # Last systems detected
    current = None

    # Columns
    columns = stats.copy()
    if compute_cc:
        columns.append("ncells")

    if args.start is not None:
        start = args.start
        # Get output parameters and setup database name
        outputdir = config.get("Output", "dir")
        dbname = (
            config.get("Output", "dbname")
            + "-"
            + start
            + "-"
            + args.end
            + ".sqlite"
        )
        database = outputdir + dbname
    else:
        database = args.database
        # Retrieve last date from the given existing database
        db = spatialite.Loader(database, "systems")
        # Get last date
        start = datetime.datetime.strptime(db.getLastDate(), "%Y%m%d")
        start = start + datetime.timedelta(days=1)
        start = start.strftime("%Y%m%d")
        # Load last systems
        current = db.loadLastSystems(columns)

    # Get all requested days
    days = get_days(start, args.end)

    # Get files
    files = get_files(repository, days)

    # Print infos
    print("== Tathu - Tracking and Analysis of Thunderstorms ==")
    print(":: Start Date:", start)
    print(":: End Date:", args.end)
    print(":: Config tracking file location:", args.config)
    print(":: Extent:", extent)
    print(":: Grid Resolution:", resolution, "km")
    print(":: Repository of images:", repository)
    print(
        ":: Minimum accepted time interval between two images:",
        timeout,
        "minutes",
    )
    print(":: Brightness temperature threshold:", threshold, "Kelvin")
    print(":: Minimum area of systems:", minarea, "km2")
    print(":: Area Overlap:", areaoverlap * 100, "%")
    print(":: Compute convective cells?", compute_cc)
    print(":: Stats:", stats)
    if compute_cc:
        print(":: CC temperature threshold:", threshold_cc, "Kelvin")
        print(":: Minimum area of CC:", minarea_cc, "km2")
    print("== Tracking Info ==")
    print(":: Number of days:", len(days))
    print(":: Number of images found:", len(files))

    if not files:
        print("* Tracking exit: No images found.")
        exit(0)

    # Convert to degrees^2
    minarea = minarea / (KM_PER_DEGREE * KM_PER_DEGREE)
    minarea_cc = minarea_cc / (KM_PER_DEGREE * KM_PER_DEGREE)

    # Extracting periods
    periods = extract_periods(files, timeout)

    # Create database connection
    db = spatialite.Outputter(database, "systems", columns)

    # Tracking
    for period in periods:
        track(
            period,
            extent,
            resolution,
            threshold,
            minarea,
            stats,
            compute_cc,
            threshold_cc,
            minarea_cc,
            areaoverlap,
            db,
            current,
        )


if __name__ == "__main__":
    main()
