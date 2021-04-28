import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from helper import state_id_map, print_formatted, print_delta, fix_name
from graph import get_date_wise_plot, get_choropleth, get_india_date_wise_plot

reverse_state_id_map = {v: k for k, v in state_id_map.items()}

tooltip_text = {
    'pct_vaccinated': 'SUM(Vaccinations) / SUM(Population)',
    'cases_per_million': 'SUM(Cases) / SUM(Population) * 1M',
    'case_fatality_rate': 'The proportion of people who died among all individuals diagnosed with Covid up till 15 days ago',
    'deaths_per_million': 'SUM(Deaths) / SUM(Population) * 1M',
}

card_body_style = {'textAlign': 'center', 'padding': '5px'}

def generate_kpi_card_body(click_data, metric, state_metrics_df):
    if not click_data:
        state_name = 'India'
        result = state_metrics_df.loc[state_name, metric]
        vs_national_avg = html.H3('-', style={'color': 'white', 'font-size': 32})
        rank = html.H6('-', style={'color': 'white', 'font-size': 20})
    else:
        state_id = click_data['points'][0]['location']
        state_name = reverse_state_id_map[state_id]
        result = state_metrics_df.loc[state_name, metric]
        if 'vacci' in metric:
            color = '#27ae60' if result > state_metrics_df.loc['India', metric] else '#d91e18'
        else:
            color = '#d91e18' if result > state_metrics_df.loc['India', metric] else '#27ae60'
        vs_national_avg = html.H3(
            f"{print_delta(now=result, prev=state_metrics_df.loc['India', metric])} vs National Avg",
                                  style={'color': color, 'font-size': 32})
        rank = html.H6(f"Rank : {int(state_metrics_df.loc[state_name, f'{metric}_rank'])} of {state_metrics_df.shape[0] - 1}",
                       style={'font-size': 20})

    card_body = dbc.CardBody([
                    html.H5(f'{state_name} - {fix_name(metric)}',
                            id=f'kpi_{metric}_header',
                            style={"textDecoration": "underline", "cursor": "pointer", 'font-size': 20}),
                    html.H1(print_formatted(result, metric),
                            style={'font-weight': 'bold', 'font-size': 40, 'margin-bottom': 0}),
                    vs_national_avg,
                    rank,
                    dbc.Tooltip(tooltip_text[metric], target=f'kpi_{metric}_header')
    ],
        style=card_body_style
    )

    return card_body


plot_card_body_style = {'textAlign': 'center', 'padding-top': '10px', 'padding-bottom': '10px', 'padding-left': '20px', 'padding-right': '0px'}

def generate_plot_card_body(click_data, metric, india_df, date_wise_metrics):
    if not click_data:
        state_name = 'India'
        plot = get_india_date_wise_plot(india_df, metric)
    else:
        state_id = click_data['points'][0]['location']
        state_name = reverse_state_id_map[state_id]
        plot = get_date_wise_plot(date_wise_metrics, state_name, metric)

    card_body = dbc.CardBody([
        html.H5(f"{state_name} - {fix_name(metric)}"),
        dbc.Row(plot)
    ], style=card_body_style)

    return card_body


