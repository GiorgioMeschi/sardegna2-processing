

import geopandas as gpd
import pandas as pd
# import rio and mask
import rasterio as rio
from rasterio.mask import mask as rio_mask
import matplotlib.pyplot as plt

#%% checks susc vals distribution over fires of test year

susc_1_file = '/home/sadc/share/project/calabria/data/susceptibility/v2_15samples/susc_calabria_2024_7.tif'
susc_2_file = '/home/sadc/share/project/calabria/data/susceptibility/v3/susc_calabria_2024_7.tif'
fires_file = '/home/sadc/share/project/calabria/data/raw/burned_area/2024_effis/8881923896a746789b58a3f40b59645f.shp'

fires = gpd.read_file(fires_file)
fires['finaldate'] = pd.to_datetime(fires['finaldate'])
fires24 = fires[fires['finaldate'].dt.year == 2024]
fires24_7 = fires24[fires24['finaldate'].dt.month == 7]
# crs 3857
fires24_7 = fires24_7.to_crs(3857)


for susc_file, title in zip([susc_1_file, susc_2_file], ['2024-7 100trees 15depth', '2024-7 100trees 20depth']):
    with rio.open(susc_file) as src:
        susc_clip, _ = rio_mask(src, fires24_7.geometry)
        # remove -1 and flatten
        susc_flat = susc_clip.flatten()
        del susc_clip
        susc_flat = susc_flat[susc_flat != -1]
        # print hist
        fig, ax = plt.subplots()
        ax.hist(susc_flat, bins=100)
        ax.set_title(title)

# plot fires over susc
import numpy as np
fig, ax = plt.subplots(figsize = (7,10), dpi = 300)
# plot fires boudanries
fires24_7.boundary.plot(ax=ax, color='black', linewidth=0.5)
# plot susc
with rio.open(susc_1_file) as src:
    susc_arr = src.read(1)
    #-1 in nan
    susc_arr[susc_arr == -1] = np.nan
    #plot with rio show with colorbar
    rio.plot.show(src, ax=ax, cmap='seismic', alpha=0.5)
    # add colorbar
    
    # ax.imshow(susc_arr, cmap='viridis', alpha=0.5)


#%% create a combined plot of susc, fires, and vegetations statistics v1

import rasterio as rio
from rasterio.mask import mask as rio_mask
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

veg_tiff_path = '/home/sadc/share/project/calabria/data/raw/vegetation/vegetation_ml.tif'
susc_1_file = '/home/sadc/share/project/calabria/data/susceptibility/v4/susc_calabria_2024_7.tif'

# Clip vegetation map over fire polygons
with rio.open(veg_tiff_path) as veg_src:
    veg_clip, veg_transform = rio_mask(veg_src, fires24_7.geometry)
    veg_array = veg_clip[0]
    veg_nodata = veg_src.nodata
    veg_res = veg_src.res[0] * veg_src.res[1]  # resolution in map units squared (e.g. m²)

# Clip susceptibility file 1 over same fire polygons
with rio.open(susc_1_file) as susc_src:
    susc_clip, _ = rio_mask(susc_src, fires24_7.geometry)
    susc_array = susc_clip[0]
    susc_nodata = susc_src.nodata

# Mask nodata
mask_valid = (veg_array != 0) & (veg_array != veg_nodata) & (susc_array != susc_nodata) & (susc_array != -1)

veg_valid = veg_array[mask_valid]
susc_valid = susc_array[mask_valid]

# Compute burned area per vegetation class
veg_classes, veg_counts = np.unique(veg_valid, return_counts=True)
burned_area_per_class = veg_counts * veg_res  # assuming area units are square meters
# hectares
burned_area_per_class /= 10000  # convert to hectares

# Compute mean susceptibility per vegetation class
df = pd.DataFrame({'veg': veg_valid, 'susc': susc_valid})
susc_mean_per_class = df.groupby('veg')['susc'].mean().reindex(veg_classes)

# Plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart: burned area
bar = ax1.bar(veg_classes, burned_area_per_class, color='tab:green', alpha=0.6, label='Burned Area')
ax1.set_ylabel('Burned Area (ha)', color='tab:green')
# ax1.set_xlabel('Vegetation Class')
ax1.tick_params(axis='y', labelcolor='tab:green')

