import pandas as pd

vaccine_df = pd.read_csv('cowin_vaccine_data_statewise.csv')

vaccine_df = vaccine_df[['Updated On', 'State', 'Total Individuals Vaccinated']]
vaccine_df.columns = ['Date', 'state', 'vaccinations']
vaccine_df['Date'] = pd.to_datetime(vaccine_df['Date'], format='%d/%m/%Y')
vaccine_df.dropna(inplace=True)

def get_state_vaccine_totals_df(vaccine_df):
    state_vaccine_totals_df = pd.pivot_table(
                        vaccine_df,
                        index='state',
                        values='vaccinations',
                        aggfunc='sum'
                    )
    return state_vaccine_totals_df