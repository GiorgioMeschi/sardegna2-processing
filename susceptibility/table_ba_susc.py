
from geospatial_tools import geotools as geotools
from home import DATAPATH
import geopandas as gpd
import pandas as pd
import rasterio as rio
import os
import json

gtras = geotools.Raster()


susc_threshold_path = f'{DATAPATH}/susceptibility/v2/thresholds/thresholds.json'

_vals = json.load(open(susc_threshold_path))
threshold1, threshold2 = _vals['lv1'], _vals['lv2']

firepath = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
crs = 'EPSG:3857'
fires_col = 'date_iso'
vs = 'v2'

f = gpd.read_file(firepath).to_crs(crs)
f[fires_col] = pd.to_datetime(f[fires_col])

years = list(range(2011, 2024))
months = list(range(1, 13)) # all months 

# loop over the years
df = pd.DataFrame(index = [1,2,3])
for year in years:

    for month in months: # if annual put months = [None]

        # fires = gpd.read_file(fires_file)
        # # filter only from: 2008 
        # fires[fires_col] = pd.to_datetime(fires[fires_col])
        # fires = fires.to_crs(crs)

        annualfire = f[(f[fires_col].dt.year == year)]
        monthlyfire = annualfire[(annualfire[fires_col].dt.month == month)] 
        susc_path = f'{DATAPATH}/susceptibility/{vs}/susc_calabria_{year}_{month}.tif'
        monthlysusc = rio.open(susc_path)

        if len(monthlyfire):

            susc_class = gtras.categorize_raster(monthlysusc.read(1), 
                                    thresholds = [threshold1, threshold2],
                                    nodata = -1)

            stats = gtras.raster_stats_in_polydiss(susc_class, monthlyfire, reference_file = susc_path)
            # conver column class in index
            stats.index = stats['class']
            stats = stats.drop(columns = 'class')

            # concat adding new column of df
            label = f'{year}_{month}' 
            df = pd.concat([df, stats], axis = 1)
            # rename the new columns
            df = df.rename(columns = {df.columns[-1]: label })

            print(f'done {label}')
        
            
    

# fillna
df = df.fillna(0)
df = df.astype(int)
# get overall df sum
tot = df.sum(axis = 1).sum(axis = 0)
df_perc = df/tot*100
df_perc = df_perc.round(2) 

# # add col 2007 to df
# df = pd.concat([pd.DataFrame([1070, 10800, 105571], index = [1,2,3]), df], axis = 1)
# # rename col 0
# df = df.rename(columns = {0: '2007'})

# add col total per row
df_perc['Total'] = df.sum(axis = 1) / tot * 100
df_perc['Total'] = df_perc['Total'].round(1)

# save 
out_folder = f'{DATAPATH}/ba_susc_table/{vs}'
os.makedirs(out_folder, exist_ok = True)
df.to_csv(f'{out_folder}/table_ba_susc.csv')
df_perc.to_csv(f'{out_folder}/table_ba_susc_perc.csv')