# Line plot: mean susceptibility
ax2 = ax1.twinx()
ax2.plot(veg_classes, susc_mean_per_class.values, color='tab:red', marker='o', label='Mean Susceptibility')
ax2.set_ylabel('Mean Susceptibility', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')

# change x ticks to be the vegetation classes remapped with json
legend_file = '/home/sadc/share/project/calabria/data/raw/vegetation/legend_veg_code_ml.json'
legend = json.load(open(legend_file))
ax1.set_xticks(veg_classes)
ax1.set_xticklabels([legend[str(int(i))] for i in veg_classes], rotation=90)

plt.title('2024/07: Burned Area and Mean Susceptibility per Vegetation Class')
plt.tight_layout()

#%% v2 normalize bA

import rasterio as rio
from rasterio.mask import mask as rio_mask
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

veg_tiff_path = '/home/sadc/share/project/calabria/data/raw/vegetation/vegetation_ml.tif'
susc_1_file = '/home/sadc/share/project/calabria/data/susceptibility/v4/susc_calabria_2024_7.tif'

# Clip vegetation map over fire polygons
with rio.open(veg_tiff_path) as veg_src:
    veg_clip, veg_transform = rio_mask(veg_src, fires24_7.geometry)
    veg_array = veg_clip[0]
    veg_nodata = veg_src.nodata
    veg_res = veg_src.res[0] * veg_src.res[1]  # resolution in map units squared (e.g. m²)

# Clip susceptibility file 1 over same fire polygons
with rio.open(susc_1_file) as susc_src:
    susc_clip, _ = rio_mask(susc_src, fires24_7.geometry)
    susc_array = susc_clip[0]
    susc_nodata = susc_src.nodata

# Mask nodata
mask_valid = (veg_array != 0) & (veg_array != veg_nodata) & (susc_array != susc_nodata) & (susc_array != -1)

veg_valid = veg_array[mask_valid]
susc_valid = susc_array[mask_valid]

# Compute burned area per vegetation class
veg_classes, veg_counts = np.unique(veg_valid, return_counts=True)
burned_area_per_class = veg_counts * veg_res  # assuming area units are square meters
burned_area_per_class /= 10000  # convert to hectares
# eval the total area in ha of each class
veg_class_areas = list()
with rio.open(veg_tiff_path) as veg_src:
    veg_arr = veg_src.read(1)
    for veg_class in veg_classes:
        area = np.where(veg_arr == veg_class, 1, 0).sum() * veg_res
        area /= 10000  # convert to hectares
        veg_class_areas.append(area)

#normalize the burned area
burned_area_per_class_ratio = burned_area_per_class / np.array(veg_class_areas) * 10000


# Build DataFrame and compute stats
df = pd.DataFrame({'veg': veg_valid, 'susc': susc_valid})
stats = df.groupby('veg')['susc'].agg(['mean', lambda x: np.percentile(x, 10), lambda x: np.percentile(x, 90)])
stats.columns = ['mean', 'p25', 'p75']
stats = stats.reindex(veg_classes)

# Plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart: burned area
ax1.bar(veg_classes, burned_area_per_class_ratio, color='tab:green', alpha=0.6, label='Burned Area')
ax1.set_ylabel('Burned Area (per 10.000 ha)', color='tab:green')
ax1.tick_params(axis='y', labelcolor='tab:green')

# Line plot: mean susceptibility with error bars (25-75 percentiles)
ax2 = ax1.twinx()
ax2.errorbar(
    veg_classes,
    stats['mean'],
    yerr=[stats['mean'] - stats['p25'], stats['p75'] - stats['mean']],
    fmt='o-',
    color='tab:red',
    capsize=4,
    label='Mean Susceptibility (10-90%)'
)
ax2.set_ylabel('Mean Susceptibility', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')

# Map x ticks to vegetation class names
legend_file = '/home/sadc/share/project/calabria/data/raw/vegetation/legend_veg_code_ml.json'
legend = json.load(open(legend_file))
ax1.set_xticks(veg_classes)
ax1.set_xticklabels([legend.get(str(int(i)), str(int(i))) for i in veg_classes], rotation=90)

plt.title('2024/07: Burned Area and Mean Susceptibility per Vegetation Class')
plt.tight_layout()

#%%


