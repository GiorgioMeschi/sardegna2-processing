
#%%

from geospatial_tools import geotools as gt
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from home import DATAPATH, DATAPATH

#%%

ba_file = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_calabria_3857.shp'
tiles_file = f'{DATAPATH}/aoi/grid_clean.geojsonl.json'
working_crs = 'EPSG:3857' #pseudo mercator (metric) - same as input dem (dem.crs)
out_folder = f'{DATAPATH}/ML'

# clip dem per tile 
tiles = gpd.read_file(tiles_file, driver='GeoJSONseq')
ba = gpd.read_file(ba_file)
ba = ba.to_crs(working_crs)

for i, tile in tiles.iterrows():
    print(f'Processing tile {tile["id_sorted"]}')
    # buffer tile of 5 km in degree
    tile['geometry'] = tile['geometry'].buffer(5000)
    #clip areas 
    ba_tile = gpd.clip(ba, tile['geometry'])
    # remove fires under 5 ha
    ba_tile = ba_tile[ba_tile['area_ha'] > 5] # use the ha aready computed with precise crs
    # save clipped raster   
    outpath = f'{out_folder}/tile_{tile["id_sorted"]}/fires'
    out_file = f'{outpath}/fires_2007_2023_epsg3857.shp'
    os.makedirs(outpath, exist_ok=True)
    ba_tile.to_file(out_file, driver='ESRI Shapefile')
    if i == 0 or i == 1 or i == 2:
        fig, ax = plt.subplots()
        ba_tile.plot(ax=ax, facecolor='none', edgecolor='black')
        # off axis and title
        ax.set_axis_off()
        ax.set_title(f'Tile {tile["id_sorted"]}')
    
    
#%%