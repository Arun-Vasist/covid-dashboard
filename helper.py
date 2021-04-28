import pandas as pd
from config import avg_days_to_death


state_abbreviations_dict = {
    'AP': 'Andhra Pradesh',
    'AR': 'Arunachal Pradesh',
    'AS': 'Assam',
    'BR': 'Bihar',
    'CH': 'Chandigarh',
    'CT': 'Chhattisgarh',
    'GA': 'Goa',
    'GJ': 'Gujarat',
    'HR': 'Haryana',
    'HP': 'Himachal Pradesh',
    'JK': 'Jammu and Kashmir',
    'JH': 'Jharkhand',
    'KA': 'Karnataka',
    'KL': 'Kerala',
    'LA': 'Ladakh',
    'MP': 'Madhya Pradesh',
    'MH': 'Maharashtra',
    'MN': 'Manipur',
    'ML': 'Meghalaya',
    'MZ': 'Mizoram',
    'NL': 'Nagaland',
    'OR': 'Odisha',
    'PB': 'Punjab',
    'RJ': 'Rajasthan',
    'SK': 'Sikkim',
    'TG': 'Telangana',
    'TN': 'Tamil Nadu',
    'TR': 'Tripura',
    'UT': 'Uttarakhand',
    'UP': 'Uttar Pradesh',
    'WB': 'West Bengal',
    'AN': 'Andaman and Nicobar Islands',
    'CH': 'Chandigarh',
    'DN': 'Dadra and Nagar Haveli',
    'DD': 'Daman and Diu',
    'DL': 'Delhi',
    'LD': 'Lakshadweep',
    'PY': 'Pondicherry'
}

state_conversion_dict = {
    'Andaman and Nicobar Islands': 'Andaman & Nicobar Island',
    'Arunachal Pradesh': 'Arunanchal Pradesh',
    'Daman and Diu': 'Daman & Diu',
    'Jammu and Kashmir': 'Jammu & Kashmir',
    'Pondicherry': 'Puducherry',
    'Dadra and Nagar Haveli': 'Dadara & Nagar Havelli',
    'Delhi': 'NCT of Delhi'
}

state_id_map = {
    'Telangana': 0,
    'Andaman and Nicobar Islands': 35,
    'Andhra Pradesh': 28,
    'Arunachal Pradesh': 12,
    'Assam': 18,
    'Bihar': 10,
    'Chhattisgarh': 22,
    'Daman and Diu': 25,
    'Goa': 30,
    'Gujarat': 24,
    'Haryana': 6,
    'Himachal Pradesh': 2,
    'Jammu and Kashmir': 1,
    'Jharkhand': 20,
    'Karnataka': 29,
    'Kerala': 32,
    'Lakshadweep': 31,
    'Madhya Pradesh': 23,
    'Maharashtra': 27,
    'Manipur': 14,
    'Chandigarh': 4,
    'Pondicherry': 34,
    'Punjab': 3,
    'Rajasthan': 8,
    'Sikkim': 11,
    'Tamil Nadu': 33,
    'Tripura': 16,
    'Uttar Pradesh': 9,
    'Uttarakhand': 5,
    'West Bengal': 19,
    'Odisha': 21,
    'Dadra and Nagar Haveli': 26,
    'Meghalaya': 17,
    'Mizoram': 15,
    'Nagaland': 13,
    'Delhi': 7
}


def clean_raw_data(df):
    df['JK'] = df['JK'] + df['LA']
    df.drop(['Date', 'LA', 'UN', 'TT', 'DD'], axis=1, inplace=True)
    df.rename({'Date_YMD': 'Date'}, axis=1, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.columns = [state_abbreviations_dict.get(col, col) for col in df.columns]
    for col in df.columns:
        if col not in ['Date', 'Status']:
            df[col] = df[col].abs()
    return df


def get_modified_state_metrics_df(state_metrics_df):
    state_metrics_df['id'] = state_metrics_df.index.map(state_id_map)
    return state_metrics_df


def filter_status(df, status):
    status_mask = df['Status'] == status
    status_filtered_df = df[status_mask].drop('Status', axis=1)
    return status_filtered_df


def get_confirmed_cum_sum_df(confirmed_df):
    confirmed_cum_sum_df = confirmed_df.copy()
    confirmed_cum_sum_df['month_year'] = confirmed_cum_sum_df['Date'].dt.strftime('%Y-%m')
    confirmed_cum_sum_df = confirmed_cum_sum_df.groupby('month_year', as_index=False).sum()
    for col in confirmed_cum_sum_df:
        if col != 'month_year':
            confirmed_cum_sum_df[col] = confirmed_cum_sum_df[col].cumsum()

    # confirmed_cum_sum_df = pd.melt(confirmed_cum_sum_df, id_vars=['month_year'], var_name='state', value_name='Confirmed')

    return confirmed_cum_sum_df


confirmed_cases_peak = 'Sept 16'

def add_derived_metrics(df):
    df['cases_per_million'] = df['Confirmed'] / df['population'] * 1000000
    df['deaths_per_million'] = df['Deceased'] / df['population'] * 1000000
    df['pct_vaccinated'] = df['vaccinations'] / df['population']
    df['case_fatality_rate'] = df['Deceased'] / df['Confirmed'].shift(avg_days_to_death)

    return df


def modify_geojson(india_geojson):
    for feature in india_geojson["features"]:
        feature["id"] = feature["properties"]["state_code"]
    return india_geojson


def human_format(num):
    num = abs(num)
    magnitude = 0
    original_num = num
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    if (magnitude == 1):
        return f"{(round(num, 2))}K"
    elif (magnitude == 2):
        return f"{round(num, 2)}M"
    else:
        return f"{round(original_num, 2)}"


def print_formatted(value, metric):
    metric = metric.lower()
    if metric.endswith('rate') or metric == 'pct_vaccinated':
        return f"{100*value:.2f}%"
    else:
        return human_format(value)


def delta_print_pct(prev, now):
    prev = float(prev)
    now = float(now)
    if prev == 0:
        if now == 0:
            return 0
        else:
            return "∞"
    else:
        result = now / (prev) - 1
        if abs(result) < 10:
            return abs(int(round((now / (prev) - 1) * 100)))
        else:
            return ">1000"


def print_delta(prev, now):
    greater = now > prev
    return f"{'▲' if greater else '▼'}{delta_print_pct(prev=prev, now=now)}%"


def fix_name(metric):
    if metric == 'Confirmed':
        return 'Cases'
    if metric == 'Deceased':
        return 'Deaths'
    if metric == 'pct_vaccinated':
        return 'Percentage vaccinated'
    metric = ' '.join(metric.split('_'))
    return metric.title()


