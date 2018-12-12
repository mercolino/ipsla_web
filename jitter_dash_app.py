import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from lib.utils import grab_hostnames, grab_ipslas, grab_graph_data, grab_all_data
import pandas as pd
from datetime import datetime
import json
from flask_app import app
import plotly.figure_factory as ff


app_dash = dash.Dash(name='jitter_dash_app', sharing=True, server=app, url_base_pathname='/jitter-dashboard/',
                     assets_external_path='/static/assets')
app_dash.config['suppress_callback_exceptions'] = True
app_dash.css.append_css({'external_url': '/static/css/bootstrap.css'})
app_dash.css.append_css({'external_url': '/static/assets/custom.css'})


def serve_layout():
    # Creating Host Dropdown
    hosts = grab_hostnames()
    host_dropdown = []
    for host in hosts:
        host_dropdown.append({'label': host[0], 'value': host[0]})

    if len(host_dropdown) == 0:
        ipsla_dropdown = []
    else:
        ipslas = grab_ipslas(host_dropdown[0]['value'])
        ipsla_dropdown = []
        for ipsla in ipslas:
            ipsla_dropdown.append({'label': ipsla[0] + ' ( ' + ipsla[1] + ' )', 'value': ipsla[0]})

    layout = html.Div(children=[

        # Navbar
        html.Div([
            html.Div([
                html.Nav([
                    # Adding Logo
                    html.A([
                        html.Img(src='/static/images/logo.png', style={'max-width': '40px',
                                                                       'margin-top': '-10px',
                                                                       'margin-right': '10px'}),
                        'IP Sla'
                    ], className='navbar-brand', href='#'),
                    # Navigation Pills
                    html.Ul([
                        html.Li([
                            html.A([
                                'Home'
                            ], className='nav-link', href='/'),
                        ], className='nav-item'),
                        html.Li([
                            html.A([
                                'Configuration'
                            ], className='nav-link', href='/config'),
                        ], className='nav-item'),
                    ], className='navbar-nav nav-pills'),
                    html.Ul([
                        html.Li([
                            html.A([
                                'Echo Dash'
                            ], className='nav-link', href='/echo-dash'),
                        ], className='nav-item'),
                        html.Li([
                            html.A([
                                'Jitter Dash'
                            ], className='nav-link active', href='/jitter-dash'),
                        ], className='nav-item'),
                    ], className='navbar-nav nav-pills ml-auto'),
                ], className='navbar navbar-shadow fixed-top navbar-expand-sm navbar-light', style={'background-color': '#e3f2fd'}),
            ], className='col-12'),
        ], className='row'),

        html.Div([
            html.Div([
                html.Div([
                    html.H2(children='Echo IP Sla Dashboard'),
                ], className='col-12 text-center'),
            ], className='row'),

            # Date Picker
            html.Div([
                html.Div([
                    html.Label('Date Range')
                ], className='col-4'),
            ], className='row'),
            html.Div([
                # Date Ranger Picker Component
                html.Div([
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        initial_visible_month=datetime.now().date(),
                        start_date=datetime.now().date(),
                        end_date=datetime.now().date()
                    ),
                ], className='col-3'),
                # Checkboxes
                html.Div([
                    dcc.Checklist(
                        id='graph_statistics_checkbox',
                        options=[
                            {'label': ' Graph Statistics', 'value': 'graph_statistics_checkbox'},
                        ],
                        values=['']
                    ),
                    dcc.Checklist(
                        id='raw_data_checkbox',
                        options=[
                            {'label': ' Show Raw Data Table', 'value': 'raw_data_checkbox'},
                        ],
                        values=['']
                    ),
                ], className='col-4'),
            ], className='row mb-1'),

            # Host and ipsla Dropdown
            html.Div([
                # Host Dropdown
                html.Div([
                    html.Label('Host'),
                    dcc.Dropdown(
                        id='host',
                        options=host_dropdown,
                    ),
                ], className='col-2'),
                # IP Sla Dropdown
                html.Div([
                    html.Label('Echo Ip Sla'),
                    dcc.Dropdown(
                        id='ipsla',
                        options=ipsla_dropdown,
                    ),
                ], className='col-3'),
                # Reserved Space
                html.Div([
                    html.Label('Averages'),
                    dcc.Dropdown(
                        options=[
                            {'label': 'No Average', 'value': ''},
                            {'label': 'Hourly', 'value': 'H'},
                            {'label': 'Daily', 'value': 'D'},
                            {'label': 'Weekly', 'value': 'W'},
                            {'label': 'Monthly', 'value': 'M'},
                        ],
                        value='',
                        searchable=False,
                        clearable=False,
                        id='averages',
                    ),
                ], className='col-2'),
                # Refresh Button
                html.Div([
                    html.Button('Refresh', id='refresh_button', className='btn btn-success mr-2'),
                    html.Button('Add to Compare', id='add_compare_button', className='btn btn-warning mr-2'),
                    html.Button('Clear Comparison', id='clear_compare_button', className='btn btn-danger'),
                ], className='col-5 align-self-end text-center'),
            ], className='row'),

            html.Hr([], className='mt-2 mb-2'),

            html.Div([
                html.Div([
                    html.H3('Graph')
                ], id='graph-title', className='col-12 text-center mt-3', style={'display': 'none'}),
            ], className='row'),

            # rtt graph placeholder
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='graph_ipsla',
                            animate=False,
                        ),
                    ], id='graph', style={}),
                ], className='col-12'),
            ], className='row'),

            html.Div([
                html.Div([
                    html.H3('Statistics')
                ], id='table-title', className='col-12 text-center mt-3', style={'display': 'none'}),
            ], className='row'),

            # table placeholder
            html.Div([
                html.Div([
                    dash_table.DataTable(
                        id='ipsla_table',
                        columns=[
                            {'name': 'Data Range', 'id': "date_range"},
                            {'name': 'Number of Points', 'id': "number_points"},
                            {'name': 'Avg(min rtt)', 'id': "min_avg_rtt"},
                            {'name': 'Min(avg rtt)', 'id': "min_rtt"},
                            {'name': 'Avg rtt', 'id': "avg_rtt"},
                            {'name': 'Max(avg rtt)', 'id': "max_rtt"},
                            {'name': 'Avg(max rtt)', 'id': "max_avg_rtt"},
                            {'name': 'Std Dev Avg rtt', 'id': "std_rtt"},
                        ],
                        style_cell={'textAlign': 'center'},
                    )
                ], id='table', className='col-12', style={'display': 'none'}),
            ], className='row'),

            # Statistics graph placeholder
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='graph_statistics',
                            animate=False,
                        ),
                    ], id='graph_statistics_placeholder', className='col-12', style={}),
                ], className='col-12'),
            ], className='row'),

            html.Hr([], id='comparison_separation_line', className='mt-3 mb-3 d-none'),

            # Comparison Graph placeholder
            html.Div([
                html.Div(id='comparison-list', className='col-12'),
            ], className='row'),

            # Comparison Graph placeholder
            html.Div([
                html.Div(id='comparison-graph', className='col-12'),
            ], className='row'),

            html.Div([
                html.Hr([], className='mt-3 mb-3'),
                html.Div([
                    html.H3('Raw Data Table')
                ], className='col-12 text-center mt-2, bg-info'),
            ], id='raw_data_div', className='d-none'),


            # Raw Data Table placeholder
            html.Div([
                html.Div(id='raw_data_table', className='col-12'),
            ], className='row'),

            # Hidden div inside the app that stores the data
            html.Div(id='shared-data', style={'display': 'none'}),

            # Hidden div inside the app that stores relayout state
            html.Div(id='relayout-data', style={'display': 'none'}),

            # Hidden div inside the app that shared dataframes for comparison
            html.Div(id='shared-data-comparison', style={'display': 'none'}),

            # Hidden div inside the app that shared the previous state of the buttons
            html.Div(id='button-states', style={'display': 'none'}),
        ], style={'padding-top': '70px'})
    ], className='container-fluid')

    return layout


