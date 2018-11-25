from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, IPAddress
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from lib.utils import cons_ipsla_types, grab_all_polls, delete_polls
#from lib.utils import ipsla_search, create_polling, insert_polling_data
from lib.utils import grab_hostnames, grab_ipslas, grab_graph_data
import pandas as pd
from datetime import datetime
import json


def serve_layout():
    # Creating Host Dropdown
    hosts = grab_hostnames()
    host_dropdown = []
    for host in hosts:
        host_dropdown.append({'label': host[0], 'value': host[0]})

    ipslas = grab_ipslas(host_dropdown[0]['value'])
    ipsla_dropdown = []
    for ipsla in ipslas:
        ipsla_dropdown.append({'label': ipsla[0] + ' ( ' + ipsla[1] + ' )', 'value': ipsla[0]})

    layout = html.Div(children=[
        html.Div([
            html.Div([
            ], className='col-2'),

            html.Div([
                html.H1(children='Cisco Ip Sla'),
            ], className='col-8 text-center'),

            html.Div([
                html.A(html.Button('Home', className='btn btn-primary'), href='/'),
            ], className='col-2 text-center align-self-center'),
        ], className='row bg-info'),

        html.Div([
            html.Div([
            ], className='col-2'),

            html.Div([
                html.H2(children='Dashboard'),
            ], className='col-8 text-center'),

            html.Div([
            ], className='col-2'),
        ], className='row'),

        # Date Picker
        # Date Picker
        html.Div([
            html.Div([
                html.Label('Date Range')
            ], className='col-4'),
        ], className='row mt-3'),
        html.Div([
            # Date Ranger Picker Component
            html.Div([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    initial_visible_month=datetime.now().date(),
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date()
                ),
            ], className='col-4'),
        ], className='row mb-3'),

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
                html.Label('Ip Sla'),
                dcc.Dropdown(
                    id='ipsla',
                    options=ipsla_dropdown,
                ),
            ], className='col-2'),
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
                    id='averages',
                ),
            ], className='col-2'),
            # Refresh Button
            html.Div([
                html.Button('Refresh', id='refresh_button', className='btn btn-success mr-2'),
                html.Button('Add to Compare', id='add_compare_button', className='btn btn-warning mr-2'),
                html.Button('Clear Comparison', id='clear_compare_button', className='btn btn-danger'),
            ], className='col-6 align-self-end text-center'),
        ], className='row'),

        # graph placeholder
        html.Div([
            html.Div(id='graph', className='col-12'),
        ], className='row'),

        # table placeholder
        html.Div([
            html.Div(id='table', className='col-12'),
        ], className='row'),

        html.Hr([], className='mt-5 mb-5'),

        # Comparison Graph placeholder
        html.Div([
            html.Div(id='comparison-list', className='col-12'),
        ], className='row'),

        # Comparison Graph placeholder
        html.Div([
            html.Div(id='comparison-graph', className='col-12'),
        ], className='row'),

        # Hidden div inside the app that stores the data
        html.Div(id='shared-data', style={'display': 'none'}),

        # Hidden div inside the app that stores relayout state
        html.Div(id='relayout-data', style={'display': 'none'}),

        # Hidden div inside the app that shared dataframes for comparison
        html.Div(id='shared-data-comparison', style={'display': 'none'}),

        # Hidden div inside the app that shared the previous state of the buttons
        html.Div(id='button-states', style={'display': 'none'}),

    ], className='container-fluid')

    return layout


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xxzSEO8jlCZt856qPayi'


app_dash = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
app_dash.config['suppress_callback_exceptions'] = True
app_dash.css.append_css({'external_url': '/static/css/bootstrap.css'})

app_dash.layout = serve_layout()


# Function to populate the ipsla dropdown depending on the host selected
@app_dash.callback(dash.dependencies.Output('ipsla', 'options'),
                   [dash.dependencies.Input('host', 'value')])
