
import os
from geospatial_tools import geotools as gt
import numpy as np
import rasterio as rio

from home import TILES_DIR, DATAPATH

VS = 'v1'
tiles = os.listdir(TILES_DIR)
tiles = [tile for tile in tiles if os.path.isdir(os.path.join(TILES_DIR, tile))]

years = list(range(2011, 2025))
months = list(range(1, 13))

# check existance
# for tile in tiles:
#     for year in years:
#         for month in months:
#             filepath = f"{TILES_DIR}/{tile}/susceptibility/annual_maps/Annual_susc_{year}_{month}.tif"
            
#             # check existance
#             if not os.path.exists(filepath):
#                 print(f"Missing: {filepath}")
#                 continue

ras = gt.Raster()

from rasterio.windows import Window

def remove_borders(tile, year, month):

    path = os.path.join(TILES_DIR, tile, 'susceptibility', VS, f'{year}_{month}', 'annual_maps', f'Annual_susc_{year}_{month}.tif')
    with rio.open(path) as src:
        width = src.width
        height = src.height

        # Define window to read, removing 10 pixels from each edge
        window = Window(30, 30, width - 60, height - 60)

        # Read the data within the window
        data = src.read(1, window=window)
        profile = src.profile

        # Update the profile with new width, height, and transform
        profile.update({
            'height': data.shape[0],
            'width': data.shape[1],
            'transform': src.window_transform(window)
        })

    # Save the clipped tile (overwrite or to a new path)
    os.remove(path)
    with rio.open(path, 'w', **profile) as dst:
        dst.write(data, 1)


# prepare function to run in parallel per each month 
def merge_susc_tiles(year, month):
    print(f"{year}-{month:02d}...")
    outfile = f'{DATAPATH}/susceptibility/{VS}/susc_{year}_{month}.tif'
    if not os.path.exists(outfile):
        # merge tiles
        files_to_merge = [f"{TILES_DIR}/{tile}/susceptibility/{VS}/{year}_{month}/annual_maps/Annual_susc_{year}_{month}.tif"
                        for tile in tiles]

        out = ras.merge_rasters(outfile, np.nan, 'last', *files_to_merge)

        # fix nan data (nan to -1)
        with rio.open(out) as src:
            arr = src.read(1)
            arr[np.isnan(arr)] = -1
            out_meta = src.meta.copy()
            out_meta.update({
                'compress': 'lzw',
                'tiled': True,
                'blockxsize': 256,
                'blockysize': 256,
            })
            with rio.open(out, 'w', **out_meta) as dst:
                dst.write(arr, 1)


        # with rio.open(outfile) as src:
        #     ras.plot_raster(src)
    else:
        # remove
        os.remove(outfile)

import multiprocessing as mp
tiles = os.listdir(TILES_DIR)
with mp.Pool(25) as pool:
    pool.starmap(remove_borders, [(tile, year, month) for tile in tiles for year in years for month in months])

with mp.Pool(25) as pool:
    pool.starmap(merge_susc_tiles, [(year, month) for year in years for month in months])

#%%  corrent nan to -1

# p = f'{DATAPATH}/susceptibility/{VS}'
# files = os.listdir(p)
# files = [f for f in files if f.endswith('.tif')]

# for file in files:
#     filepath = os.path.join(p, file)
#     with rio.open(filepath) as src:
#         arr = src.read(1)
#         arr[np.isnan(arr)] = -1
#         out_meta = src.meta.copy()
#         out_meta.update({
#             'compress': 'lzw',
#             'tiled': True,
#             'blockxsize': 256,
#             'blockysize': 256,
#         })
#         with rio.open(filepath, 'w', **out_meta) as dst:
#             dst.write(arr, 1)
        




