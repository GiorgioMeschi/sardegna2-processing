

import rasterio as rio
from rasterio.mask import mask as riomask
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import json

from home import DATAPATH

susc_file = f'{DATAPATH}/susceptibility/static_v2/susceptibility/SUSCEPTIBILITY.tif'
fires_file = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
fires_col = 'date_iso'
crs = 'EPSG:3857'

fires = gpd.read_file(fires_file)
fires['date_iso'] = pd.to_datetime(fires['date_iso'])

# open susc, extract values in burned area
with rio.open(susc_file) as susc:
    # mask the raster with the fire polygons
    out_image, out_transform = riomask(susc, fires.geometry, nodata = -9999)
    # get the values of the masked area
    susc_values = out_image[out_image >= 0]
    # eval quantiles
    q1 = np.quantile(susc_values, 0.01)
    q2 = np.quantile(susc_values, 0.10)


folder = f'{DATAPATH}/susceptibility/static_v2/thresholds'
os.makedirs(folder, exist_ok=True)
# save in json
thresholds = dict(lv1=float(q1), lv2=float(q2))
with open(f'{folder}/thresholds.json', 'w') as f:
    json.dump(thresholds, f, indent=4)


import matplotlib.pyplot as plt

plt.imshow(out_image.squeeze())





