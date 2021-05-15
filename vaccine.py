import pandas as pd



def add_daily_vaccinations(state_df):
    # state_df['vaccinations'] = state_df['Total Individuals Vaccinated'].diff()
    state_df['vaccinations'] = state_df['Total Doses Administered'].diff()
    state_df['second_doses'] = state_df['Second Dose Administered'].diff()
    return state_df


vaccine_df = pd.read_csv('cowin_vaccine_data_statewise.csv')
vaccine_df = vaccine_df.groupby('State').apply(add_daily_vaccinations)
vaccine_df = vaccine_df[['Updated On', 'State', 'vaccinations', 'second_doses']]
vaccine_df.columns = ['Date', 'state', 'vaccinations', 'second_doses']
vaccine_df['Date'] = pd.to_datetime(vaccine_df['Date'], format='%d/%m/%Y')
vaccine_df.dropna(inplace=True)



def get_state_vaccine_totals_df(vaccine_df):
    state_vaccine_totals_df = pd.pivot_table(
                        vaccine_df,
                        index='state',
                        values=['vaccinations', 'second_doses'],
                        aggfunc='sum'
                    )
    return state_vaccine_totals_df