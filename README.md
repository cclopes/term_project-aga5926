# term_project-aga5926
Term Project for AGA5926 discipline @ IAG-USP. Description at [Project 7 in the proposals document](https://docs.google.com/document/d/1qw8Jy3IBGZOXkhLB7XZu8q14-8C5VLkAV_w2KdJlWFs/edit#heading=h.32btn4h0jcaf).

## Structure

### "Raw" data download
- `download_g16.py`: downloading data from [AWS](https://noaa-goes16.s3.amazonaws.com/index.html) based on date range and bands

### TATHU-related scripts
- `tracking_g16.py`: main tracking script extracted from TATHU tracking examples.
- `config-g16.ini`: settings applied on the `tracking_g16.py` file.

### TATHU post-processing
- `extract_systems.py`: converting `.sqlite` tracking output to `.csv`, if necessary.
- `get_random_g16_samples.py`: extracting random GOES-16 samples in arrays of 150 x 150 pixels as the "no convection" arrays.
- `mask_systems.py`: reading GOES-16 data + TATHU tracking output and applying polygon masks.
- `preprocess_model_input.py`: normalizing arrays values according to satellite bands.
- `visualize_systems.py`: quick looks of all centroids identified and mask/unmasked/random examples.

### CNN model application
- **`config_apply_model.ipynb`: main script. Applying the CNN model on the input datasets.**

### Data folder
- `g16` folder: GOES-16 level 2 files (available at [Google Drive](https://drive.google.com/file/d/1VSaS9XNo9IcxXf2rJfBGBqnnY5LO9dIh/view?usp=sharing))
- `cnn_test_80_20` and `cnn_test_90_10` folders: CNN models applied in the `config_apply_model` script
- `tracking-20200112-20200114.sqlite`: SQLite-based properties of systems identified by TATHU (available at [Google Drive](https://drive.google.com/file/d/13He1nxLaipv8ZSTf6HWcMkYmLyrliTJq/view?usp=sharing))
- `systems-20200112-20200114.csv`: CSV-based properties of systems identified by TATHU (available at [Google Drive](https://drive.google.com/file/d/13FnPcKbdjuLcxbP7aQbCj89e8uxvRtcl/view?usp=sharing))
- `imgs_pickles.zip`: masked/unmasked/random images arrays without normalization (available at [Google Drive](https://drive.google.com/file/d/1uACYhhpTyGAWJBVr4JwfrqcNY940OX4P/view?usp=sharing))
- **`imgs_input.zip`: masked/unmasked/random normalized images arrays used as input (available at [Google Drive](https://drive.google.com/file/d/14kxQPdyN5oQ-FgPWNJBYZG1XklvSqNpm/view?usp=sharing))**
