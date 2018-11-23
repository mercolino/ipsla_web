#from easysnmp import Session, EasySNMPTimeoutError, EasySNMPConnectionError, EasySNMPUnknownObjectIDError
import yaml
import sqlite3
import pandas as pd


cons_ipsla_types = ['padding',
                    'echo',
                    'pathEcho',
                    'fileIO',
                    'script',
                    'udpEcho',
                    'tcpConnect',
                    'http',
                    'dns',
                    'jitter',
                    'dlsw',
                    'dhcp',
                    'ftp',
                    'voip',
                    'rtp',
                    'lspGroup',
                    'icmpjitter',
                    'lspPing',
                    'lspTrace',
                    'ethernetPing',
                    'ethernetJitter',
                    'lspPingPseudowire',
                    'video',
                    'y1731Delay',
                    'y1731Loss',
                    'mcastJitter',
                    'fabricPathEcho']


cons_ipsla_oper_sense = ['other',
                         'ok',
                         'disconnected',
                         'overThreshold',
                         'timeout',
                         'busy',
                         'notConnected',
                         'dropped',
                         'sequenceError',
                         'verifyError',
                         'applicationSpecific',
                         'dnsServerTimeout',
                         'tcpConnectTimeout',
                         'httpTransactionTimeout',
                         'dnsQueryError',
                         'httpError',
                         'error',
                         'mplsLspEchoTxError',
                         'mplsLspUnreachable',
                         'mplsLspMalformedReq',
                         'mplsLspReachButNotFEC',
                         'enableOk',
                         'enableNoConnect',
                         'enableVersionFail',
                         'enableInternalError',
                         'enableAbort',
                         'enableFail',
                         'enableAuthFail',
                         'enableFormatError',
                         'enablePortInUse',
                         'statsRetrieveOk',
                         'statsRetrieveNoConnect',
                         'statsRetrieveVersionFail',
                         'statsRetrieveInternalError',
                         'statsRetrieveAbort',
                         'statsRetrieveFail',
                         'statsRetrieveAuthFail',
                         'statsRetrieveFormatError',
                         'statsRetrievePortInUse']


# # Function to query the host to gather the ip sla's, return three lists indexes, type and tags
# def ipsla_search(data):
#
#     # Retrieving SNMP config from yaml
#     f = open('config.yaml', 'r')
#     config = yaml.load(f)
#
#     f.close()
#
#     # Check Version of SNMP Used
#     if data['snmp_version'] == '2':
#         message = "SNMP Version 2 Is not implemented yet"
#         message_category = 'error'
#         return [], [], [], message, message_category
#     elif data['snmp_version'] == '3':
#         # Create an SNMP session to be used for all our requests
#         snmp_session = Session(retries=config['snmp']['retries'], timeout=config['snmp']['timeout'],
#                                hostname=data['hostname'], version=int(data['snmp_version']), security_level=data['security_level'],
#                                security_username=data['security_username'], auth_protocol=data['auth_protocol'],
#                                auth_password=data['auth_password'], privacy_protocol=data['privacy_protocol'],
#                                privacy_password=data['privacy_password'])
#
#         try:
#             # Perform an SNMP walk to retrieve all the ipsla's configured and types
#             ipsla_types = snmp_session.walk('1.3.6.1.4.1.9.9.42.1.2.1.1.4')
#         # Handle timeout error
#         except EasySNMPTimeoutError:
#             message = "Timeout connecting to host {host}".format(host=data['hostname'])
#             message_category = 'error'
#             return [], [], [], message, message_category
#         # Handle Connection error
#         except EasySNMPConnectionError:
#             message = "Error connecting to host {host}".format(host=data['hostname'])
#             message_category = 'error'
#             return [], [], [], message, message_category
#         # Handle OID Problem, device not supported maybe?
#         except EasySNMPUnknownObjectIDError:
#             message = "Device {host} not supported".format(host=data['hostname'])
#             message_category = 'error'
#             return [], [], [], message, message_category
#
#         # Perform an SNMP walk to retrieve all the Tags for the ipsla's
#         ipsla_tags = snmp_session.walk('1.3.6.1.4.1.9.9.42.1.2.1.1.12')
#
#         # Create lists for indexes and types
#         indexes = []
#         types = []
#         tags = []
#         i = 0
#         for ipsla in ipsla_types:
#             indexes.append(ipsla.oid_index)
#             types.append(ipsla.value)
#             tags.append(ipsla_tags[i].value)
#             i += 1
#
#     message = 'Connection to host {host} successful'.format(host=data['hostname'])
#     message_category = 'success'
#
#     return indexes, types, tags, message, message_category
#
#
# # Function to create the polling table on the database
# def create_polling():
#     # Retrieving SNMP config from yaml
#     f = open('config.yaml', 'r')
#     config = yaml.load(f)
#
#     f.close()
#
#     # Check type of Database is used
#     if config['db'].lower() == 'sqlite':
#         db = sqlite3.connect('db/' + config['db_name'].lower())
#         cursor = db.cursor()
#         cursor.execute('''
#                     CREATE TABLE IF NOT EXISTS ipsla_polling( id INTEGER PRIMARY KEY, hostname TEXT, ipsla_index TEXT,
#                     ipsla_type TEXT, ipsla_tag TEXT, snmp_version TEXT, snmp_community TEXT, snmp_security_level TEXT,
#                     snmp_security_username TEXT, snmp_auth_protocol TEXT, snmp_auth_password TEXT, snmp_priv_protocol TEXT,
#                     snmp_priv_password TEXT)
#                 ''')
#         db.commit()
#         db.close()
#     elif config['db'].lower() == 'mongodb':
#         print("mongodb still not supported")
#
#
# # Function to insert polling data in the database
# def insert_polling_data(selection, ipsla_indexes, snmp_data, ipsla_types, ipsla_tags):
#     # Retrieving SNMP config from yaml
#     f = open('config.yaml', 'r')
#     config = yaml.load(f)
#
#     f.close()
#
#     # Check type of Database is used
#     if config['db'].lower() == 'sqlite':
#         db = sqlite3.connect('db/' + config['db_name'].lower())
#         cursor = db.cursor()
#
#         # Insert data selected on the database
#         for s in selection:
#             i = ipsla_indexes.index(s)
#             # Check first if the combination hostname ipsla index is not present on the database
#             cursor.execute('''SELECT id FROM ipsla_polling WHERE hostname=? AND ipsla_index=?''',
#                            (snmp_data['hostname'], s))
#             exists = cursor.fetchone()
#
#             # If no entry on the database then add it
#             if exists is None:
#                 cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
#                         snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
#                         snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
#                                (snmp_data['hostname'], s, ipsla_types[i], ipsla_tags[i], snmp_data['snmp_version'],
#                                 snmp_data['community'],
#                                 '' if snmp_data['security_level'] == "Choose..." else snmp_data['security_level'],
#                                 snmp_data['security_username'],
#                                 '' if snmp_data['auth_protocol'] == "Choose..." else snmp_data['auth_protocol'],
#                                 snmp_data['auth_password'],
#                                 '' if snmp_data['privacy_protocol'] == "Choose..." else snmp_data['privacy_protocol'],
#                                 snmp_data['privacy_password']))
#
#         db.commit()
#         db.close()
#
#         message = 'Ip Sla\'s added to the polling database'
#         message_category = 'warning'
#
#         return message, message_category
#
#     elif config['db'].lower() == 'mongodb':
#         print("mongodb still not supported")


