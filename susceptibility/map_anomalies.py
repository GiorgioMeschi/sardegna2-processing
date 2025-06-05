
'''
compute monthly maps of anomalies comparing monhtly map with static map
the sttic map derives from a custom static model with mean spi1 3 6 12 over 17 years
'''
#%%
import os
import geopandas as gpd
import rasterio as rio
import numpy as np
from geospatial_tools import geotools as gt
import matplotlib.pyplot as plt

Ras = gt.Raster()

static_map_file = '/home/sadc/share/project/calabria/data/susceptibility/static/susceptibility/SUSCEPTIBILITY.tif'
monthly_folder = '/home/sadc/share/project/calabria/data/susceptibility/v4'
outfolder = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG/anomalies'
os.makedirs(outfolder, exist_ok=True)
static_arr = Ras.read_1band(static_map_file)
static_arr_nan = np.where(static_arr == -1, np.nan, static_arr)

years = list(range(2020, 2025))
months = list(range(1, 13))

yearmonths = [f'{year}_{month}' for year in years for month in months]

for month in yearmonths:
    print(month)
    filepath = os.path.join(monthly_folder, f'susc_calabria_{month}.tif')
    # compute array of anomalies
    with rio.open(filepath) as month_ras:
        arr = month_ras.read(1)
        arr = np.where(arr == -1, np.nan, arr)
        arr = ((arr / static_arr_nan) - 1)*100 # percentage of anomaly, ex: 100% means twice the value
        arr[np.isnan(arr)] = -9999
        # plot    
        out = os.path.join(outfolder, f'anomaly_{month}.png')  
        if not os.path.exists(out):                   
            Ras.plot_raster(arr,
                array_classes = [-9999, -500, -300, -150, -50, -25, 0, 25, 50, 150, 300, 500, 10000],
                array_colors = [
                    "#00000000",  # Transparent for nodata
                    "#1f5f91",    # Extreme negative (< -500)
                    "#3f83b9",    # very Strong negative (-300)
                    "#6ca6dc",    # Strong negative (-150)
                    "#a5c8f0",    # Moderate negative (-50)
                    "#d0e1f9",    # Slight negative (-25)
                    "#d3d3d3",    # No anomaly (0)
                    "#ffecd9",    # Slight positive (25)
                    "#ffc4a3",    # Moderate positive (50)
                    "#ff8a66",    # Strong positive (150)
                    "#e44d2e",    # very Strong positive (300)
                    "#b71616",    # Very strong positive (500)
                    "#7f0000",    # Extreme positive (>500)
                ],
                array_names = [
                    "No Data", 
                    "Extreme negative anomaly\n(> 6 times lower)", 
                    "Very strong negative anomaly", 
                    "Strong negative anomaly", 
                    "Moderate negative anomaly", 
                    "Slight negative anomaly", 
                    "No anomaly", 
                    "Slight positive anomaly", 
                    "Moderate positive anomaly", 
                    "Strong positive anomaly", 
                    "Very strong positive anomaly", 
                    "Extreme positive anomaly\n(> 6 times higher)"
                ],
                shrink_legend=0.6,
                title = f'Anomaly {month}',
                outpath = out,
            )
            del arr
            plt.close('all')

#%% merge

#images
Img = gt.Imtools()

basep = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG/anomalies'
out_folder = '/home/sadc/share/project/calabria/data/susceptibility/v4/PNG/MERGED'
years = list(range(2007, 2025))
months = list(range(1, 13))

os.makedirs(out_folder, exist_ok=True)

yearmonths = [f"{year}_{month}" for year in years for month in months]
year_filenames = [f'anomaly_{yrm}' for yrm in yearmonths]
year_files = [f"{basep}/{filename}.png" for filename in year_filenames]


fig = Img.merge_images(year_files, ncol=12, nrow=18)
# fig.savefig(f"{out_folder}/susc_plot_{year}.png", dpi=500, bbox_inches='tight')
# save image (Image object)
fig.save(f"{out_folder}/anomaly_2007-2024.png")

#%%


