
#%%
import os
import shutil
import pandas as pd

from home import TILES_DIR

tiles = os.listdir(TILES_DIR)
tiles = ['tile_11','tile_22'] # os.listdir(TILES_DIR) # tiles to clip the data on  # 

overwrite = True

for tile in tiles:
    print(tile)

    input_folderpath = os.path.join(TILES_DIR, tile, 'climate')
    output_folderpath = os.path.join(TILES_DIR, tile, 'climate_1m_shift')

    os.makedirs(output_folderpath, exist_ok=True)

    # Get all year_month folders in climate directory
    monthly_folders = [f for f in os.listdir(input_folderpath) if os.path.isdir(os.path.join(input_folderpath, f))]

    for monthly_folder in monthly_folders:

        # put the real month in the next month folder (each month now has month before)
        shifted_date = pd.to_datetime(monthly_folder, format="%Y_%m") + pd.DateOffset(months=1)
        shifted_date_foldername = shifted_date.strftime("%Y_%-m")  # Format as YYYY_M (e.g., 2018_12)
        
        src_folder = os.path.join(input_folderpath, monthly_folder)
        dest_folder = os.path.join(output_folderpath, shifted_date_foldername)

        os.makedirs(dest_folder, exist_ok=True)
        for file in os.listdir(src_folder):
            _in = os.path.join(src_folder, file)
            out = os.path.join(dest_folder, file)
            if not os.path.exists(out) or overwrite:
                #if file contains bilinear in the name:
                if file.endswith(".tif") and 'bilinear' in file:
                    shutil.move(_in, out)

#%% copy 2011_2 to 2022_1 for all the tiles
for tile in tiles:
    print(tile)

    src_folder = f'{TILES_DIR}/{tile}/climate_1m_shift/2011_2'
    dest_folder = f'{TILES_DIR}/{tile}/climate_1m_shift/2011_1'

    os.makedirs(dest_folder, exist_ok=True)
    for file in os.listdir(src_folder):
        _in = os.path.join(src_folder, file)
        out = os.path.join(dest_folder, file)
        if not os.path.exists(out) or overwrite:
            #if file contains bilinear in the name:
            if file.endswith(".tif") and 'bilinear' in file:
                shutil.copy(_in, out)


# %%
