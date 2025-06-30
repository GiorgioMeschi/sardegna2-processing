

#%% imports

import os
import numpy as np
from geospatial_tools import geotools as gt
import rasterio as rio
from rasterio.merge import merge
import geopandas as gpd 
from rasterio.mask import mask as riomask
import multiprocessing as mp
import time
from home import DATAPATH, TILES_DIR

CORES = 60


#%% inputs


variables = ['SPI', 'SPEI'] # , 'P', 'Tanomaly', 'T'] # only spi and spei are used
months_aggregation = [1, 3, 6]
years = list(range(2011, 2025)) #
months = list(range(1, 13)) # 
tiles = os.listdir(TILES_DIR) # tiles to clip the data on  # 
# tiles = ['tile_7'] #, 'tile_14','tile_3', 'tile_4', 'tile_2', 'tile_1'] # os.listdir(TILES_DIR) # tiles to clip the data on  # 

Raster = gt.Raster()

#%% clip the raw spi and save it in the proper month folder


def clip_to_tiles(var, aggr, year, month, tile: str, tile_df: gpd.GeoDataFrame):

    # folderpath changes depending on the variables
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

    elif var == 'P':
        basep = f'/home/drought/drought_share/data/Italy/output/{var}/MCM/{aggr}m/{year}'
        name_cut = f'{var}_{aggr}m_{year}{month:02}'
        allnames = os.listdir(basep)
        name = [name for name in allnames if name.startswith(name_cut)][0]
        path = f'{basep}/{name}'

    elif var == 'Tanomaly':
        basep = f'/home/drought/drought_share/archive/Italy/{var}/DROPS/maps/{year}/{month:02}'
        day = os.listdir(basep)[-1]
        name = f'TANOMALY{aggr}_zscr-DROPS_{year}{month:02}{day}.tif'
        path = f'{basep}/{day}/{name}'

    elif var == 'T':
        name = f'AirT_{aggr}m_DROPS_{year}{month:02}_italy.tif'
        path = f'/home/drought/drought_share/data/Italy/output/T_ANOMALY/DROPS/{aggr}m/{year}/{name}'

    out_folder = os.path.join(TILES_DIR, tile, 'climate', f'{year}_{month}')
    os.makedirs(out_folder, exist_ok=True)
    wgs_file = os.path.join(out_folder, f'{var}_{aggr}m_orig.tif')
    reproj_out_file = os.path.join(out_folder, f'{var}_{aggr}m_bilinear_epsg32632.tif') # out filename

    if not os.path.exists(reproj_out_file):
    # if reproj_out_file == f'{DATAPATH}/ML/tile_2/climate/2012_6/spi_1m_bilinear_epsg3857.tif':

        # clip and reproject
        tile_geom = tile_df[tile_df['id_sorted'] == int(tile[5:])].geometry.values[0]
        # buffer 5 km in degrees
        tile_geom = tile_geom.buffer(0.05)
        
        with rio.open(path) as src:
            out_image, out_transform = riomask(src, [tile_geom], crop = True)
            out_meta = src.meta.copy()
            out_meta.update({
                'height': out_image.shape[1],
                'width': out_image.shape[2],
                'transform': out_transform
            })
            with rio.open(wgs_file, 'w', **out_meta) as dst:
                dst.write(out_image)
        
        # reference_file_wgs = os.path.join(TILES_DIR, tile, 'dem', 'dem_wgs.tif')
        reference_file = os.path.join(TILES_DIR, tile, 'dem', 'dem_20m_3857.tif')
        rename = os.path.join(TILES_DIR, tile, 'dem', 'dem_100m_32632.tif')
        if not os.path.exists(reference_file):
            reference_file = rename
        else:
            os.rename(reference_file, rename)
            reference_file = rename  # Use the renamed file for reprojection
        with rio.open(reference_file) as ref:
            bounds = ref.bounds  # Extract bounds (left, bottom, right, top)
            xres = ref.transform[0]  # Pixel width
            yres = ref.transform[4]  # Pixel height
            working_crs = 'EPSG:32632'  # Target CRS

        # Use gdalwarp to reproject and match the bounds and resolution of the reference file
        interpolation = 'bilinear'  # Interpolation method
        os.system(
            f'gdalwarp -t_srs {working_crs} -te {bounds.left} {bounds.bottom} {bounds.right} {bounds.top} '
            f'-tr {xres} {yres} -r {interpolation} -of GTiff '
            f'-co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=256 -co BLOCKYSIZE=256 '
            f'{wgs_file} {reproj_out_file}'
        )

        time.sleep(2)
        os.remove(wgs_file)

    else:
        print(f'already exists: {reproj_out_file} ')

with mp.Pool(CORES) as p:
    # open the tiles already in WGS 84
    tile_df = gpd.read_file(f'{DATAPATH}/aoi/grid_wgs_clean.geojsonl.json', driver='GeoJSONSeq')
    tile_df = tile_df.to_crs('EPSG:4326') #proj of the input drought
    # use all the cores to clip the data
    p.starmap(clip_to_tiles, [(var, aggr, year, month, tile, tile_df) for var in variables
                                                                for aggr in months_aggregation
                                                                for year in years
                                                                for month in months
                                                                for tile in tiles
                                                               ])


#%% open all the files to spot corruption due to gdal warp

# years = list(range(2011, 2025)) 
# months = list(range(1, 13)) # 
# tiles = os.listdir(TILES_DIR) # tiles to clip the data on  # 


folder = 'climate_1m_shift'

def check(tile, var, aggr, year, month):
    # folderpath changes depending on the variables
    file = os.path.join(TILES_DIR, tile, folder, f'{year}_{month}', f'{var}_{aggr}m_bilinear_epsg32632.tif')
    if os.path.exists(file):
        try:
            with rio.open(file) as src:
                data = src.read(1)
        except Exception as e:
            print(f'Corrupted file: {file} \n {e}')
            # os.remove(file)

with mp.Pool(80) as p:
    p.starmap(check, [(tile, var, aggr, year, month,) for tile in tiles for var in variables
                                                                for aggr in months_aggregation
                                                                for year in years
                                                                for month in months
                                                                
                                                               ])


#%%



