# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import requests
from dash.dependencies import Input, Output
from dash_table.Format import Format

BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
url = 'https://covid19api.herokuapp.com/'
data_requests = requests.get(url)
json_data = data_requests.json()
latest = json_data['latest']
confirmedCases = latest['confirmed']
deathsCases = latest['deaths']
recoveredCases = latest['recovered']
remainCases = confirmedCases - (deathsCases + recoveredCases)
latestDate = json_data['updatedAt']

app = dash.Dash(__name__,
                assets_folder='./assets/',
                external_stylesheets=[BS],
                )

app.title = 'Coronavirus COVID-19 Global Monitor'
columns = ['Country', 'Confirmed', 'Deaths', 'Recovered']
conf_list, reco_list, death_list = [], [], []
confirmed, recovered, death = {}, {}, {}
types = ['confirmed', 'deaths', 'recovered']
for data_type in types:
    for data in json_data[data_type]['locations']:
        if data_type == 'confirmed':
            country = data['country']
            if country in confirmed:
                confirmed[country] += data['latest']
            else:
                confirmed[country] = data['latest']
            if data['province'] == 'nan':
                province = country
                continue
            else:
                province = data['province']
            # total = sorted(data['history'].values(), reverse=True)[0]
            conf_list.append((province, country, data['latest']))
        elif data_type == 'recovered':
            country = data['country']
            if country in recovered:
                recovered[country] += data['latest']
            else:
                recovered[country] = data['latest']
            if data['province'] == 'nan':
                province = country
                continue
            else:
                province = data['province']
            # total = sorted(data['history'].values(), reverse=True)[0]
            reco_list.append((province, country, data['latest']))
        elif data_type == 'deaths':
            country = data['country']
            if country in death:
                death[country] += data['latest']
            else:
                death[country] = data['latest']
            if data['province'] == 'nan':
                province = country
                continue
            else:
                province = data['province']
            # total = sorted(data['history'].values(), reverse=True)[0]
            death_list.append((province, country, data['latest']))
conf_cols = ['Country', 'Confirmed']
recover_cols = ['Country', 'Recovered']
death_cols = ['Country', 'Deaths']
confirmed_df = pd.DataFrame(zip(confirmed.keys(), confirmed.values()), columns=conf_cols)
recovered_df = pd.DataFrame(zip(recovered.keys(), recovered.values()), columns=recover_cols)
death_df = pd.DataFrame(zip(death.keys(), death.values()), columns=death_cols)
WorldwildTable = confirmed_df.merge(recovered_df, how='outer', on='Country').merge(death_df, how='outer', on='Country')
WorldwildTable['Active'] = WorldwildTable['Confirmed'] - WorldwildTable['Deaths'] - WorldwildTable['Recovered']
WorldwildTable = WorldwildTable.sort_values(
    by=['Confirmed'], ascending=False).reset_index(drop=True)
WorldwildTable['id'] = WorldwildTable['Country']
WorldwildTable.set_index('id', inplace=True, drop=False)
cols = ['Country', 'Active', 'Confirmed', 'Recovered', 'Deaths']
WorldwildTable = WorldwildTable[cols]

conf_cols = ['Province', 'Country', 'Confirmed']
recover_cols = ['Province', 'Country', 'Recovered']
death_cols = ['Province', 'Country', 'Deaths']

confirmed_df = pd.DataFrame(conf_list, columns=conf_cols)
recovered_df = pd.DataFrame(reco_list, columns=recover_cols)
death_df = pd.DataFrame(death_list, columns=death_cols)
df_sunburst = confirmed_df.merge(recovered_df, how='inner', on=['Province', 'Country']).merge(death_df, how='inner',
                                                                                              on=['Province',
                                                                                                  'Country'])
df_sunburst['Active'] = df_sunburst['Confirmed'] - df_sunburst['Deaths'] - df_sunburst['Recovered']
server = app.server
app.config[
    'suppress_callback_exceptions'] = True
