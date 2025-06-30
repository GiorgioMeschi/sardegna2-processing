

from geospatial_tools import geotools as gt

from home import DATAPATH
import os

ras = gt.Raster()

years = list(range(2011, 2025))
months = list(range(1, 13))
yearmonths = [f'{year}_{month}' for year in years for month in months]
dem_file = f'{DATAPATH}/raw/dem/dem_ispra_100m_32632_v2.tif'
basep = f'{DATAPATH}/susceptibility/v1'
for yr in yearmonths:
    path = f'{basep}/susc_{yr}.tif'
    outpath = f'{basep}/reproj_susc_{yr}.tif'
    ras.reproject_raster_as_v2(path, outpath, dem_file, 'EPSG:32632', 'EPSG:32632', 'nearest')
    os.rename(path, f'{basep}/susc_{yr}_raw.tif')
    os.rename(outpath, path)





