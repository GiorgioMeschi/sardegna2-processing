

#%%

import os
import numpy as np
from geospatial_tools import geotools as gt
import rasterio as rio
import geopandas as gpd 
import pandas as pd
import multiprocessing as mp
from rasterio.mask import mask as riomask
from home import DATAPATH

#%% create tif file of vegetation

#extract the codes used in ML
in_file = f'{DATAPATH}/raw/vegetation/vegetation_ml_32632.tif'
reference_file = f'{DATAPATH}/raw/dem/dem_ispra_100m_32632_v2.tif'
tiles_file = f'{DATAPATH}/aoi/grid_wgs_clean.geojsonl.json'
out_folder = f'{DATAPATH}/ML'
crs = 'EPSG:32632'

# clip veg per tile 
with rio.open(in_file) as veg:
    tiles = gpd.read_file(tiles_file, driver='GeoJSONseq')
    tiles = tiles.to_crs(crs)
    for i, tile in tiles.iterrows():
        print(f'Processing tile {tile["id_sorted"]}')
        # buffer tile of 5 km 
        tile['geometry'] = tile['geometry'].buffer(5000)
        # clip usin rasterio
        tile_geom = tile['geometry']
        _tile, transform = riomask(veg, [tile_geom], crop=True)
        # save clipped dem
        path = f'{out_folder}/tile_{tile["id_sorted"]}/veg'
        os.makedirs(path, exist_ok=True)
        veg_file = f'{path}/veg_100m_32632.tif'
        meta_updated = veg.meta.copy()
        meta_updated.update({
            'transform': transform,
            'height': _tile.shape[1],
            'width': _tile.shape[2],
            # compression
            'compress': 'lzw',
            'tiled': True,
        })
        with rio.open(veg_file, 'w', **meta_updated) as dst:
            dst.write(_tile)
        
        # os.remove(f'{path}/veg_100m_32632.tif')


#%% view one tile veg

veg_file = f'{DATAPATH}/ML/tile_1/veg/veg_100m_32632.tif'
gt.Raster().plot_raster(rio.open(veg_file))

#%%













