import numpy as np
import pandas as pd
from config import avg_days_to_death

def get_date_wise_metrics(df, state_population_df, vaccine_df):
    date_wise_metrics = pd.pivot_table(
                    df,
                    index='Date',
                    columns='Status',
                    values=df.columns[2:],
                    aggfunc='sum'
                    )

    date_wise_metrics = date_wise_metrics.stack(level=0)
    date_wise_metrics.reset_index(inplace=True)
    date_wise_metrics.rename({'level_1': 'state'}, axis=1, inplace=True)
    date_wise_metrics = pd.merge(date_wise_metrics, state_population_df, on='state', how='left')
    date_wise_metrics = pd.merge(date_wise_metrics, vaccine_df, on=['Date', 'state'], how='left')
    date_wise_metrics = pd.pivot_table(
                        date_wise_metrics,
                        index='Date',
                        columns='state',
                        values=date_wise_metrics.columns[2:],
                        aggfunc='sum'
                    )

    for col in date_wise_metrics.columns:
        metric, state = col
        if metric == 'Confirmed':
            date_wise_metrics[('case_fatality_rate', state)] = date_wise_metrics[('Deceased', state)] / \
                                                               date_wise_metrics[col].shift(avg_days_to_death)
            date_wise_metrics[('cases_per_million', state)] = date_wise_metrics[('Confirmed', state)] / \
                                                              date_wise_metrics[('population', state)] * 1000000
            date_wise_metrics[('deaths_per_million', state)] = date_wise_metrics[('Deceased', state)] / \
                                                               date_wise_metrics[('population', state)] * 1000000
            date_wise_metrics[('pct_vaccinated', state)] = date_wise_metrics[('vaccinations', state)] / \
                                                                     date_wise_metrics[('population', state)]

    date_wise_metrics = date_wise_metrics.applymap(lambda x: np.nan if x == np.inf else x)
    date_wise_metrics = date_wise_metrics.interpolate()

    return date_wise_metrics
