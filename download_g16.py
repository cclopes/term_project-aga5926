import os
from datetime import datetime, timedelta
import pandas as pd

from utilities import download_CMI

# Defining data path
data_path = "data_in/g16"
os.makedirs(data_path, exist_ok=True)

# AMAZON repository information
# https://noaa-goes16.s3.amazonaws.com/index.html
bucket_name = "noaa-goes16"
product_name = "ABI-L2-CMIPF"
dates = pd.date_range(
    datetime(2020, 1, 12, 0, 0), datetime(2020, 1, 14, 23, 50), freq="min"
).strftime("%Y%m%d%H%M")
# print(dates)
bands = ["2", "11", "13", "14", "15"]

# Download all the files
for band in bands:
    for date in dates:
        download_CMI(date, band, data_path)
