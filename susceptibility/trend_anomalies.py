



import os
import geopandas as gpd
import rasterio as rio
import numpy as np
from geospatial_tools import geotools as gt
import matplotlib.pyplot as plt
import pandas as pd
from home import DATAPATH
import json
Ras = gt.Raster()

static_map_file = f'{DATAPATH}/susceptibility/static_v2/susc_classified/susc_3classes.tif'
monthly_folder = f'{DATAPATH}/susceptibility/v2'
outfolder = f'{DATAPATH}/susceptibility/v2/PNG/trend_anomalies'
tr = f'{DATAPATH}/susceptibility/v2/thresholds/thresholds.json'
os.makedirs(outfolder, exist_ok=True)
high_tr = json.load(open(tr))['lv2']
static_arr = Ras.read_1band(static_map_file)
static_arr_cl3 = np.where(static_arr == 3, 1, 0)
static_cl3_extent = static_arr_cl3.sum()

years = list(range(2011, 2024))
months = list(range(1, 13))
yearmonths = [f'{year}_{month}' for year in years for month in months]

anomalis = []
for month in yearmonths:
    print(month)
    filepath = os.path.join(monthly_folder, f'susc_calabria_{month}.tif')
    # compute array of anomalies
    with rio.open(filepath) as month_ras:
        arr_cl3 = month_ras.read(1)
        arr_cl3 = np.where(arr_cl3 >= high_tr, 1, 0)  # convert to binary for class 3
        # arr_cl3 = np.where(arr_cl3 == 3, 1, 0)
        dynamic_cl3_extent = arr_cl3.sum()
        anomaly = ((dynamic_cl3_extent / static_cl3_extent) - 1) * 100
        anomalis.append(anomaly)


# trend burned area 
fires_file = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
fires = gpd.read_file(fires_file)
fires['date_iso'] = pd.to_datetime(fires['date_iso'])
fires = fires.to_crs('EPSG:32632')
# avg_ba = fires.area_ha.mean()
area_months = list()
for year in years:
    for month in months:
        ba_year = fires[fires['date_iso'].dt.year == year]
        ba_month = ba_year[ba_year['date_iso'].dt.month == month]
        area = ba_month.area_ha.sum()
        area_months.append(area)


# eval mean of months
mean_monthly_ba = np.mean(area_months)
std = np.std(area_months)
# eval anomalies
ba_anomaly = lambda area, avg_ba: ((area / avg_ba) - 1) * 100
# ba_anomaly = lambda area, avg_ba, ba_std: (area - avg_ba) / ba_std  # z score
ba_anomalies = [ba_anomaly(area, mean_monthly_ba) for area in area_months]


# plot
fig, ax = plt.subplots(figsize=(30, 8), dpi = 200)
ax.plot(yearmonths, anomalis, marker='o', label = 'Monthly susc anomaly', color = 'red')
ax.set_title('Anomalies of high susceptibility class for dynamic maps w.r.t the baseline static map')
ax.set_xticklabels(yearmonths, rotation=90, fontsize=8)
ax.axhline(0, color='gray', linewidth=0.5, linestyle='--', label='Baseline')
ax.set_ylabel('Anomaly [%]')
# add on second y the ba abnomalies
ax2 = ax.twinx()
ax2.plot(yearmonths, ba_anomalies, marker='o', label = 'Burned area anomaly', color = 'blue')
ax2.set_ylabel('Anomaly [%]')
ax2.tick_params(axis='y', labelcolor='blue')
# align the 0 with the 2 axis
y1_min, y1_max = min(anomalis), max(anomalis)
y2_min, y2_max = min(ba_anomalies), max(ba_anomalies)

# Calculate limits that keep 0 in same relative position
y1_range = max(abs(y1_min), abs(y1_max))
y2_range = max(abs(y2_min), abs(y2_max))

# Set symmetrical limits around zero for both axes
ax.set_ylim(-y1_range, y1_range)
ax2.set_ylim(-y2_range, y2_range)

lines_1, labels_1 = ax.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
plt.tight_layout()

# save
fig.savefig(f'{outfolder}/trend_anomalies.png', dpi=200, bbox_inches='tight')


       




