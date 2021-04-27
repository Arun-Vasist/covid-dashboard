import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from helper import state_id_map, print_formatted, print_delta, fix_name
from graph import get_date_wise_plot, get_choropleth, get_india_date_wise_plot

reverse_state_id_map = {v: k for k, v in state_id_map.items()}

tooltip_text = {
    'cases_per_million': 'SUM(Cases) / SUM(Population) * 1M',
    'case_fatality_rate': 'The proportion of people who died among all individuals diagnosed with Covid up till 15 days ago',
    'deaths_per_million': 'SUM(Deaths) / SUM(Population) * 1M',
}


def generate_kpi_card_body(click_data, metric, state_metrics_df):
    if not click_data:
        state_name = 'India'
        result = state_metrics_df.loc[state_name, metric]
        vs_national_avg = html.H2('-', style={'color': 'white'})
        rank = html.H5('-', style={'color': 'white'})
    else:
        state_id = click_data['points'][0]['location']
        state_name = reverse_state_id_map[state_id]
        result = state_metrics_df.loc[state_name, metric]
        color = '#d91e18' if result > state_metrics_df.loc['India', metric] else '#27ae60'
        vs_national_avg = html.H2(
            f"{print_delta(now=result, prev=state_metrics_df.loc['India', metric])} vs National Avg",
                                  style={'color': color})
        rank = html.H5(f"Rank : {int(state_metrics_df.loc[state_name, f'{metric}_rank'])} of {state_metrics_df.shape[0] - 1}")

    card_body = dbc.CardBody([
                    html.H5(f'{state_name} - {fix_name(metric)}',
                            id=f'kpi_{metric}_header',
                            style={"textDecoration": "underline", "cursor": "pointer"}),
                    html.H1(print_formatted(result, metric), style={'font-weight': 'bold', 'font-size': 50}),
                    vs_national_avg,
                    rank,
                    dbc.Tooltip(tooltip_text[metric], target=f'kpi_{metric}_header')
    ],
        style={'textAlign': 'center'}
    )

    return card_body


def generate_plot_card_body(click_data, metric, india_df, date_wise_metrics):
    if not click_data:
        state_name = 'India'
        plot = get_india_date_wise_plot(india_df, metric)
    else:
        state_id = click_data['points'][0]['location']
        state_name = reverse_state_id_map[state_id]
        plot = get_date_wise_plot(date_wise_metrics, state_name, metric)

    card_body = dbc.CardBody([
        html.H4(f"{state_name} - {fix_name(metric)}"),
        dbc.Row(plot)
    ], style={'textAlign': 'center'})

    return card_body


def create_app(date_wise_metrics, state_metrics_df, india_df, india_geojson):
    choropleth = get_choropleth(state_metrics_df, india_geojson)

    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    cases_per_million_card = dbc.Card(id='cases_per_million_card', style={'margin-bottom': '20px'})
    case_fatality_rate_card = dbc.Card(id='case_fatality_rate_card', style={'margin-bottom': '20px'})
    deaths_per_million_card = dbc.Card(id='deaths_per_million_card')

    kpi_cards = [
        cases_per_million_card,
        case_fatality_rate_card,
        deaths_per_million_card,
    ]

    confirmed_plot_card = dbc.Card(id='confirmed_plot_card', style={'margin-bottom': '20px'})
    case_fatality_rate_plot_card = dbc.Card(id='case_fatality_rate_plot_card', style={'margin-bottom': '20px'})
    deaths_plot_card = dbc.Card(id='deaths_plot_card')

    plots = [
        confirmed_plot_card,
        case_fatality_rate_plot_card,
        deaths_plot_card
    ]

    button_style = {
        'margin-left': '20px',
        'margin-right': '20px',
        'margin-bottom': '20px',
     }
    button = dbc.Button('Reset', id='india_button', style=button_style)

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
        style={'margin': '20px'}
    )

    app.layout = html.Div(
                        [
                            # dbc.Row(
                            #     [
                            #         dbc.Col(header_card, width=12),
                            #     ]
                            # ),
                            body
                        ]
                )

    '''KPI Cards'''

    @app.callback(
        [
            Output("cases_per_million_card", "children"),
            Output("case_fatality_rate_card", "children"),
            Output("deaths_per_million_card", "children"),
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
            cases_kpi_card = generate_kpi_card_body(click_data, "cases_per_million", state_metrics_df)
            cfr_kpi_card = generate_kpi_card_body(click_data, "case_fatality_rate", state_metrics_df)
            deaths_kpi_card = generate_kpi_card_body(click_data, "deaths_per_million", state_metrics_df)
            cases_plot_card = generate_plot_card_body(click_data, 'Confirmed', india_df, date_wise_metrics)
            cfr_plot_card = generate_plot_card_body(click_data, 'case_fatality_rate', india_df, date_wise_metrics)
            deaths_plot_card = generate_plot_card_body(click_data, 'Deceased', india_df, date_wise_metrics)
            return cases_kpi_card, cfr_kpi_card, deaths_kpi_card, cases_plot_card, cfr_plot_card, deaths_plot_card
        else:
            cases_kpi_card = generate_kpi_card_body(None, "cases_per_million", state_metrics_df)
            cfr_kpi_card = generate_kpi_card_body(None, "case_fatality_rate", state_metrics_df)
            deaths_kpi_card = generate_kpi_card_body(None, "deaths_per_million", state_metrics_df)
            cases_plot_card = generate_plot_card_body(None, 'Confirmed', india_df, date_wise_metrics)
            cfr_plot_card = generate_plot_card_body(None, 'case_fatality_rate', india_df, date_wise_metrics)
            deaths_plot_card = generate_plot_card_body(None, 'Deceased', india_df, date_wise_metrics)
            return cases_kpi_card, cfr_kpi_card, deaths_kpi_card, cases_plot_card, cfr_plot_card, deaths_plot_card

    return app