app_dash.layout = serve_layout


# Function to populate the ipsla dropdown depending on the host selected
@app_dash.callback(dash.dependencies.Output('ipsla', 'options'),
                   [dash.dependencies.Input('host', 'value')])
def update_ipsla_dropdown(h):
    if h is not None:
        ipslas = grab_ipslas(h)
        ipsla_dropdown = []
        for ipsla in ipslas:
            if ipsla[2] in ['9']:
                ipsla_dropdown.append({'label': ipsla[0] + ' ( ' + ipsla[1] + ' )', 'value': ipsla[0]})

        return ipsla_dropdown
    else:
        return []


# Function to save the state of the comparison buttons
@app_dash.callback(dash.dependencies.Output('button-states', 'children'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                       dash.dependencies.Input('clear_compare_button', 'n_clicks'),
                   ],
                   )
def save_button_states(n, c):
    state = {'add': n, 'clear': c}

    return json.dumps(state)


# Function to add the data for comparison
@app_dash.callback(dash.dependencies.Output('shared-data-comparison', 'children'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                       dash.dependencies.Input('clear_compare_button', 'n_clicks'),
                   ],
                   [
                       dash.dependencies.State('shared-data', 'children'),
                       dash.dependencies.State('shared-data-comparison', 'children'),
                       dash.dependencies.State('button-states', 'children'),
                   ],
                   )