app.layout = html.Div(
    id='app-body',
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(
                    id='herder-title',
                    children="Coronavirus (COVID-19) Outbreak Monitor"),
                html.P(
                    className='time-stamp',
                    children="Last update: {}.".format(latestDate),
                    style={'text-align': 'center'}
                ),
                html.Hr(
                ),
            ]
        ),
        html.Div(
            className="number-plate",
            children=[
                html.Div(
                    className='number-plate-single',
                    id='number-plate-active',
                    style={'border-top': '#000000 solid .2rem', },
                    children=[
                        html.H5(
                            style={'color': '#000000'},
                            children="Active cases"
                        ),
                        html.H3(
                            style={'color': '#000000'},
                            children=[
                                '{:,d}'.format(remainCases),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    className='number-plate-single',
                    id='number-plate-confirm',
                    style={'border-top': '#000000 solid .2rem', },
                    children=[
                        html.H5(
                            style={'color': '#000000'},
                            children="Confirmed cases"
                        ),
                        html.H3(
                            style={'color': '#000000'},
                            children=[
                                '{:,d}'.format(confirmedCases),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    className='number-plate-single',
                    id='number-plate-recover',
                    style={'border-top': '#000000 solid .2rem', },
                    children=[
                        html.H5(
                            style={'color': '#000000'},
                            children="Recovered cases"
                        ),
                        html.H3(
                            style={'color': '#000000'},
                            children=[
                                '{:,d}'.format(recoveredCases),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    className='number-plate-single',
                    id='number-plate-death',
                    style={'border-top': '#000000 solid .2rem', },
                    children=[
                        html.H5(
                            style={'color': '#000000'},
                            children="Death cases"
                        ),
                        html.H3(
                            style={'color': '#000000'},
                            children=[
                                '{:,d}'.format(deathsCases),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            className='section-line',
            children=[
                html.Hr(
                ),
            ]
        ),
        html.Div(
            className='dcc-table',
            children=[
                html.H5(
                    id='dcc-table-header',
                    children='Covid-19 Cases WorldWide Summary'
                ),
                dcc.Tabs(
                    id="tabs-table",
                    value='Worldwide',
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                        dcc.Tab(
                            label='Worldwide',
                            value='Worldwide',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            children=[
                                dash_table.DataTable(
                                    # id='datatable-interact-location',
                                    # Don't show coordinates
                                    columns=[{"name": 'Country', "id": 'Country'}] +
                                            [{"name": i, "id": i,
                                              'type': 'numeric',
                                              'format': Format(group=',')}
                                             for i in WorldwildTable.columns[1:5]],
                                    # But still store coordinates in the table for interactivity
                                    data=WorldwildTable.to_dict("rows"),
                                    # css= [{'selector': 'tr:hover', 'rule': 'background-color: #2674f6;'}],
                                    row_selectable="single",
                                    sort_action="native",
                                    style_as_list_view=True,
                                    style_cell={
                                        'fontFamily': 'Roboto',
                                        'backgroundColor': '#ffffff',
                                    },
                                    fixed_rows={
                                        'headers': True, 'data': 0},
                                    style_table={
                                        'minHeight': '400px',
                                        'height': '400px',
                                        'maxHeight': '400px',
                                        'overflowX': 'auto',
                                    },
                                    style_header={
                                        'backgroundColor': '#ffffff',
                                        'fontWeight': 'bold'
                                    },
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'Country'}, 'width': '35%'},
                                        {'if': {'column_id': 'Active'}, 'width': '18%'},
                                        {'if': {'column_id': 'Confirmed'}, 'width': '18%'},
                                        {'if': {'column_id': 'Recovered'}, 'width': '18%'},
                                        {'if': {'column_id': 'Deaths'}, 'width': '18%'},
                                        {'if': {'column_id': 'Active'}, 'color': '#f0953f'},
                                        {'if': {'column_id': 'Confirmed'}, 'color': '#f03f42'},
                                        {'if': {'column_id': 'Recovered'}, 'color': '#2ecc77'},
                                        {'if': {'column_id': 'Deaths'}, 'color': '#7f7f7f'},
                                        {'textAlign': 'center'}
                                    ],
                                )
                            ]
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            className='dcc-plot',
            id='sunburst-chart',
            children=[
                html.Div(
                    className='dcc-sub-plot sunburst-ternary-plot',
                    children=[
                        html.Div(
                            className='header-container',
                            children=[
                                html.H5(
                                    children='Sunburst Chart | Worldwide'
                                ),
                            ]
                        ),
                        dcc.Dropdown(
                            id="sunburst-dropdown",
                            placeholder="Select a metric",
                            value='Confirmed',
                            searchable=False,
                            clearable=False,
                            options=[{'label': 'Active cases', 'value': 'Active'},
                                     {'label': 'Confirmed cases', 'value': 'Confirmed'},
                                     {'label': 'Recovered cases', 'value': 'Recovered'},
                                     {'label': 'Deaths', 'value': 'Deaths'},
                                     ]
                        ),
                        dcc.Graph(
                            id='dropdown-sunburst-plots',
                            style={'height': '500px'},
                            config={"displayModeBar": False, "scrollZoom": False},
                        ),
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(Output('dropdown-sunburst-plots', 'figure'),
              [Input('sunburst-dropdown', 'value')])
def render_sunburst_plot(metric):
    colorTheme = px.colors.qualitative.Safe

    if metric == 'Confirmed':
        hovertemplate = '<b>%{label} </b> <br><br>Confirmed: %{value} cases'
    elif metric == 'Recovered':
        hovertemplate = '<b>%{label} </b> <br>Recovered: %{value} cases'
    elif metric == 'Deaths':
        hovertemplate = '<b>%{label} </b> <br>Deaths: %{value} cases'
    elif metric == 'Active':
        hovertemplate = '<b>%{label} </b> <br>Active: %{value} cases'

    fig_sunburst = px.sunburst(
        df_sunburst,
        path=['Country', 'Province'],
        values=metric,
        hover_data=[metric],
        color_discrete_sequence=colorTheme,
    )

    fig_sunburst.update_traces(
        textinfo='label+percent root',
        hovertemplate=hovertemplate
    )
    fig_sunburst.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=-0.2,
                xref='paper',
                yref='paper',
                text='Click to unfold segment',
                showarrow=False,
                font=dict(
                    family='Roboto, sans-serif',
                    size=16,
                    color="#292929"
                ),
            )
        ]
    )

    return fig_sunburst


if __name__ == "__main__":
    app.run_server(host="0.0.0.0")
