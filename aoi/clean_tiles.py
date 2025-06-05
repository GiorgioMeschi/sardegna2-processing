
#%%
'''
enumerate tiles by id_sorted from top left to bottom right
'''

import geopandas as gpd
import matplotlib.pyplot as plt
from home import HOME, DATAPATH

tiles_file = f'{DATAPATH}/aoi/grid.geojsonl.json'

# open tiles
tiles = gpd.read_file(tiles_file, driver='GeoJSONSeq')
# order id by rows, I have 4 columns left top bottom right:
tiles = tiles.sort_values(by=['top'], ascending=[False])  # Ensure top-to-bottom order first
tiles = tiles.sort_values(by=['top', 'left'], ascending=[False, True])  # Then left to right in each row
# creat new id
tiles['id_sorted'] = range(1, len(tiles)+1)
# plot every tile with id as label:
tiles.plot(column='id_sorted', legend=True)
for idx, row in tiles.iterrows():
    centroid = row.geometry.centroid
    plt.text(centroid.x, centroid.y, str(row['id_sorted']), fontsize=8, ha='center', va='center', color='black')

#save tiles
out = tiles_file.replace('.geojsonl.json', '_clean.geojsonl.json')
tiles.to_file(out, driver='GeoJSONSeq')


#%% plot tile with boundaries

tiles_f = f'{DATAPATH}/aoi/grid_clean.geojsonl.json'
boud_f = f'{DATAPATH}/aoi/calabria.geojsonl.json'

tiles = gpd.read_file(tiles_f, driver='GeoJSONSeq')
bouds = gpd.read_file(boud_f, driver='GeoJSONSeq')

# to 3857
tiles = tiles.to_crs(epsg=3857)
bouds = bouds.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(10, 10), dpi = 300)

tiles.plot(column='id_sorted', ax=ax, facecolor='none', edgecolor='blue', linewidth=1)
bouds.boundary.plot(ax=ax, color='black', linewidth=0.7)

for idx, row in tiles.iterrows():
    centroid = row.geometry.centroid
    ax.text(centroid.x, centroid.y, str(row['id_sorted']), fontsize=12, ha='center', va='center', color='black')

#ax off
ax.axis('off')
#save
fig.savefig(f'{DATAPATH}/aoi/tiles.png', dpi=300, bbox_inches='tight')

#%%