def data_comparison(n, c, df_json, previous_data, previous_state):
    if previous_state is not None:
        previous_state = json.loads(previous_state)

        if previous_state['clear'] != c:
            return

    if df_json is not None:
        if previous_data is not None:
            dataset_list = json.loads(previous_data)
            dataframe = pd.read_json(df_json)
            string = dataframe['host'][0] + '(' + dataframe['ipsla_type'][0] + ',' + str(
                dataframe['ipsla_index'][0]) + ')'
            if string in dataset_list:
                return previous_data
            else:
                dataset_list[string] = df_json
                dataset_compare = json.dumps(dataset_list)
        else:
            dataset_list = {}
            dataframe = pd.read_json(df_json)
            string = dataframe['host'][0] + '(' + dataframe['ipsla_type'][0] + ',' + str(
                dataframe['ipsla_index'][0]) + ')'
            dataset_list[string] = dataframe.to_json(date_format='iso')
            dataset_compare = json.dumps(dataset_list)

        return dataset_compare
    else:
        return previous_data


# Function to grab the data and pass it to other callbacks,more efficient
@app_dash.callback(dash.dependencies.Output('shared-data', 'children'),
                   [
                       dash.dependencies.Input('host', 'value'),
                       dash.dependencies.Input('ipsla', 'value'),
                       dash.dependencies.Input('averages', 'value'),
                       dash.dependencies.Input('date-picker-range', 'start_date'),
                       dash.dependencies.Input('date-picker-range', 'end_date'),
                       dash.dependencies.Input('refresh_button', 'n_clicks'),
                   ])
def data(h, i, a, sd, ed, n):
    if (h is not None) and (i is not None):

        sd_datetime = sd + ' 00:00:00'
        ed_datetime = ed + ' 23:59:59'

        try:
            ipsla_type, dataframe = grab_graph_data(h, i, sd_datetime, ed_datetime, a)
        except Exception as e:
            print(e)
            return pd.DataFrame().to_json()

        if not dataframe.empty:
            dataframe['ipsla_type'] = ipsla_type
            dataframe['ipsla_index'] = i
            dataframe['host'] = h
            return dataframe.to_json(date_format='iso')


# Callback Function to save previous state of relayout
@app_dash.callback(dash.dependencies.Output('relayout-data', 'children'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'relayoutData'),
                   ])
def save_relayout_state(r):

    return json.dumps(r)


# Function to show the graph title
@app_dash.callback(dash.dependencies.Output('graph-title', 'style'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'figure'),
                   ])
def graph_title(fig):
    if bool(fig):
        return {}
    else:
        return {'display': 'none'}


# Function to show the graph
@app_dash.callback(dash.dependencies.Output('graph', 'style'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'figure'),
                   ])
def show_graph(fig):
    if bool(fig):
        return {}
    else:
        return {'display': 'none'}


