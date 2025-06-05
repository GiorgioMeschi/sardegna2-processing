

import os
import numpy as np
from geospatial_tools import geotools as gt
import rasterio as rio
import matplotlib.pyplot as plt
from rasterio.mask import mask as riomask
import geopandas as gpd

from home import DATAPATH

#%%
variables = ['P'] #SPI, 'SPEI', 'P', 'Tanomaly', 'T'] # last one is mean T
months_aggregation = [1, 3, 6]
years = list(range(2011, 2025)) #
months = list(range(1, 13)) # 
Raster = gt.Raster()


calabria_path = f'{DATAPATH}/aoi/calabria.geojsonl.json'
calabria = gpd.read_file(calabria_path)
calabria = calabria.to_crs(epsg=4326)
calabria_geom = calabria.geometry.values[0]


#%% clip the raw spi and save it in the proper month folder


for var in variables:
    plot_1m = []
    plot_3m = []
    plot_6m = []
    for aggr in months_aggregation:
        for year in years:
            for month in months:
                
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

                
                # eval the mean value and save the val
                with rio.open(path) as src:
                    out_image, _ = riomask(src, [calabria_geom], crop = True, nodata = -9999)
                # compute mean value excluding -9999
                out_image[out_image == -9999] = np.nan
                _mean = np.nanmean(out_image)
                if aggr == 1:
                    plot_1m.append(_mean)
                elif aggr == 3:
                    plot_3m.append(_mean)
                elif aggr == 6:
                    plot_6m.append(_mean)


    ticks = [f'{year}-{month:02}' for year in years for month in months]

    # plot in a chart with 3 lines
    fig, ax = plt.subplots(figsize=(25, 6), dpi = 200)
    ax.plot(plot_1m, label='1 month', color='blue')
    ax.plot(plot_3m, label='3 month', color='orange')
    ax.plot(plot_6m, label='6 month', color='green')
    ax.set_title(f'{var} - Calabria')
    ax.set_xlabel('Time (months)')
    ax.set_ylabel('SPI')
    ax.legend()


    ax.set_xticks(range(len(ticks)))
    ax.set_xticklabels(ticks, rotation=90, fontsize=7)







