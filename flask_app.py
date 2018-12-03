from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, IPAddress
from lib.utils import cons_ipsla_types, grab_all_polls, delete_polls
from lib.utils import ipsla_search, create_polling, insert_polling_data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xxzSEO8jlCZt856qPayi'


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
    pill_active = ['active', '', '']
    return render_template('main.html', pill_active=pill_active)


# Config page, all the ip sla's on the polling database and presented and can be added or removed
@app.route('/config', methods=['GET', 'POST'])
def config():
    pill_active = ['', 'active', '']
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

    if all_rows.empty:
        empty = True
    else:
        empty = False

    # Render page
    return render_template('config.html', empty=empty, all_rows=all_rows, types_names=cons_ipsla_types,
                           pill_active=pill_active)


# Function to search for IP Sla's
@app.route('/search', methods=['GET', 'POST'])
def search():
    pill_active = ['', 'active', '']
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

    return render_template('search.html', form=form, pill_active=pill_active)

# Function to search for IP Sla's
@app.route('/reports')
def reports():
    pill_active = ['', '', 'active']
    return render_template('reports.html', pill_active=pill_active)


# Function to add ipsla to the database
@app.route('/ipsla', methods=['GET', 'POST'])
def ipsla():
    pill_active = ['', 'active', '']
    # Retrieve Session data saved in search function
    ipsla_indexes = session['indexes']
    ipsla_types = session['types']
    # Creating list with names instead of numbers
    ipsla_types_names = []
    for t in ipsla_types:
        ipsla_types_names.append(cons_ipsla_types[int(t)])
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
                           types_names=ipsla_types_names, snmp_data=snmp_data, pill_active=pill_active)


@app.route('/dash')
def dash():
    return redirect('/dashboard')