# Function to graph the data
@app_dash.callback(dash.dependencies.Output('graph_ipsla', 'figure'),
                   [
                       dash.dependencies.Input('shared-data', 'children'),
                   ])
def graph(df_json):
    if df_json is not None:

        dataframe = pd.read_json(df_json)

        if not dataframe.empty:
            ipsla_type = dataframe['ipsla_type'].unique()[0]
            i = dataframe['ipsla_index'].unique()[0]
            h = dataframe['host'].unique()[0]

            # Add min to the dataframe
            dataframe['min'] = dataframe['latest_rtt'].min()

            # Add average to the dataframe
            dataframe['avg'] = dataframe['latest_rtt'].mean()

            # Add max to the dataframe
            dataframe['max'] = dataframe['latest_rtt'].max()

            return {
                'data': [
                    {
                        'x': dataframe.index,
                        'y': dataframe['latest_rtt'],
                        'type': 'line',
                        'name': 'avg rtt',
                        'connectgaps': False
                    },
                    {
                        'x': dataframe.index,
                        'y': dataframe['min_rtt'],
                        'type': 'line',
                        'name': 'min rtt',
                        'connectgaps': False
                    },
                    {
                        'x': dataframe.index,
                        'y': dataframe['max_rtt'],
                        'type': 'line',
                        'name': 'max rtt',
                        'connectgaps': False
                    },
                    {
                        'x': dataframe.index,
                        'y': dataframe['min'],
                        'type': 'line',
                        'name': 'min(avg rtt)',
                        'line': {'width': 0.5}
                    },
                    {
                        'x': dataframe.index,
                        'y': dataframe['avg'],
                        'type': 'line',
                        'name': 'avg(avg rtt)',
                        'line': {'width': 0.5}
                    },
                    {
                        'x': dataframe.index,
                        'y': dataframe['max'],
                        'type': 'line',
                        'name': 'max(avg rtt)',
                        'line': {'width': 0.5}
                    },
                ],
                'layout': {
                    'height': 600,
                    'title': '{type} Ip Sla {ipsla} for host {host}'.format(
                        type=ipsla_type[0].upper() + ipsla_type[1:],
                        ipsla=i,
                        host=h),
                    'xaxis': {
                        'title': 'DateTime',
                        'autorange': True,
                        'rangeselector': {
                            'buttons': [
                                {'count': 15, 'label': '15m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 30, 'label': '30m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1d', 'step': 'day', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1wk', 'step': 'week', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1y', 'step': 'year', 'stepmode': 'backward'},
                                {'step': 'all'}
                            ]
                        },
                        'rangeslider': {'type': 'date', 'visible': True},
                    },
                    'yaxis': {'title': 'Milliseconds', 'autorange': True},
                }
            }
        else:
            return {
                'data': [],
                'layout': {
                    'title': 'No Data to Graph!!!',
                    'font': {
                        'size': 18,
                        'color': '#ff0000'
                    }
                },
            }
    else:
        return {}


# Function to show the graph
@app_dash.callback(dash.dependencies.Output('graph_statistics_placeholder', 'style'),
                   [
                       dash.dependencies.Input('graph_statistics', 'figure'),
                   ])
def show_graph_statistics(fig):
    if bool(fig):
        return {}
    else:
        return {'display': 'none'}


# Function to graph the data
@app_dash.callback(dash.dependencies.Output('graph_statistics', 'figure'),
                   [
                       dash.dependencies.Input('shared-data', 'children'),
                       dash.dependencies.Input('graph_statistics_checkbox', 'values'),
                   ],)
def graph_statistics(df_json, checkbox_values):
    if len(checkbox_values) == 2 and df_json is not None:
        dataframe = pd.read_json(df_json)
        ipsla_type = dataframe['ipsla_type'].unique()[0]
        i = dataframe['ipsla_index'].unique()[0]
        h = dataframe['host'].unique()[0]

        try:
            fig = ff.create_distplot([dataframe['latest_rtt'].dropna().tolist(), ], ['rtt', ])

            fig['layout'].update(title='RTT Statistics for {type} Ip Sla {ipsla} in host {host}'.format(
                type=ipsla_type[0].upper() + ipsla_type[1:],
                ipsla=i,
                host=h),)
        except Exception as e:
            print(e)
            fig = {
                'data': [],
                'layout': {
                    'title': 'No statistic graph can be done for Ip Sla {ipsla} in host {host}'.format(
                        ipsla=i, host=h),
                    'font': {
                        'size': 18,
                        'color': '#ff0000'
                    }
                }
            }

        return fig
    else:
        return {}


# Function to show table title
@app_dash.callback(dash.dependencies.Output('table-title', 'style'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'figure')
                   ])
