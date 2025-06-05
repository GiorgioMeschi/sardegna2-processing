

#%%

from geospatial_tools import geotools as gt
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import rasterio as rio
from rasterio.mask import mask as riomask
import numpy as np
import pandas as pd
import json
import multiprocessing as mp

#%% for each  class rasterize it and evaluate the bunrned %


ras = gt.Raster()

veg_path = '/home/sadc/share/project/calabria/data/raw/vegetation/carta natura.shp'
fires_path = '/home/sadc/share/project/calabria/data/raw/burned_area/fires_dpc_2007_2023.shp'
dem_path = '/home/sadc/share/project/calabria/data/raw/dem/dem_calabria_20m_3857.tif'
legend_file = '/home/sadc/share/project/calabria/data/raw/vegetation/legenda_carta_natura.json'

veg = gpd.read_file(veg_path)
veg = veg.to_crs('EPSG:3857') 
namecol = 'COD_ISPRA' #cal name of classes (description is not present, look in local in a pdf)
legend = json.load(open(legend_file))

fires = gpd.read_file(fires_path)
fires = fires.to_crs('EPSG:3857')

hectars_1_pixel = 0.04 # given pixel of size 20m x 20m

# define a function that iterats toward classes in parallel
def statistics(cl: str):

    out = '/home/sadc/share/project/calabria/data/raw/vegetation/temp'
    out_filepath = f'{out}/stats_{cl}.csv'
    if not os.path.exists(out_filepath):
        print(f'Processing class {cl}')
        veg_cl = veg[veg[namecol] == cl]
        array = ras.rasterize_gdf_as(veg_cl, dem_path, all_touched = False)
        total_extent_ha = np.where(array == 1, 1, 0).sum() * hectars_1_pixel
        # save temp array for clipping it
        out_temp = f'/home/sadc/share/project/calabria/data/raw/vegetation/{cl}.tif'
        temporary_raster = ras.save_raster_as(array, out_temp, dem_path )     
        del array                                   
        #how much is burned
        with rio.open(temporary_raster) as src:
            burned_area_arr, _ = riomask(src, fires.geometry, crop=False)
        os.remove(out_temp)
        burned_area_ha = np.where(burned_area_arr == 1, 1, 0).sum() * hectars_1_pixel
        del burned_area_arr
        burned_percent = burned_area_ha / total_extent_ha * 100
        # put in df and save as csv
        try:
            legend_name = legend[cl]
        except KeyError:
            legend_name = 'UNKNOWN'
        stats = {
                'class': cl, 
                'description': legend_name,
                'total_extent_ha': int(total_extent_ha), 
                'burned_area_ha': int(burned_area_ha), 
                'burned_percent': round(burned_percent,1)}
        
        stats_df = pd.DataFrame(stats, index=[0])
        os.makedirs(out, exist_ok=True)
        stats_df.to_csv(out_filepath)

with mp.Pool(10) as p:
    classes = veg[namecol].unique()
    p.map(statistics, classes)


#%% after the run concat the files

folder = '/home/sadc/share/project/calabria/data/raw/vegetation/temp'
filenames = os.listdir(folder)

csvs = list()
for filename in filenames:
    path = os.path.join(folder, filename)
    f = pd.read_csv(path, index_col=0)
    csvs.append(f)

print(len(classes))
print(len(csvs))

# concat
f = pd.concat(csvs).reset_index(drop=True)

# sort by percentage
f = f.sort_values('burned_percent', ascending=False)
# set index the class code
f = f.set_index('class')

f.loc['41.D', 'description'] = 'Boschi a Populus tremula'

unknokn_codes = list(f[f['description'] == 'UNKNOWN'].index)
# manually find the legend
true_names = ['Ginestreti a Spartium Junceum',
              'Praterie ad Arundo plinii',
              'Steppe di alte erbe mediterranee a Hyparrhenia hirta',
              'Steppe di alte erbe mediterranee a Lygeum spartum',
              'Boschi e boscaglie ripariali di specie alloctone invasive',
              'Garighe termo e mesomediterranee',
              'Ghiaioni carbonatici macrotermi della penisola italiana e delle isole tirreniche',
              'Boschi e boscaglie di latifoglie alloctone o fuori dal loro areale',
              'Aree invase da Opuntia sp. pl.',
              'Roveti',
              'Boschi e boscaglie di latifoglie alloctone o fuori dal loro areale - Robinieti',
              'Boschi a Alnus cordata',
              'Piantagioni di latifoglie',
              'Cave dismesse e depositi detritici di risulta',
              'Boschi e boscaglie di latifoglie alloctone o fuori dal loro areale -Impianti e aree invase da Acacia sp. pl.',
              'Rimboschimenti di Abies alba'
              ]

for code, name in zip(unknokn_codes, true_names):
    f.loc[code, 'description'] = name

f.to_csv('/home/sadc/share/project/calabria/data/raw/vegetation/stats.csv')

import shutil
shutil.rmtree(folder)

#%% introduce the 1st level category and save it again

f = pd.read_csv('/home/sadc/share/project/calabria/data/raw/vegetation/stats.csv', index_col=0)

# create a columns with a first digit of the index
f['category'] = f.index.str[0]

# sort by category and then percentage 
f2 = f.sort_values(['category', 'burned_percent'], ascending=[True, False])

f2.to_csv('/home/sadc/share/project/calabria/data/raw/vegetation/stats_v2.csv')
#%%






