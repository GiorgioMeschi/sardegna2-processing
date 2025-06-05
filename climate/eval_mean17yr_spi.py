
import os
import rasterio as rio
import multiprocessing as mp
from geospatial_tools import geotools as gt
import numpy as np
from home import DATAPATH, TILES_DIR
ras = gt.Raster()

#%%
tiles = os.listdir(TILES_DIR)

aggrs = [1, 3, 6]

# for aggr in aggrs:
#     for tile in tiles:
def compute_average_spi(var, tile, aggr):
    tile_path = os.path.join(TILES_DIR, tile)
    idx = 0
    print(f'tile {tile} for SPI {aggr} months')
    for year in range(2011, 2025):
        for month in range(1, 13):
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

            #open and add 
            arr = rio.open(path).read(1)
            if idx == 0:
                arr_sum = arr
            else:
                arr_sum += arr
            idx += 1
    #divide by idx
    arr_sum /= idx
    #save the result
    folder = f'{DATAPATH}/{var}_aggr/{tile}'
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f'{var}_{aggr}m_2011-2024_bilinear_epsg3857.tif')
    ras.save_raster_as(arr_sum, filepath, path, clip_extent=True)

with mp.Pool(25) as pool:
    _vars = ['SPI', 'SPEI']
    pool.starmap(compute_average_spi, [(var, tile, aggr) for var in _vars for tile in tiles for aggr in aggrs])

#%% merge tiles

_vars = ['SPI', 'SPEI']
for var in _vars:
    basep = f'{DATAPATH}/{var}_aggr'
    for aggr in aggrs:
        spi_tiles = [f'{basep}/{tile}/{var}_{aggr}m_2011-2024_bilinear_epsg3857.tif' for tile in tiles]
        # merge
        out_fp = f'{basep}/{var}_{aggr}m_2011-2024_bilinear_epsg3857.tif'
        ras.merge_rasters(out_fp, np.nan, 'first', *spi_tiles)

#%% repr as dem



reference = f"{DATAPATH}/raw/dem/dem_calabria_20m_3857.tif"
_vars = ['SPI', 'SPEI']
for var in _vars:
    basep = f'{DATAPATH}/{var}_aggr'
    for aggr in aggrs:
        file = f'{basep}/{var}_{aggr}m_2011-2024_bilinear_epsg3857.tif'
        ras.save_raster_as(
            rio.open(file).read(1), 
            file.replace('.tif', '_repr.tif'), 
            reference, 
            dtype='float32',
        )





