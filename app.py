from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, IPAddress
import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

app_dash = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
app_dash.css.append_css({'external_url': '/static/css/bootstrap.css'})

app_dash.layout = html.Div(children=[

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

    html.Div([
        html.Div([
            html.Label('Host'),
            dcc.Dropdown(
                id='host',
                options=[
                    {'label': '1.1.1.1', 'value': '1.1.1.1'},
                    {'label': '2.2.2.2', 'value': '2.2.2.2'},
                    {'label': '5.5.5.5', 'value': '5.5.5.5'}
                ],
            ),
        ], className='col-3'),
        html.Div([
            html.Label('Ip Sla'),
            dcc.Dropdown(
                id='ipsla',
            ),
        ], className='col-3'),
    ], className='row'),


    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montreal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
], className='container-fluid')


@app_dash.callback(dash.dependencies.Output('ipsla', 'options'),
                   [dash.dependencies.Input('host', 'value')])
def update_ipsla_dropdown(h):
    if h == '1.1.1.1':
        return [{'label': '1 (Tag1)', 'value': '1'},
                {'label': '10', 'value': '10'},
                {'label': '100', 'value': '100'}]
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


# Function to query the host to gather the ip sla's, return three lists indexes, type and tags
def ipsla_search(data):
    flash('Connection to host {host} successful'.format(host=data['hostname']), 'success')
    for key in data:
        print "The key {key} is \'{value}\'".format(key=key, value=data[key])

    indexes = ['1', '10', '100']
    #indexes = []
    types = ['1', '1', '1']
    tags = ['tag1', '', '']

    return indexes, types, tags


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
                db = sqlite3.connect('db/ipsla_poll.db')
                cursor = db.cursor()
                # Remove all the ip sla's selected
                for s in selection:
                    cursor.execute('''DELETE FROM ipsla_polling WHERE id = ? ''', (s,))

                db.commit()
                db.close()
                flash('Ip Sla\'s removed form the polling database', 'warning')
            else:
                flash('Nothing selected!. No Ip Sla\'s were removed form the polling database', 'error')


    # Connect to the database when config page with method get is used
    db = sqlite3.connect('db/ipsla_poll.db')
    cursor = db.cursor()
    # Grab all ip sla's on the database
    try:
        cursor.execute('''SELECT id, hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version FROM ipsla_polling''')
        all_rows = cursor.fetchall()
    except sqlite3.OperationalError:
        all_rows = []

    # Render page
    return render_template('config.html', all_rows=all_rows)


# Function to search for IP Sla's
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Define form with class configured
    form = SearchIpSlaForm()
    # If Form's submit button was pressed enter
    if request.method == 'POST':
        if form.validate():
            # Connect to the host and retrieve all the ip sla data
            ipsla_indexes, ipsla_types, ipsla_tags = ipsla_search(form.data)
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
    ipsla_tags = session['tags']
    snmp_data = session['snmp_data']

    # If checkboxes selected and submit button pressed process this
    if request.method == 'POST':
        # Gather checkboxes selected
        selection = request.form.getlist('selection')
        # Connect to the databaseand create the table is does not exist
        db = sqlite3.connect('db/ipsla_poll.db')
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ipsla_polling( id INTEGER PRIMARY KEY, hostname TEXT, ipsla_index TEXT, 
            ipsla_type TEXT, ipsla_tag TEXT, snmp_version TEXT, snmp_community TEXT, snmp_security_level TEXT, 
            snmp_security_username TEXT, snmp_auth_protocol TEXT, snmp_auth_password TEXT, snmp_priv_protocol TEXT, 
            snmp_priv_password TEXT)
        ''')
        db.commit()

        # Insert data selected on the database
        for s in selection:
            i = ipsla_indexes.index(s)
            # Check first if the combination hostname ipsla index is not present on the database
            cursor.execute('''SELECT id FROM ipsla_polling WHERE hostname=? AND ipsla_index=?''',
                           (snmp_data['hostname'], s))
            exists = cursor.fetchone()

            # If no entry on teh database then add it
            if exists is None:
                cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                               (snmp_data['hostname'], s, ipsla_types[i], ipsla_tags[i], snmp_data['snmp_version'],
                                snmp_data['community'],
                                '' if snmp_data['security_level'] == "Choose..." else snmp_data['security_level'],
                                snmp_data['security_username'],
                                '' if snmp_data['auth_protocol'] == "Choose..." else snmp_data['auth_protocol'],
                                snmp_data['auth_password'],
                                '' if snmp_data['privacy_protocol'] == "Choose..." else snmp_data['privacy_protocol'],
                                snmp_data['privacy_password']))

        db.commit()
        db.close()
        flash('Ip Sla\'s added to the polling database', 'warning')
        return redirect('/config')

    return render_template('ipsla.html', indexes=ipsla_indexes, types=ipsla_types, tags=ipsla_tags, snmp_data=snmp_data)


@app.route('/dash')
def dash():
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run_server()