def create_app(date_wise_metrics, state_metrics_df, india_df, india_geojson):
    choropleth = get_choropleth(state_metrics_df, india_geojson)

    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    card_style = {'margin-bottom': '10px', 'padding-bottom': '0px'}
    pct_vaccinated_card = dbc.Card(id='pct_vaccinated_card', style=card_style)
    cases_per_million_card = dbc.Card(id='cases_per_million_card', style=card_style)
    case_fatality_rate_card = dbc.Card(id='case_fatality_rate_card', style=card_style)
    deaths_per_million_card = dbc.Card(id='deaths_per_million_card', style=card_style)

    kpi_cards = [
        pct_vaccinated_card,
        cases_per_million_card,
        case_fatality_rate_card,
        deaths_per_million_card,
    ]

    vaccinations_plot_card = dbc.Card(id='vaccinations_plot_card', style=card_style)
    confirmed_plot_card = dbc.Card(id='confirmed_plot_card', style=card_style)
    case_fatality_rate_plot_card = dbc.Card(id='case_fatality_rate_plot_card', style=card_style)
    deaths_plot_card = dbc.Card(id='deaths_plot_card', style=card_style)

    plots = [
        vaccinations_plot_card,
        confirmed_plot_card,
        case_fatality_rate_plot_card,
        deaths_plot_card,
    ]

    button_style = {
        'margin-left': '20px',
        'margin-right': '20px',
        'margin-bottom': '20px',
     }
    button = dbc.Button('Show overall', id='india_button', style=button_style)

    choropleth_card = dbc.Card(
        [
            html.H4('States with Deaths per million > 250',
                    style={'textAlign': 'center', 'margin-top': '20px'}
                    ),
            choropleth,
            button
        ]
    )

    header_card = dbc.Card(
        html.H1(
            'India Covid Dashboard',
            style={'margin-left': '20px', 'font-size': 35, 'font-weight': 'bold', 'color': '#bdc3c7'}
        ),
        style={'margin-left': '20px', 'margin-right': '20px', 'margin-top': '20px'}
    )

    body = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(kpi_cards, width=4),
                    dbc.Col(plots, width=4),
                    dbc.Col(choropleth_card, width=4),
                    dbc.Col(html.H1(id='test')),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                ]
            )
        ],
        style={'margin': '10px'}
    )

    app.layout = html.Div(
                        [
                            body
                        ]
                )

    @app.callback(
        [
            Output("pct_vaccinated_card", "children"),
            Output("cases_per_million_card", "children"),
            Output("case_fatality_rate_card", "children"),
            Output("deaths_per_million_card", "children"),
            Output("vaccinations_plot_card", "children"),
            Output("confirmed_plot_card", "children"),
            Output("case_fatality_rate_plot_card", "children"),
            Output("deaths_plot_card", "children"),
         ],
        [Input("choropleth", "clickData"), Input("india_button", "n_clicks")]
    )
    def render_page_content(click_data, _):
        ctx = dash.callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'choropleth':
            vaccinations_kpi_card = generate_kpi_card_body(click_data, "pct_vaccinated", state_metrics_df)
            cases_kpi_card = generate_kpi_card_body(click_data, "cases_per_million", state_metrics_df)
            cfr_kpi_card = generate_kpi_card_body(click_data, "case_fatality_rate", state_metrics_df)
            deaths_kpi_card = generate_kpi_card_body(click_data, "deaths_per_million", state_metrics_df)
            vaccinations_plot_card = generate_plot_card_body(click_data, 'vaccinations', india_df, date_wise_metrics)
            cases_plot_card = generate_plot_card_body(click_data, 'Confirmed', india_df, date_wise_metrics)
            cfr_plot_card = generate_plot_card_body(click_data, 'case_fatality_rate', india_df, date_wise_metrics)
            deaths_plot_card = generate_plot_card_body(click_data, 'Deceased', india_df, date_wise_metrics)
            return vaccinations_kpi_card, cases_kpi_card, cfr_kpi_card, deaths_kpi_card, vaccinations_plot_card, cases_plot_card, cfr_plot_card, deaths_plot_card
        else:
            vaccinations_kpi_card = generate_kpi_card_body(None, "pct_vaccinated", state_metrics_df)
            cases_kpi_card = generate_kpi_card_body(None, "cases_per_million", state_metrics_df)
            cfr_kpi_card = generate_kpi_card_body(None, "case_fatality_rate", state_metrics_df)
            deaths_kpi_card = generate_kpi_card_body(None, "deaths_per_million", state_metrics_df)
            vaccinations_plot_card = generate_plot_card_body(None, 'vaccinations', india_df, date_wise_metrics)
            cases_plot_card = generate_plot_card_body(None, 'Confirmed', india_df, date_wise_metrics)
            cfr_plot_card = generate_plot_card_body(None, 'case_fatality_rate', india_df, date_wise_metrics)
            deaths_plot_card = generate_plot_card_body(None, 'Deceased', india_df, date_wise_metrics)
            return vaccinations_kpi_card, cases_kpi_card, cfr_kpi_card, deaths_kpi_card, vaccinations_plot_card, cases_plot_card, cfr_plot_card, deaths_plot_card

    return app