def update_ipsla_dropdown(h):
    if h is not None:
        ipslas = grab_ipslas(h)
        ipsla_dropdown = []
        for ipsla in ipslas:
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
def data_comparison(n, c):
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
            dataframe= pd.read_json(df_json)
            string = dataframe['host'][0] + '(' + dataframe['ipsla_type'][0] + ',' + str(
                dataframe['ipsla_index'][0]) + ')'
            dataset_list[string] =dataframe.to_json(date_format='iso')
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

        ipsla_type, dataframe = grab_graph_data(h, i, sd_datetime, ed_datetime, a)

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



# Function to graph the data
@app_dash.callback(dash.dependencies.Output('graph', 'children'),
                   [
                       dash.dependencies.Input('shared-data', 'children'),
                   ])
def graph(df_json):
    if df_json is not None:

        dataframe = pd.read_json(df_json)
        ipsla_type = dataframe['ipsla_type'].unique()[0]
        i = dataframe['ipsla_index'].unique()[0]
        h = dataframe['host'].unique()[0]

        # Add min to the dataframe
        dataframe['min'] = dataframe['latest_rtt'].min()

        # Add average to the dataframe
        dataframe['avg'] = dataframe['latest_rtt'].mean()

        # Add max to the dataframe
        dataframe['max'] = dataframe['latest_rtt'].max()

        return [
            html.Div([
                html.H3('Graph')
            ], className='col-12 text-center mt-3'),
            dcc.Graph(
                id='graph_ipsla',
                animate=False,
                figure={
                    'data': [
                        {'x': dataframe.index, 'y': dataframe['latest_rtt'], 'type': 'line', 'name': 'rtt'},
                        {'x': dataframe.index, 'y': dataframe['min'], 'type': 'line', 'name': 'min', 'line':{'width': 0.5}},
                        {'x': dataframe.index, 'y': dataframe['avg'], 'type': 'line', 'name': 'avg', 'line':{'width': 0.5}},
                        {'x': dataframe.index, 'y': dataframe['max'], 'type': 'line', 'name': 'max', 'line':{'width': 0.5}},
                    ],
                    'layout': {
                        'height': 600,
                        'title': '{type} Ip Sla {ipsla} for host {host}'.format(type=ipsla_type[0].upper() + ipsla_type[1:],ipsla=i, host=h),
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


# Function to create the table
@app_dash.callback(dash.dependencies.Output('table', 'children'),
                   [
                       dash.dependencies.Input('shared-data', 'children')
                   ])
def table(df_json):
    if df_json is not None:
        dataframe = pd.read_json(df_json)

        # Add min to the dataframe
        min = dataframe['latest_rtt'].min()

        # Add average to the dataframe
        avg = dataframe['latest_rtt'].mean()

        # Add std to the dataframe
        std = dataframe['latest_rtt'].std()

        # Add max to the dataframe
        max = dataframe['latest_rtt'].max()

        return [
            html.Div([
                html.H3('Statistics')
            ], className='col-12 text-center'),
            dash_table.DataTable(
                id='ipsla_table',
                columns=[
                    {'name': 'Data Range', 'id': "date_range"},
                    {'name': 'Number of Points', 'id': "number_points"},
                    {'name': 'Min rtt', 'id': "min_rtt"},
                    {'name': 'Avg rtt', 'id': "avg_rtt"},
                    {'name': 'Std Dev rtt', 'id': "std_rtt"},
                    {'name': 'Max rtt', 'id': "max_rtt"},
                ],
                data=[
                    {
                        'date_range': dataframe.index.min().strftime('%Y-%m-%d %H:%M:%S') + ' --> ' + dataframe.index.max().strftime('%Y-%m-%d %H:%M:%S'),
                        'number_points': len(dataframe.index),
                        'min_rtt': min,
                        'avg_rtt': avg,
                        'std_rtt': std,
                        'max_rtt': max
                    }
                ],
                style_cell={'textAlign': 'center'},
            )
        ]


# Callback to update the Table
@app_dash.callback(dash.dependencies.Output('ipsla_table', 'data'),
                   [
                       dash.dependencies.Input('graph_ipsla', 'relayoutData'),
                   ],
                   [
                       dash.dependencies.State('shared-data', 'children'),
                       dash.dependencies.State('relayout-data', 'children')
                   ])
def update_table(r, df_json, pr):

    if r is None:
        return

    dummy = ''

    # Check if actual relayout is the same as teh previous one, if it is, something changed on other variables and need to reset calc.
    if json.dumps(r) != pr:
        for key in r:
            if key == 'xaxis.range':
                dummy = key
                break
            elif key == 'xaxis.range[0]':
                dummy = key
                break

    dataframe = pd.read_json(df_json)

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
    min = dataframe['latest_rtt'].min()

    # Add average to the dataframe
    avg = dataframe['latest_rtt'].mean()

    # Add average to the dataframe
    std = dataframe['latest_rtt'].std()

    # Add max to the dataframe
    max = dataframe['latest_rtt'].max()

    return [
        {
            'date_range': sd.strftime('%Y-%m-%d %H:%M:%S') + ' --> ' + ed.strftime('%Y-%m-%d %H:%M:%S'),
            'number_points': len(dataframe.index),
            'min_rtt': min,
            'avg_rtt': avg,
            'std_rtt': std,
            'max_rtt': max
        }
    ]


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
            ], className='col-12 text-center mt-3, bg-info'),
            html.Div([
                'Comparing: | ' + compare_list
            ], className='col-12 mt-3 bg-dark text-white'),
        ]
    else:
        return []


# Function to agraph the comparison graph
@app_dash.callback(dash.dependencies.Output('comparison-graph', 'children'),
                   [
                       dash.dependencies.Input('add_compare_button', 'n_clicks'),
                        dash.dependencies.Input('shared-data-comparison', 'children'),
                   ],)
def comparison_graph(n, json_list):
    if json_list is not None:
        value_list = json.loads(json_list)
        data=[]
        for value in value_list:
            dataframe = pd.read_json(value_list[value])
            data.append(
                {'x': dataframe.index, 'y': dataframe['latest_rtt'], 'type': 'line', 'name': value},
            )

        children = [
            dcc.Graph(
                id='comparison_graph_ipsla',
                animate=False,
                figure={
                    'data': data,
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

# Class to define the ip sla search form
class SearchIpSlaForm(FlaskForm):
    hostname = StringField('Hostname', validators=[DataRequired(), IPAddress()])
    snmp_version = StringField('SNMP Version', validators=[DataRequired()])
    community = StringField('Community', validators=[])
    security_level = StringField('Security Level', validators=[])
    security_username = StringField('Security Username', validators=[])
    auth_protocol = StringField('Authentication Protocol', validators=[])
    auth_password = StringField('Authentication Password', validators=[])
    privacy_protocol = StringField('Privacy Protocol', validators=[])
    privacy_password = StringField('Privacy Password', validators=[])

    # Custom Validations
    def validate(self):
        # Python 3 use super().validate()
        # Validate with the original validators first
        if not FlaskForm.validate(self):
            return False

        result = True

        # With snmp version 2 community should be set
        if self.snmp_version.data == '2' and self.community.data == '':
            self.community.errors.append('Community cannot be empty!')
            result = False

        if self.snmp_version.data == '3':
            # With snmp version 3 security level and username should be always set
            if self.security_username.data == '' or self.security_level.data == 'Choose...':
                self.security_level.errors.append('Security Username and/or Security Level cannot be empty!')
                self.security_username.errors.append('Security Username and/or Security Level cannot be empty!')
                result = False
            # With snmp version 3 and auth without priv auth protocol and auth password should be set
            if self.security_level.data == 'auth_without_privacy':
                if self.auth_protocol.data == 'Choose...' or self.auth_password.data == '':
                    self.auth_password.errors.append(
                        'With Auth without Privacy, Auth Prot and/or Auth Pwd cannot be empty')
                    self.auth_protocol.errors.append(
                        'With Auth without Privacy, Auth Prot and/or Auth Pwd cannot be empty')
                    result = False
            # With snmp version 3 and auth with priv everything should be set
            if self.security_level.data == 'auth_with_privacy':
                if self.auth_protocol.data == 'Choose...' or self.auth_password.data == '' or \
                        self.privacy_protocol.data == 'Choose...' or self.privacy_password.data == '':
                    self.auth_password.errors.append('With Auth with Privacy, No Field can be empty')
                    self.auth_protocol.errors.append('With Auth with Privacy, No Field can be empty')
                    self.privacy_protocol.errors.append('With Auth with Privacy, No Field can be empty')
                    self.privacy_password.errors.append('With Auth with Privacy, No Field can be empty')
                    result = False

        return result


# Main Function just the landing page for now, here plotly dashboard is going to be presented
@app.route('/')
def main():
    return render_template('main.html')


# Config page, all the ip sla's on the polling database and presented and can be added or removed
@app.route('/config', methods=['GET', 'POST'])
def config():
    # Checking if method is post because form was sent
    if request.method == 'POST':
        # Check if button remove was pressed
        if request.form.get('crud') == 'remove':
            # Gather all the checkboxes selected
            selection = request.form.getlist('selection')
            # Connect to the database if the selection was not empty
            if len(selection) != 0:
                message, message_category = delete_polls(selection)
                flash(message, message_category)
            else:
                flash('Nothing selected!. No Ip Sla\'s were removed form the polling database', 'error')

    # query all rows in the polling table of the database
    all_rows = grab_all_polls()

    # Render page
    return render_template('config.html', all_rows=all_rows, types_names=cons_ipsla_types)


# Function to search for IP Sla's
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Define form with class configured
    form = SearchIpSlaForm()
    # If Form's submit button was pressed enter
    if request.method == 'POST':
        if form.validate():
            # Connect to the host and retrieve all the ip sla data
            ipsla_indexes, ipsla_types, ipsla_tags, message, message_category = ipsla_search(form.data)
            flash(message, message_category)
            if message_category == 'error':
                return redirect('/search')
            # Save data on session to be used on ipsla function
            session['indexes'] = ipsla_indexes
            session['types'] = ipsla_types
            session['tags'] = ipsla_tags
            session['snmp_data'] = form.data
            return redirect('/ipsla')

    return render_template('search.html', form=form)


# Function to add ipsla to the database
@app.route('/ipsla', methods=['GET', 'POST'])
def ipsla():
    # Retrieve Session data saved in search function
    ipsla_indexes = session['indexes']
    ipsla_types = session['types']
    # Creating list with names instead of numbers
    ipsla_types_names = []
    for type in ipsla_types:
        ipsla_types_names.append(cons_ipsla_types[int(type)])
    ipsla_tags = session['tags']
    snmp_data = session['snmp_data']

    # If checkboxes selected and submit button pressed process this
    if request.method == 'POST':
        # Gather checkboxes selected
        selection = request.form.getlist('selection')
        # Connect to the database and create the table if does not exist
        create_polling()

        # Insert data in the polling table
        message, message_category = insert_polling_data(selection, ipsla_indexes, snmp_data, ipsla_types, ipsla_tags)

        # Provide feedback to the user
        flash(message, message_category)

        # Redirect
        return redirect('/config')

    return render_template('ipsla.html', indexes=ipsla_indexes, types=ipsla_types, tags=ipsla_tags,
                           types_names=ipsla_types_names, snmp_data=snmp_data)


@app.route('/dash')
def dash():
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run_server(debug=True)
