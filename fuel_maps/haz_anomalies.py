

import geopandas as gpd
from geospatial_tools import geotools as gt
import os
import numpy as np
import pandas as pd

Raster = gt.Raster()

# input files 
datapath = '/home/sadc/share/project/calabria/data'
haz_static_file = f'{datapath}/fuel_maps/static/FUEL_MAP.tif'
haz_monthly_folder = f'{datapath}/fuel_maps/v4'
ba_file = f'{datapath}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'

# settings
years = list(range(2007, 2025))
months = list(range(1, 13))
yearmonths = [f'{year}_{month}' for year in years for month in months]

# initial data
static_fuel = Raster.read_1band(haz_static_file)
h3_static = np.where(static_fuel == 3, 1, 0).sum()
h6_static = np.where(static_fuel == 6, 1, 0).sum()
h9_static = np.where(static_fuel == 9, 1, 0).sum()
h12_static = np.where(static_fuel == 12, 1, 0).sum()
static_extents = [h3_static, h6_static, h9_static, h12_static]

ba = gpd.read_file(ba_file)
ba['date_iso'] = pd.to_datetime(ba['date_iso'])

# prepare out lists
areas = []
h3, h6, h9, h12 = [], [], [], []
lists = [h3, h6, h9, h12]

anomaly = lambda montly, static: ((montly / static) - 1) * 100

# eval monthly anomalies
cls = [3,6,9,12]
for month in yearmonths:
    print(month)
    fuel_map_filepath = f'{haz_monthly_folder}/fuel_calabria_{month}.tif'
    fuel = Raster.read_1band(fuel_map_filepath)
    y = int(month.split('_')[0])
    m = int(month.split('_')[1])
    ba_year = ba[ba['date_iso'].dt.year == y]
    ba_month = ba_year[ba_year['date_iso'].dt.month == m]
    area = ba_month.area_ha.sum()
    areas.append(area)
    # eval anomalies and appned in the class list
    for cl, proper_list, static_extent in zip(cls, lists, static_extents):
        h_month = np.where(fuel == cl, 1, 0).sum()
        perc_anomaly = anomaly(h_month, static_extent) # percentage of anomaly, ex: 100% means twice the value
        proper_list.append(perc_anomaly)
        
df = pd.DataFrame({
    'year_month': yearmonths,
    'area_ha': areas,
    'h3': h3,
    'h6': h6,
    'h9': h9,
    'h12': h12
})   


# save
outpath = f'{haz_monthly_folder}/anomalies/anomalies.csv'
os.makedirs(os.path.dirname(outpath), exist_ok=True)
df.to_csv(outpath, index=False)

#%% fancy plot 

import matplotlib.pyplot as plt

df = pd.read_csv(outpath)

df['date'] = pd.to_datetime(df['year_month'].str.replace('_', '-'))
base_vals = [h3_static, h6_static, h9_static, h12_static]
base_vals = [i * 0.04 for i in base_vals] # convert to ha

for cl, color, base_val in zip(cls, ['green', 'yellow', 'violet', 'red'], base_vals):

    fig, ax = plt.subplots(figsize=(30, 8), dpi = 200)

    # Curve delle anomalie
    ax.plot(df['date'], df[f'h{cl}'], label=f'Anomalia Classe {cl}', linewidth=1.2, color = color)
    # plt.plot(df['date'], df['h6'], label='Anomalia Classe 6', linewidth=1.2, marker='s')
    # plt.plot(df['date'], df['h9'], label='Anomalia Classe 9', linewidth=1.2, marker='^')
    # plt.plot(df['date'], df['h12'], label='Anomalia Classe 12', linewidth=1.2, marker='d')

    # Secondo asse y per l'area bruciata
    # ax = plt.gca()
    ax2 = ax.twinx()
    ax2.plot(df['date'], df['area_ha'], color='black', label='Area Bruciata (ha)', linewidth=2, linestyle='--')

    # Stile e labels
    ax.set_title(f"Trend delle Anomalie della fuel map e Aree Bruciate - CLASSE {cl}", fontsize=16)
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel("Anomalia (%)", fontsize=12)
    ax2.set_ylabel("Area Bruciata (ha)", fontsize=12)
    ax.set_xticks(df['date'])
    ax.set_xticklabels(df['date'].dt.strftime('%Y-%m'), rotation=90, fontsize=8)
    ax.set_xlim(xmax= df['date'].max())

    ax2.set_yticks(np.arange(-100, df['area_ha'].max() * 1.1, 2000))
    ax2.set_yticklabels(np.arange(-100, df['area_ha'].max() * 1.1, 2000), fontsize=8)


    ax.set_ylim(-100, 100)
    ax2.set_ylim(-100, df['area_ha'].max() * 1.1)


    # put horizzontal line at 0
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')

    # y label of 0 change with another number
    ax.set_yticks(np.arange(-100, 600, 100))
    y_ticks = [ str(i) for i in np.arange(-100, 600, 100) ]
    y_ticks[1] = f'{int(base_val)} ha'
    ax.set_yticklabels(y_ticks, fontsize=8)


    # Legenda combinata
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    plt.tight_layout()
    #save
    fig.savefig(f'{haz_monthly_folder}/anomalies/anomalies_plot_{cl}.png', dpi=200, bbox_inches='tight')
    

