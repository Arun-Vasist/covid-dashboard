import pandas as pd
from helper import add_derived_metrics
from vaccine import get_state_vaccine_totals_df
from datetime import timedelta
from config import avg_days_to_death


def get_state_metrics_df(df, vaccine_df, state_population_df):
    state_vaccine_totals_df = get_state_vaccine_totals_df(vaccine_df)

    max_date = df['Date'].max()
    not_confirmed_mask = df['Status'].isin(['Recovered', 'Deceased'])
    date_mask = df['Date'] <= max_date - timedelta(days=avg_days_to_death)

    state_metrics_df = pd.pivot_table(
                        df[date_mask | not_confirmed_mask],
                        columns='Status',
                        aggfunc='sum'
                    )
    state_metrics_df.index.name = 'state'

    state_metrics_df = pd.merge(state_metrics_df, state_population_df, on='state')
    state_metrics_df = pd.merge(state_metrics_df, state_vaccine_totals_df, on='state')
    state_metrics_df.set_index('state', inplace=True)

    state_metrics_df['cases_per_million'] = state_metrics_df['Confirmed'] / state_metrics_df['population'] * 1000000
    state_metrics_df['deaths_per_million'] = state_metrics_df['Deceased'] / state_metrics_df['population'] * 1000000
    state_metrics_df['vaccinations_per_million'] = state_metrics_df['vaccinations'] / state_metrics_df['population'] * 1000000
    state_metrics_df['case_fatality_rate'] = state_metrics_df['Deceased'] / state_metrics_df['Confirmed']
    
    for metric in state_metrics_df:
        state_metrics_df[f"{metric}_rank"] = state_metrics_df[metric].rank(method='max', ascending=False)

    state_metrics_df.loc["India"] = state_metrics_df.sum()

    state_metrics_df['cases_per_million'] = state_metrics_df['Confirmed'] / state_metrics_df['population'] * 1000000
    state_metrics_df['deaths_per_million'] = state_metrics_df['Deceased'] / state_metrics_df['population'] * 1000000
    state_metrics_df['vaccinations_per_million'] = state_metrics_df['vaccinations'] / state_metrics_df['population'] * 1000000
    state_metrics_df['case_fatality_rate'] = state_metrics_df['Deceased'] / state_metrics_df['Confirmed']

    return state_metrics_df