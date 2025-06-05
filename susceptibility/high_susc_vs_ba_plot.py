



import json
import os
import time
import numpy as np
import geopandas as gpd
import rasterio as rio
import pandas as pd
from geospatial_tools import geotools as gt
import matplotlib.pyplot as plt

gtras = gt.Raster()

basep = '/home/sadc/share/project/calabria/data/susceptibility/v4'
treshold_path = f'{basep}/thresholds/thresholds.json'
fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
fires_col = 'date_iso'
crs = 'EPSG:3857'
years = list(range(2007, 2024))
months = list(range(1, 13))

# here use vs13 thresholds
_vals = json.load(open(treshold_path))
lv1, lv2 = _vals['lv1'], _vals['lv2']

# for country in countries:
fires = gpd.read_file(fires_file)
fires[fires_col] = pd.to_datetime(fires[fires_col])
fires = fires.to_crs(crs)

month_list = []
ba_list = []
ba_perc_list = []
total_ba = fires['geometry'].area.sum() / 10000
for year in years:
    for month in months:

        monthlyfire = fires[(fires[fires_col].dt.year == year) & (fires[fires_col].dt.month == month)]
        # tot area
        burned_area = monthlyfire['geometry'].area.sum() / 10000        
        perc_ba = int(round((burned_area/total_ba)*100, 0))
        ba_perc_list.append(perc_ba)

        monthly_susc_path = f'{basep}/susc_calabria_{year}_{month}.tif'
        monthlysusc = rio.open(monthly_susc_path)

        # grid = make_grid(2,1)
        susc_class = gtras.categorize_raster(monthlysusc.read(1), 
                                thresholds = [lv1, lv2],
                                nodata = -1)

        high_susc_area = np.where(susc_class == 3, 1, 0).sum()
        tot = np.where(susc_class != 0, 1, 0).sum()
        perc = round((high_susc_area/tot)*100, 2)

        month_list.append(perc)  
        ba_list.append(burned_area) 

        # # add the mean value of spi
        # spi_file =  

arr  = np.array(month_list)

# plot in 1 image
fig, ax = plt.subplots(figsize=[40,10], dpi = 250)
time = [f'{year}-{month}' for year in years for month in months]

ax.plot(time, arr, label = 'v4',
        color = '#9467bd')

# ax.set_xticks(years)
ax.set_xticklabels(time, rotation = 90)

# add bar of burned area 
ax2 = ax.twinx()
ax2.bar(time, ba_list, color = 'brown', alpha = 0.5, edgecolor = 'brown', linewidth = 2, facecolor = 'none')

# add annotateion on top of bars
for year, ba, ba_perc in zip(time, ba_list, ba_perc_list):

    if ba_perc > 0:
        ax2.annotate(f'{ba_perc:.0f} %', xy = (year, ba), xytext = (year, ba), 
                    ha = 'center', va = 'bottom', fontsize = 4, fontweight = 'bold',
                    color = 'Brown')

# color brown for the burned area
ax2.set_ylabel('Burned Area [ha]', color = 'brown', fontsize = 14)
ax.set_ylabel('High-susc extent [%]', fontsize = 14, color = '#9467bd')
ax2.tick_params(axis='y', labelcolor='brown', labelsize = 12)
ax.tick_params(axis='y', labelsize = 12, labelcolor = '#9467bd')

# FORMAT Y AX WITH COMMA
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

ax.legend(loc='upper left')
ax.set_title(f'Calabria 2007-2023 - Extend of high susceptibility w.r.t annual burned area', fontsize = 15, fontweight = 'bold')

fig.savefig(f'{basep}/plot_trends/high_susc_vs_ba.png', dpi = 250, bbox_inches = 'tight')
# extrace back the color used by the lines
# lines = ax.get_lines()
# colors = [line.get_color() for line in lines]