def table_title(fig):
    if bool(fig):
        return {}
    else:
        return {'display': 'none'}


# Function to showthe table
@app_dash.callback(dash.dependencies.Output('table', 'style'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'figure')
                   ])
def show_table(fig):
    if bool(fig):
        return {}
    else:
        return {'display': 'none'}


# Callback to create/update the Table
@app_dash.callback(dash.dependencies.Output('ipsla_table', 'data'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'relayoutData'),
                       dash.dependencies.Input('shared-data', 'children'),
                   ],
                   [
                       dash.dependencies.State('relayout-data', 'children')
                   ])
def statistics_table(r, df_json, pr):

    if df_json is not None:
        if r is None:
            return

        dummy = ''

        # Check if actual relayout is the same as teh previous one, if it is, something changed on other
        # variables and need to reset calc.
        if json.dumps(r) != pr:
            for key in r:
                if key == 'xaxis.range':
                    dummy = key
                    break
                elif key == 'xaxis.range[0]':
                    dummy = key
                    break

        dataframe = pd.read_json(df_json)

        if not dataframe.empty:
            if dummy == 'xaxis.range':
                sd = pd.to_datetime(r['xaxis.range'][0])
                ed = pd.to_datetime(r['xaxis.range'][1])
                dataframe = dataframe.loc[(dataframe.index > sd) & (dataframe.index <= ed)]
            elif dummy == 'xaxis.range[0]':
                sd = pd.to_datetime(r['xaxis.range[0]'])
                ed = pd.to_datetime(r['xaxis.range[1]'])
                dataframe = dataframe.loc[(dataframe.index > sd) & (dataframe.index <= ed)]
            else:
                sd = dataframe.index.min()
                ed = dataframe.index.max()

                # Add min to the dataframe
                min_avg = dataframe['min_rtt'].mean()

                # Add min to the dataframe
                minimum = dataframe['latest_rtt'].min()

                # Add average to the dataframe
                avg = dataframe['latest_rtt'].mean()

                # Add average to the dataframe
                std = dataframe['latest_rtt'].std()

                # Add max to the dataframe
                maximum = dataframe['latest_rtt'].max()

                # Add min to the dataframe
                max_avg = dataframe['max_rtt'].mean()

                return [
                    {
                        'date_range': sd.strftime('%Y-%m-%d %H:%M:%S') + ' --> ' + ed.strftime('%Y-%m-%d %H:%M:%S'),
                        'number_points': len(dataframe.index),
                        'min_avg_rtt': min_avg,
                        'min_rtt': minimum,
                        'avg_rtt': avg,
                        'max_rtt': maximum,
                        'max_avg_rtt': max_avg,
                        'std_rtt': std,

                    }
                ]
        else:
            return [
                {
                    'date_range': 'No Data',
                    'number_points': 'No Data',
                    'min_rtt': 'No Data',
                    'avg_rtt': 'No Data',
                    'std_rtt': 'No Data',
                    'max_rtt': 'No Data'
                }
            ]
    else:
        return []


# Function to add to the dropdown the data for the comparison graph
@app_dash.callback(dash.dependencies.Output('comparison-list', 'children'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                       dash.dependencies.Input('shared-data-comparison', 'children'),
                   ],)
