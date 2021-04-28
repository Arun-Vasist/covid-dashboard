import pandas as pd
from helper import add_derived_metrics
from config import avg_days_to_death


def get_india_df(df, vaccine_df):
    india_df = pd.concat([df.iloc[:, :2], df.iloc[:, 2:].sum(axis=1)], axis=1)
    india_df.columns = ['Date', 'Status', 'Value']
    india_df = pd.pivot_table(
                india_df,
                index='Date',
                columns='Status',
                values='Value',
                aggfunc='sum'
            )
    india_df.reset_index(inplace=True)
    india_df['population'] = 138000385
    india_mask = vaccine_df['state'] == 'India'
    india_df = pd.merge(india_df, vaccine_df[india_mask], how='left', on='Date')
    india_df.set_index('Date', inplace=True)
    india_df['cases_per_million'] = india_df['Confirmed'] / india_df['population'] * 1000000
    india_df['deaths_per_million'] = india_df['Deceased'] / india_df['population'] * 1000000
    india_df['pct_vaccinated'] = india_df['Deceased'] / india_df['population']
    india_df['case_fatality_rate'] = india_df['Deceased'] / india_df['Confirmed'].shift(avg_days_to_death)

    return india_df



