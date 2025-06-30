
import json
import os
import numpy as np

from geospatial_tools import FF_tools as ff

from home import DATAPATH
vs = 'v1'

fft = ff.FireTools()

years = list(range(2011, 2024))
months = list(range(1, 13))
allyears = [f"{year}_{month}" for year in years for month in months]

settings = dict(
    countries = ['sardegna2'],
    years = allyears,
    folder_before_country = '/share/drought/projects',
    folder_after_country = f'data/susceptibility/{vs}',
    fires_paths = 'data/raw/burned_area/incendi_dpc_2007_2023_sardegna_32632.shp',
    name_susc_without_year = 'susc_',
    year_fires_colname = 'date_iso',
    crs = 'epsg:32632',
    year_in_name = True,
    allow_plot = False
) 

data = fft.eval_annual_susc_thresholds(**settings)

# redefine tr for monthly 
ba_list = data[3]
high_vals_years = data[1]
low_vals_years = data[2]

avg_ba = np.mean(ba_list)
mask_over_treashold = [1 if ba > avg_ba else 0 for ba in ba_list]

# select values from high and  low vals
mask = np.array(mask_over_treashold)
high_val_over_tr =  high_vals_years[mask == 1]
low_val_over_tr =  low_vals_years[mask == 1]
lv2 = np.mean(high_val_over_tr)
lv1 = np.mean(low_val_over_tr)

#std
# lv1_std = np.std(low_val_over_tr)
# lv2_std = np.std(high_val_over_tr)

# save
thresholds = dict(lv1=lv1, lv2=lv2)
basep = f'{DATAPATH}/susceptibility/{vs}/thresholds'
os.makedirs(basep, exist_ok=True)
with open(f'{basep}/thresholds.json', 'w') as f:
    json.dump(thresholds, f, indent=4)

