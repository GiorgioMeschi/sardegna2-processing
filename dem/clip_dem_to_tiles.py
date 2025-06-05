
'''
take calabria  dem at 20 m from Ispra, clip and save per 5km buffered tile
'''
#%%

import rasterio as rio 
from geospatial_tools import geotools as gt
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.mask import mask as riomask
import os
from home import DATAPATH

#%%
raster = gt.Raster()
dem_file = f'{DATAPATH}/raw/dem/dem_calabria_20m_3857.tif'
tiles_file = f'{DATAPATH}/aoi/grid_clean.geojsonl.json'
working_crs = 'EPSG:3857' #pseudo mercator (metric) - same as input dem (dem.crs)
out_folder = f'{DATAPATH}/ML'

# clip dem per tile 
with rio.open(dem_file) as dem:
    tiles = gpd.read_file(tiles_file, driver='GeoJSONseq')
    tiles = tiles.to_crs(working_crs)
    # save tiles reprojected
    tiles.to_file(tiles_file, driver='GeoJSON')
    for i, tile in tiles.iterrows():
        print(f'Processing tile {tile["id_sorted"]}')
        # buffer tile of 5 km in degree
        tile['geometry'] = tile['geometry'].buffer(5000)
        # clip usin rasterio
        tile_geom = tile['geometry']
        dem_tile, transform = riomask(dem, [tile_geom], crop=True)
        # save clipped dem
        path = f'{out_folder}/tile_{tile["id_sorted"]}/dem'
        os.makedirs(path, exist_ok=True)
        dem_file = f'{path}/dem_20m_3857.tif'
        meta_updated = dem.meta.copy()
        meta_updated.update({
            'transform': transform,
            'height': dem_tile.shape[1],
            'width': dem_tile.shape[2],
            # compression
            'compress': 'lzw',
            'tiled': True,
        })
        with rio.open(dem_file, 'w', **meta_updated) as dst:
            dst.write(dem_tile)
        
        
        
#%% open a dem tile

dem_file = f'{DATAPATH}/ML/tile_1/dem/dem_20m_3857.tif'
gt.Raster().plot_raster(rio.open(dem_file))

#%%

