#%%

from geospatial_tools import FF_tools
from home import DATAPATH
from matplotlib import pyplot as plt
import os
ft = FF_tools.FireTools()

#%%



def plot_fuel(fires, fire_col, out_folder, _crs, _year, _month):

    hazard_file = f'{DATAPATH}/fuel_maps/v1/fuel_{_year}_{_month}.tif'
    outputlike = f'{out_folder}/haz_plot_{_year}{_month}.png'

    if not os.path.exists(outputlike):
        settings = dict(
            fires_file=         fires,
            fires_col=          fire_col,
            crs=                _crs,
            hazard_path=         hazard_file,
            xboxmin_hist=       0.1,
            yboxmin_hist=       0.1,
            xboxmin_pie=        0.1,
            yboxmin_pie=        0.7,
            out_folder=         out_folder,
            year=               _year,
            month=              _month,
            season=             False,
            haz_nodata=         0,
            pixel_to_ha_factor= 1,
            allow_hist=         True,
            allow_pie=          True,
            allow_fires=        True,
        )
        
        ft.plot_haz_with_bars(**settings)
        plt.close('all')

import multiprocessing as mp

if __name__ == '__main__':
    years = list(range(2011, 2025))
    months = list(range(1, 13))
    crs = 'EPSG:32632'
    fires_file = f'{DATAPATH}/raw/burned_area/incendi_dpc_2007_2023_sardegna_32632.shp'
    fire_col = 'date_iso'
    out = f'{DATAPATH}/fuel_maps/v1/PNG'

    with mp.Pool(processes=20) as pool:
        pool.starmap(
            plot_fuel,
            [
                (   
                    fires_file,
                    fire_col,
                    out,
                    crs,
                    year,
                    month
                )
                for year in years
                for month in months
            ]
        )

#%%

import os
from geospatial_tools import geotools as gt

#images
Img = gt.Imtools()

out_folder = f'{out}/MERGED'
years = list(range(2011, 2025))
months = list(range(1, 13))

os.makedirs(out_folder, exist_ok=True)

yearmonths = [f"{year}{month}" for year in years for month in months]
year_filenames = [f'haz_plot_{yrm}' for yrm in yearmonths]
year_files = [f"{out}/{filename}.png" for filename in year_filenames]

fig = Img.merge_images(year_files, ncol=12, nrow=14)
# save image (Image object)
fig.save(f"{out_folder}/fuel_plot_2011-2024.png")



#%%