# Function to grab all data on the polling database
def grab_all_polls():
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        try:
            cursor.execute(
                '''SELECT * FROM ipsla_polling''')
            all_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            all_rows = []
        db.commit()
        db.close()

        return all_rows

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")


# Function to delete entries on the polling database
def delete_polls(selection):
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        # TODO: Remove also data from the ip sla data table
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        # Remove all the ip sla's selected
        for s in selection:
            cursor.execute('''DELETE FROM ipsla_polling WHERE id = ? ''', (s,))

        db.commit()
        db.close()

        message = 'Ip Sla\'s removed form the polling database'
        message_category = 'warning'
        return message, message_category

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")


# Function to grab the hosts from the poller database
def grab_hostnames():
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        try:
            cursor.execute(
                '''SELECT DISTINCT hostname FROM ipsla_polling''')
            all_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            all_rows = []

        db.close()

        return all_rows

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")


# Function to grab the ipsla's from a host from the poller database
def grab_ipslas(hostname):
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        try:
            cursor.execute(
                '''SELECT DISTINCT ipsla_index, ipsla_tag FROM ipsla_polling WHERE hostname = ?''', (hostname,))
            all_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            all_rows = []
        db.commit()
        db.close()

        return all_rows

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")


# Function to grab the ipsla's from a host from the poller database
def grab_graph_data2(hostname, ipsla):
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        try:
            cursor.execute(
                '''SELECT ipsla_type FROM ipsla_polling WHERE hostname = ? AND ipsla_index = ?''', (hostname, ipsla))
            result = cursor.fetchone()[0]
            ipsla_type = cons_ipsla_types[int(result)]
        except sqlite3.OperationalError:
            return [], []
        try:
            sql = 'SELECT datetime, latest_rtt FROM ' + ipsla_type + ' WHERE hostname = \'' + hostname + '\' AND ipsla_index = \'' + ipsla + '\' ORDER BY datetime ASC'
            cursor.execute(sql)
            all_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            all_rows = []
        db.commit()
        db.close()

        return ipsla_type, all_rows

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")


# Function to grab the ipsla's from a host from the poller database
def grab_graph_data(hostname, ipsla):
    # Retrieving SNMP config from yaml
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Check type of Database is used
    if config['db'].lower() == 'sqlite':
        db = sqlite3.connect('db/' + config['db_name'].lower())
        cursor = db.cursor()
        try:
            cursor.execute(
                '''SELECT ipsla_type FROM ipsla_polling WHERE hostname = ? AND ipsla_index = ?''', (hostname, ipsla))
            result = cursor.fetchone()[0]
            ipsla_type = cons_ipsla_types[int(result)]
        except sqlite3.OperationalError:
            return [], []

        # Querying database
        sql = 'SELECT datetime, latest_rtt FROM ' + ipsla_type + ' WHERE hostname = \'' + hostname + '\' AND ipsla_index = \'' + ipsla + '\' ORDER BY datetime ASC'
        df = pd.read_sql_query(sql, db)

        # Convert Datetime strings to datetime
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert latest_rtt strings to numeric
        df['latest_rtt'] = pd.to_numeric(df['latest_rtt'])

        return ipsla_type, df

    elif config['db'].lower() == 'mongodb':
        print("mongodb still not supported")
