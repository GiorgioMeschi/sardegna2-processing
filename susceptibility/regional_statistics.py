


'''
compare ussceptibilty maps of june 2025 with june 2024 and 2021 
'''
import rasterio as rio
import numpy as np
import pandas as pd
from home import DATAPATH
import json
from itertools import combinations

VS = 'v1'

dem_file = f'{DATAPATH}/raw/dem/dem_ispra_100m_32632_v2.tif'

# Define file paths
susc_files = {
    'June 2025': f'{DATAPATH}/susceptibility/{VS}/susc_2025_6.tif',
    'June 2024': f'{DATAPATH}/susceptibility/{VS}/susc_2024_6.tif',
    'June 2021': f'{DATAPATH}/susceptibility/{VS}/susc_2021_6.tif',
}

threshold_file = f'{DATAPATH}/susceptibility/{VS}/thresholds/thresholds.json'
lv1, lv2 = json.load(open(threshold_file))['lv1'], json.load(open(threshold_file))['lv2']


# ---- Utility functions ---- #
def eval_susc(susc_file, lv1, lv2):
    with rio.open(susc_file) as src:
        arr = src.read(1)
        vals = arr[arr != -1]
        mean = np.mean(vals)
        std = np.std(vals)
        p25 = np.percentile(vals, 25)
        p75 = np.percentile(vals, 75)
        p99 = np.percentile(vals, 99)
        high_px = np.where(vals >= lv2, 1, 0).sum()
        low_px = np.where(vals < lv1, 1, 0).sum()
        medium_px = vals.size - high_px - low_px
        tot_px = vals.size
    return mean, std, p25, p75, p99, high_px/tot_px*100, low_px/tot_px*100, medium_px/tot_px*100

def pairwise_corr(file1, file2):
    with rio.open(file1) as src1, rio.open(file2) as src2:
        a1 = src1.read(1).astype(float)
        a2 = src2.read(1).astype(float)
        mask = (a1 != -1) & (a2 != -1)
        return np.corrcoef(a1[mask], a2[mask])[0, 1]

def class_agreement(file1, file2, lv1, lv2):
    def classify(arr):
        return np.where(arr < lv1, 1, np.where(arr < lv2, 2, 3))

    with rio.open(file1) as src1, rio.open(file2) as src2:
        a1 = classify(src1.read(1))
        a2 = classify(src2.read(1))
        mask = (a1 != -1) & (a2 != -1)
        return (a1[mask] == a2[mask]).sum() / mask.sum() * 100

# ---- Collect statistics ---- #
df_dict = {}
for name, path in susc_files.items():
    mean, std, p25, p75, p99, high_px, low_px, med_px = eval_susc(path, lv1, lv2)
    df_dict[name] = {
        'mean': round(mean, 3),
        'std': round(std, 3),
        'p25': round(p25, 3),
        'p75': round(p75, 3),
        'p99': round(p99, 3),
        'class 3 (%)': round(high_px, 0),
        'class 2 (%)': round(med_px, 0),
        'class 1 (%)': round(low_px, 0),
    }

# ---- Add pairwise correlation and agreement ---- #
# Loop through combinations
for (name1, file1), (name2, file2) in combinations(susc_files.items(), 2):
    corr = pairwise_corr(file1, file2)
    agree = class_agreement(file1, file2, lv1, lv2)
    
    df_dict[name1][f'corr with {name2}'] = round(corr, 2)
    df_dict[name1][f'agree with {name2} (%)'] = round(agree, 0)

    df_dict[name2][f'corr with {name1}'] = round(corr, 3)
    df_dict[name2][f'agree with {name1} (%)'] = round(agree, 0)

# ---- Final DataFrame ---- #
df = pd.DataFrame(df_dict).T
#repalce nan with '-'
df = df.fillna('-')
folder = f'{DATAPATH}/susceptibility/{VS}/regional_statistics/june'
os.makedirs(folder, exist_ok=True)
df.to_csv(f'{folder}//regional_statistics_june.csv')


