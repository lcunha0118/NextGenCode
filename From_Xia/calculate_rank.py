# Compute rank for selected metrics

import pandas as pd
import numpy as np

# data
df = pd.read_csv('test_rank.csv')

# variables
catids = df['catchment_id'].unique().tolist()
all_metrics = df.columns[2:].tolist()
part_metrics = all_metrics[2:] 
interval_value = {'KGE': [-np.inf, 0, 0.3, 0.6, 0.75, 1],'NNSEWt': [0, 0.2, 0.5, 0.6, 0.75, 1], 'PBIAS': [-np.inf, -50, -20, -10, -5, 0],
                  'RMSE': [-np.inf, -0.8, -0.6, -0.4, -0.2, 0],'HSEG_FDC': [-np.inf, -50, -20, -10, -5, 0],
                  'pk_error_perc_median': [-np.inf, -60, -40, -20, -10, 0],'pk_timing_error_mean_h': [-np.inf, -36, -24, -12, -6, 0]}
rank_category=[1, 2, 3, 4, 5]

# calculate rank
df_rank = pd.DataFrame()
for catid in catids:
    for row in df.itertuples():
        dict1 = {'catid': catid, 'model': row.model}
        for x in all_metrics:
            if x in part_metrics:
                value = -abs(df.loc[row.Index, x])
            else:
                value = df.loc[row.Index, x]
            z = pd.cut(np.array([value]), bins=interval_value[x], include_lowest=False if x=='KGE' else True)
            bl = z.categories.map(lambda xx: value in xx)
            rank_value = [r for r, b in zip(rank_category, bl) if b][0]
            dict1.update({x: rank_value}) 
        df_rank = df_rank.append([dict1], ignore_index=True)

print(df_rank)

    
