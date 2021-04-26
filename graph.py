import plotly.graph_objects as go
import dash_core_components as dcc

def generateDiscreteColourScale(colour_set):
    #colour set is a list of lists
    colour_output = []
    num_colours = len(colour_set)
    divisions = 1./num_colours
    c_index = 0.
    # Loop over the colour set
    for cset in colour_set:
        num_subs = len(cset)
        sub_divisions = divisions/num_subs
        # Loop over the sub colours in this set
        for subcset in cset:
            colour_output.append((c_index,subcset))
            colour_output.append((c_index + sub_divisions-
                .001,subcset))
            c_index = c_index + sub_divisions
    colour_output[-1]=(1,colour_output[-1][1])
    return colour_output

color_schemes = [
    ['#890000','#890000','#5c0000'],
    ['#2a6b28','#0b4c07','#003206'],
    ['#4f5a90','#374798','#30375a'],
    ['#fff4b1','#ffed86','#ffdb00']
]

color_schemes = [
    ['#bdc3c7'] * 10 + ['#d91e18'] * 22,
]

def get_choropleth(state_metrics_df, india_geojson):
    colorscale = generateDiscreteColourScale(color_schemes)

    text = []
    for state in state_metrics_df.index:
        text.append(f'<b>{state}</b><br>(Click to view data)')
    data = [
        go.Choroplethmapbox(
                        geojson=india_geojson,
                        locations=state_metrics_df['id'],
                        z=state_metrics_df['deaths_per_million'],
                        # colorscale="YlOrRd",
                        colorscale=colorscale,
                        showscale=False,
                        marker_opacity=0.8,
                        text=text,
                        hovertemplate='%{text}<extra></extra>',
                        )
    ]

    layout = go.Layout(
        mapbox_style="carto-positron",
        mapbox_zoom=4,
        mapbox_center={"lat": 23.0895, "lon": 81.5},
        height=700,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hoverlabel=dict(
            bgcolor="white",
            font_size=28,
            font_family="Calibri"
        )
    )

    dash_graph = dcc.Graph(figure={
                            'data':data,
                            'layout': layout
                            },
                            id='choropleth',
                            style={
                                'margin-left': '20px',
                                'margin-right': '20px',
                                'margin-bottom': '20px',
                                'margin-top': '10px'
                            }
                )
    return dash_graph


def get_date_wise_plot(date_wise_metrics, state, metric):
    trace = go.Scatter(
        x=date_wise_metrics.index,
        y=date_wise_metrics[(metric, state)],
        name=state,
        marker_color='blue',
        hovertemplate='%{y:,%}<extra></extra>' if metric == 'case_fatality_rate' else '%{y:.0f}<extra></extra>'
    )

    data = [trace]

    height = 172

    layout = go.Layout(
        yaxis=dict(rangemode='tozero'),
        height=height,
        width=570,
        margin=dict(l=50, r=20, t=10, b=30)
    )

    if metric == 'case_fatality_rate':
        layout['yaxis'] = dict(tickformat='%', rangemode='tozero')

    dash_graph = dcc.Graph(figure={
        'data': data,
        'layout': layout
    }
    )

    return dash_graph


def get_india_date_wise_plot(india_df, metric):
    moving_avg_df = india_df.copy()
    moving_avg_df = moving_avg_df.rolling(7).mean()
    date_mask = moving_avg_df.index > '2020-07-01'
    trace = go.Scatter(
        x=moving_avg_df[date_mask].index,
        y=moving_avg_df[date_mask][metric],
        marker_color='blue',
        hovertemplate='%{y:,%}<extra></extra>' if metric == 'case_fatality_rate' else '%{y:.0f}<extra></extra>'
    )

    data = [trace]

    height = 172

    layout = go.Layout(
        yaxis=dict(rangemode='tozero'),
        height=height,
        width=570,
        margin=dict(l=50, r=20, t=10, b=30)
    )

    if metric == 'case_fatality_rate':
        layout['yaxis'] = dict(tickformat='%', rangemode='tozero')

    dash_graph = dcc.Graph(figure={
        'data': data,
        'layout': layout
    }
    )

    return dash_graph


metric = 'case_fatality_rate'
def plot_metric(state_metrics_df, metric, largest=True):
    if largest:
        df = state_metrics_df.nlargest(n=5, columns=metric)
    else:
        df = state_metrics_df.nsmallest(n=5, columns=metric)

    data = [go.Bar(x=df[metric], y=df['state'], orientation='h')]

    if largest:
        layout = go.Layout(
            title=f'States with highest {metric}',
            yaxis=dict(autorange="reversed")
        )
    else:
        layout = go.Layout(
            title=f'States with lowest {metric}',
            yaxis = dict(autorange="reversed")
        )
    fig = go.Figure(data,layout)
    fig.show()

# for metric in state_metrics_df.columns:
#     if metric not in ['state', 'population']:
#         plot_metric(state_metrics_df, metric)
#         plot_metric(state_metrics_df, metric, largest=False)
