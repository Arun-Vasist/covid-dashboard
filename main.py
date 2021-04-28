import pandas as pd
from helper import clean_raw_data, modify_geojson, get_modified_state_metrics_df
from vaccine import vaccine_df
from state_level import get_state_metrics_df
from india_overall import get_india_df
from date_wise import get_date_wise_metrics
import json
from create_app import create_app
from config import in_production

# TODO Dadra and Nagar Haveli and Daman and Diu
# TODO Add Navbar


df = pd.read_csv('state_wise_daily.csv')
df = clean_raw_data(df)

india_df = get_india_df(df, vaccine_df)

state_population_df = pd.read_csv('population.csv')

state_metrics_df = get_state_metrics_df(df, vaccine_df, state_population_df)
state_metrics_df = get_modified_state_metrics_df(state_metrics_df)

date_wise_metrics = get_date_wise_metrics(df, state_population_df, vaccine_df)

india_geojson = json.load(open("states_india.geojson", "r"))
india_geojson = modify_geojson(india_geojson)

moving_avg_df = date_wise_metrics.copy()
moving_avg_df = moving_avg_df.rolling(7).mean()

date_mask = moving_avg_df.index >= '2020-07-01'
app = create_app(moving_avg_df[date_mask], state_metrics_df, india_df, india_geojson)

# server = app.server
if in_production:
    server = app.server
else:
    app.run_server()