def comparison_list(n, json_list):
    if json_list is not None:
        value_list = json.loads(json_list)
        compare_list = ''
        for value in value_list:
            compare_list = value + ' | ' + compare_list

        return [
            html.Div([
                html.H3('Comparison Graph')
            ], className='col-12 text-center mt-2, bg-info'),
            html.Div([
                'Comparing: | ' + compare_list
            ], className='col-12 mt-3 bg-dark text-white'),
        ]
    else:
        return []


# Show separation Line
@app_dash.callback(dash.dependencies.Output('comparison_separation_line', 'className'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                       dash.dependencies.Input('clear_compare_button', 'n_clicks')
                   ],
                   [
                       dash.dependencies.State('button-states', 'children')
                   ])
def show_comparison_separation_line(n, c, s):
    if s is not None:
        state = json.loads(s)
    if n is None or c != state['clear']:
        return 'mt-5 mb-5 d-none'
    else:
        return 'mt-5 mb-5'

# Function to a graph the comparison graph
@app_dash.callback(dash.dependencies.Output('comparison-graph', 'children'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                       dash.dependencies.Input('shared-data-comparison', 'children'),
                   ],)
def comparison_graph(n, json_list):
    if json_list is not None:
        value_list = json.loads(json_list)
        ipsla_data = []
        for value in value_list:
            dataframe = pd.read_json(value_list[value])
            ipsla_data.append(
                {'x': dataframe.index, 'y': dataframe['latest_rtt'], 'type': 'line', 'name': value},
            )

        children = [
            dcc.Graph(
                id='comparison_graph_ipsla',
                animate=False,
                figure={
                    'data': ipsla_data,
                    'layout': {
                        'height': 600,
                        'xaxis': {
                            'title': 'DateTime',
                            'autorange': True,
                            'rangeselector': {
                                'buttons': [
                                    {'count': 15, 'label': '15m', 'step': 'minute', 'stepmode': 'backward'},
                                    {'count': 30, 'label': '30m', 'step': 'minute', 'stepmode': 'backward'},
                                    {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                    {'count': 1, 'label': '1d', 'step': 'day', 'stepmode': 'backward'},
                                    {'count': 1, 'label': '1wk', 'step': 'week', 'stepmode': 'backward'},
                                    {'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                    {'count': 1, 'label': '1y', 'step': 'year', 'stepmode': 'backward'},
                                    {'step': 'all'}
                                ]
                            },
                            'rangeslider': {'type': 'date', 'visible': True},
                        },
                        'yaxis': {'title': 'Milliseconds', 'autorange': True},
                    }
                }
            ),
        ]
        return children
    else:
        return []


# Function to show the Raw Data separation line
@app_dash.callback(dash.dependencies.Output('raw_data_div', 'className'),
                   [
                       dash.dependencies.Input('raw_data_table', 'children'),
                   ])
def show_graph_statistics(table):
    if bool(table):
        return ''
    else:
        return 'd-none'


# Callback to create/update the Table
@app_dash.callback(dash.dependencies.Output('raw_data_table', 'children'),
                   [
                       dash.dependencies.Input('host', 'value'),
                       dash.dependencies.Input('ipsla', 'value'),
                       dash.dependencies.Input('averages', 'value'),
                       dash.dependencies.Input('date-picker-range', 'start_date'),
                       dash.dependencies.Input('date-picker-range', 'end_date'),
                       dash.dependencies.Input('refresh_button', 'n_clicks'),
                       dash.dependencies.Input('raw_data_checkbox', 'values')
                   ])
def raw_data_table(h, i , a, sd, ed, n, rd):

    if h is not None and i is not None:
        if len(rd) == 2:

            sd_datetime = sd + ' 00:00:00'
            ed_datetime = ed + ' 23:59:59'

            dataframe = grab_all_data(h, i, sd_datetime, ed_datetime, a).dropna()

            headers = ['id', 'datetime', 'hostname', 'ipsla_index', 'type', 'tag','threshold', 'timeout', 'frequency',
                       'target_address', 'source_address', 'latest_rtt', 'return_code', 'sysuptime', 'time']

            dataframe = dataframe[headers]

            return [
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in dataframe.columns],
                    style_cell={'textAlign': 'center'},
                    data=dataframe.to_dict("rows")
                )
            ]