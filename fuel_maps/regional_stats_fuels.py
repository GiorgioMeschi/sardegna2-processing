

import rasterio as rio
import numpy as np
import pandas as pd
from home import DATAPATH

VS = 'v1'

# Define file paths
fuel_files = {
    'June 2025': f'{DATAPATH}/risico/monthly_fuel_maps/fuel12cl_2025_6_spi1-05_spi3-05_spi6-05_spei1-05_spei3-05_spei6-05.tif',
    'June 2024': f'{DATAPATH}/fuel_maps/{VS}/fuel_2024_6.tif',
    'June 2021': f'{DATAPATH}/fuel_maps/{VS}/fuel_2021_6.tif',
}

def get_fuel_class_distribution(fuel_file, classes=range(1, 13)):
    with rio.open(fuel_file) as src:
        arr = src.read(1)
        arr = arr[arr != 0]  # mask nodata
        total = arr.size
        percentages = {}
        for i in classes:
            sum_px = np.where(arr == i, 1, 0).sum() 
            percentages[f'class {i} (%)'] = sum_px / total * 100
    return percentages

# Collect stats
df_dict = {}
for name, path in fuel_files.items():
    df_dict[name] = get_fuel_class_distribution(path)

# Create and format DataFrame
df = pd.DataFrame(df_dict).T
df = df.round(2)

folder = f'{DATAPATH}/fuel_maps/{VS}/regional_stats/june'
os.makedirs(folder, exist_ok=True)
output_file = f'{folder}/fuel_class_distribution_june_sardegna.csv'
df.to_csv(output_file)



