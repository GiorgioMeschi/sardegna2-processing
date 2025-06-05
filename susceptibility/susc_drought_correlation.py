# 1) open every spi1 3 6 12 and calculate the mean value for each month
# 2) for that month compute the area at high susceptibility (>= lv2)
# 3) append to a dataframe

import os 
from rasterio.mask import mask as riomask
import rasterio as rio
import geopandas as gpd
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

from home import DATAPATH

# 1
years = list(range(2011, 2024))
months = list(range(1, 13))
yearmonths = [f"{year}_{month}" for year in years for month in months]
months_aggregation = [1, 3, 6]
variables = ['SPI', 'SPEI', 'P', 'Tanomaly', 'T'] # last one is mean T

calabria_path = f'{DATAPATH}/aoi/calabria.geojsonl.json'
calabria = gpd.read_file(calabria_path)
calabria = calabria.to_crs(epsg=4326)
calabria_geom = calabria.geometry.values[0]
vs_susc = 'v1'
susc_thresholds_file = f'{DATAPATH}/susceptibility/{vs_susc}/thresholds/thresholds.json'
high_threshold = json.load(open(susc_thresholds_file))['lv2']

corr_df = pd.DataFrame()
for year in years:
    for month in months:

        print(f"{year}-{month:02d}")

        # put susc 
        susc_file = f"{DATAPATH}/susceptibility/{vs_susc}/susc_calabria_{year}_{month}.tif"
        with rio.open(susc_file) as src:
            susc_arr = src.read(1)
        susc_arr = np.where(susc_arr >= high_threshold, 1, 0)
        high_susc_pixels = np.sum(susc_arr)
        del susc_arr
        
        corr_df.loc[f'{year}_{month}', f'pixels_high_susc'] = int(high_susc_pixels)

        for var in variables:
            for aggr in months_aggregation:

                if var == 'SPI':
                    basep = f'/home/drought/drought_share/archive/Italy/{var}/MCM/maps/{year}/{month:02}'
                    day = os.listdir(basep)[-1]
                    name = f'{var}{aggr}-MCM_{year}{month:02}{day}.tif'
                    path = f'{basep}/{day}/{name}'

                elif var == 'SPEI':
                    basep = f'/home/drought/drought_share/archive/Italy/{var}/MCM-DROPS/maps/{year}/{month:02}'
                    day = os.listdir(basep)[-1]
                    name = f'{var}{aggr}-MCM-DROPS_{year}{month:02}{day}.tif'
                    path = f'{basep}/{day}/{name}'

                elif var == 'P':
                    basep = f'/home/drought/drought_share/data/Italy/output/{var}/MCM/{aggr}m/{year}'
                    name_cut = f'{var}_{aggr}m_{year}{month:02}'
                    allnames = os.listdir(basep)
                    name = [name for name in allnames if name.startswith(name_cut)][0]
                    path = f'{basep}/{name}'

                elif var == 'Tanomaly':
                    basep = f'/home/drought/drought_share/archive/Italy/{var}/DROPS/maps/{year}/{month:02}'
                    day = os.listdir(basep)[-1]
                    name = f'TANOMALY{aggr}_zscr-DROPS_{year}{month:02}{day}.tif'
                    path = f'{basep}/{day}/{name}'

                elif var == 'T':
                    name = f'AirT_{aggr}m_DROPS_{year}{month:02}_italy.tif'
                    path = f'/home/drought/drought_share/data/Italy/output/T_ANOMALY/DROPS/{aggr}m/{year}/{name}'

                
                with rio.open(path) as src:
                    out_image, _ = riomask(src, [calabria_geom], crop = True, nodata = -9999)
                # compute mean value excluding -9999
                out_image[out_image == -9999] = np.nan
                _mean = np.nanmean(out_image)
                corr_df.loc[f'{year}_{month}', f'{var}{aggr}'] = round(_mean, 2)

#add fires
fires_file = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
fires = gpd.read_file(fires_file)
fires['date_iso'] = pd.to_datetime(fires['date_iso'])
fires['year'] = fires['date_iso'].dt.year
fires['month'] = fires['date_iso'].dt.month
#eval area for each month of the year
print('\nFIRES\n\n')
for year in years:
    for month in months:
        print(f"{year}-{month:02d}")
        # get the area of the burned area
        month_fires = fires[(fires['year'] == year) & (fires['month'] == month)]
        if len(month_fires) > 0:
            month_area = month_fires.area.sum() / 10000
        else:
            month_area = 0
        corr_df.loc[f'{year}_{month}', 'burned_area'] = int(month_area)

# corr matrix
corr = corr_df.corr(method='pearson')
#plot
fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.matshow(corr, cmap='coolwarm')

# Add colorbar
plt.colorbar(cax)

# Set ticks and labels
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha='left')
ax.set_yticklabels(corr.columns)

# Optional: add values in each cell
for (i, j), val in np.ndenumerate(corr.values):
    ax.text(j, i, f'{val:.2f}', ha='center', va='center', color='black', fontsize=6)

plt.tight_layout()

# save df and plot
out = f'{DATAPATH}/susceptibility/{vs_susc}/correlation'
os.makedirs(out, exist_ok=True)
corr_df.to_csv(f'{out}/corr_df.csv')
fig.savefig(f'{out}/corr_matrix.png', dpi=300, bbox_inches='tight')



