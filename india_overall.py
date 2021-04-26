import pandas as pd
from helper import add_derived_metrics


def get_india_df(df):
    india_df = pd.concat([df.iloc[:, :2], df.iloc[:, 2:].sum(axis=1)], axis=1)
    india_df.columns = ['Date', 'Status', 'Value']
    india_df = pd.pivot_table(
                india_df,
                index='Date',
                columns='Status',
                values='Value',
                aggfunc='sum'
            )
    india_df['population'] = 138000385
    india_df['cases_per_million'] = india_df['Confirmed'] / india_df['population'] * 1000000
    india_df['deaths_per_million'] = india_df['Deceased'] / india_df['population'] * 1000000
    india_df['case_fatality_rate'] = india_df['Deceased'] / india_df['Confirmed'].shift(15)

    return india_df



