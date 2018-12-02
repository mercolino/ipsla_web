import yaml
from multiprocessing import Process, Queue
from easysnmp import Session, EasySNMPConnectionError, EasySNMPTimeoutError, EasySNMPUnknownObjectIDError
from lib.utils import cons_ipsla_types, grab_all_polls
import time
from ipaddress import IPv4Address
from datetime import datetime, timedelta
import sqlite3
import sys
import pymongo
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random


def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


def ipsla_worker(poll_q, ipsla_q):
    # Load config file
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Retrieve Username
    f = open('_usr.p', 'rb')
    data = f.read().decode('ascii')
    f.close()

    encryption_key = data.encode('ascii')

    while poll_q.qsize() != 0:
        # Grabbing task from the poll queue
        poll = poll_q.get()

        # Process data from the queue
        hostname = poll[1]
        ipsla_index = poll[2]
        ipsla_type = poll[3]
        ipsla_tag = poll[4]
        snmp_version = poll[5]
        snmp_community = poll[6]
        snmp_security_level = poll[7]
        snmp_security_username = poll[8]
        snmp_auth_protocol = poll[9]
        snmp_auth_password = decrypt(encryption_key, poll[10]).decode('ascii')
        snmp_priv_protocol = poll[11]
        snmp_priv_password = decrypt(encryption_key, poll[12]).decode('ascii')

        # Open OID Template
        try:
            f = open('ipsla_templates/' + cons_ipsla_types[int(ipsla_type)] + '.yaml', 'r')
        except FileNotFoundError:
            print('Type {type} not implemented yet!!!'.format(type=ipsla_type))
            return

        # Reading yaml IPSLA template
        template = yaml.load(f)
        f.close()

        # Check SNMP Version
        if snmp_version == '2':
            print("SNMP Version 2 Is not implemented yet")
        elif snmp_version == '3':
            # Create an SNMP session to be used for all our requests
            snmp_session = Session(retries=config['snmp']['retries'], timeout=config['snmp']['timeout'],
                                   hostname=hostname, version=int(snmp_version),
                                   security_level=snmp_security_level,
                                   security_username=snmp_security_username, auth_protocol=snmp_auth_protocol,
                                   auth_password=snmp_auth_password, privacy_protocol=snmp_priv_protocol,
                                   privacy_password=snmp_priv_password)
            ipsla_results = {}
            ipsla_results['hostname'] = hostname
            ipsla_results['ipsla_index'] = ipsla_index
            # Get sysuptime
            try:
                ipsla_results['sysuptime'] = snmp_session.get('1.3.6.1.2.1.1.3.0').value
                # Handle timeout error
            except EasySNMPTimeoutError:
                message = "Timeout connecting to host {host}".format(host=hostname)
                print(message)
                break
            # Handle Connection error
            except EasySNMPConnectionError:
                message = "Error connecting to host {host}".format(host=hostname)
                print(message)
                break
            # Handle OID Problem, device not supported maybe?
            except EasySNMPUnknownObjectIDError:
                message = "Device {host} not supported".format(host=hostname)
                print(message)
                break
            # Get snmp data from the template
            for key in template:
                try:
                    snmp_res = snmp_session.get(template[key] + '.' + ipsla_index)
                    # Handle timeout error
                except EasySNMPTimeoutError:
                    message = "Timeout connecting to host {host}".format(host=hostname)
                    print(message)
                    break
                # Handle Connection error
                except EasySNMPConnectionError:
                    message = "Error connecting to host {host}".format(host=hostname)
                    print(message)
                    break
                # Handle OID Problem, device not supported maybe?
                except EasySNMPUnknownObjectIDError:
                    message = "Device {host} not supported".format(host=hostname)
                    print(message)
                    break

                ipsla_results[key] = snmp_res.value

            # Adding Data to the queue to be later processed by the db process
            ipsla_q.put(ipsla_results)
    return


def db_worker(ipsla_q):
    while ipsla_q.qsize() != 0:
        # Retrieving SNMP config from yaml
        f = open('config.yaml', 'r')
        config = yaml.load(f)

        f.close()

        # Grabbing data from queue
        ipsla_processed = ipsla_q.get()

        # Check type of Database is used
        if config['db'].lower() == 'sqlite':
            # Create sqlite object
            db = sqlite3.connect('db/' + config['db_name'].lower() + '.db')
            cursor = db.cursor()
            # Create sql to create table based on the keys of the ipsla template
            sql = 'CREATE TABLE IF NOT EXISTS ' + cons_ipsla_types[int(ipsla_processed['type'])] + ' ( id INTEGER PRIMARY KEY, '
            for key in ipsla_processed:
                sql = sql + key + ' TEXT, '
            sql = sql + 'datetime' + ' TEXT, '
            sql = sql[:-2] + ')'
            # Create table
            cursor.execute(sql)

            # Commit creation of table
            db.commit()

            # Create sql string to insert data into the table
            sql1 = 'INSERT INTO ' + cons_ipsla_types[int(ipsla_processed['type'])] + ' ( '
            sql2 = ' VALUES('
            sql3 = 'SELECT * FROM ' + cons_ipsla_types[int(ipsla_processed['type'])] + ' WHERE '
            for key in ipsla_processed:
                if key == 'target_address' or key == 'source_address':
                    sql1 = sql1 + key + ','
                    sql2 = sql2 + '\'' + str(IPv4Address(ipsla_processed[key].encode('latin-1'))) + '\','
                    sql3 = sql3 + key + '=\'' + str(IPv4Address(ipsla_processed[key].encode('latin-1'))) + '\' AND '
                    print("key: {key}, value: {value}".format(key=key,
                                                              value=IPv4Address(
                                                                  ipsla_processed[key].encode('latin-1'))))
                elif key == 'sysuptime':
                    sql1 = sql1 + key + ','
                    sql2 = sql2 + '\'' + ipsla_processed[key] + '\','
                    print("key: {key}, value: {value}".format(key=key, value=ipsla_processed[key]))
                else:
                    sql1 = sql1 + key + ','
                    sql2 = sql2 + '\'' + ipsla_processed[key] + '\','
                    sql3 = sql3 + key + '=\'' + ipsla_processed[key] + '\' AND '
                    print("key: {key}, value: {value}".format(key=key, value=ipsla_processed[key]))

            diff = int(ipsla_processed['sysuptime']) - int(ipsla_processed[key])
            converted_ticks = datetime.now() - timedelta(seconds=diff / 100)
            sql1 = sql1 + 'datetime' + ','
            sql2 = sql2 + '\'' + converted_ticks.strftime("%Y-%m-%d %H:%M:%S") + '\','
            print("key: 'datetime', value: {value}".format(key=key,
                                                      value=converted_ticks.strftime("%Y-%m-%d %H:%M:%S")))

            sql1 = sql1[:-1] + ')'
            sql2 = sql2[:-1] + ')'
            sql = sql1 + sql2
            sql3 = sql3[:-5]

            # Check if record is not present
            cursor.execute(sql3)
            exists = cursor.fetchone()

            if exists is None:
                # Insert data into table
                # Create table
                cursor.execute(sql)

                # Commit Insert into table and close database
                db.commit()
                db.close()

            print('##########################################\n' * 3)

        elif config['db'].lower() == 'mongodb':

            # Create Url to connect to mongo database
            url = "mongodb://{username}:{password}@{host}:{port}".format(
                username=config['mongo']['username'],
                password=config['mongo']['password'],
                host=config['mongo']['host'],
                port=config['mongo']['port']
            )
            # Create conenction
            client = pymongo.MongoClient(url)
            # Create database
            db = client[config['db_name']]
            # Create Collection
            col = db[cons_ipsla_types[int(ipsla_processed['type'])]]

            # Create datetime index
            col.create_index([("datetime", pymongo.DESCENDING)], background=True)

            diff = int(ipsla_processed['sysuptime']) - int(ipsla_processed[key])
            converted_ticks = datetime.now() - timedelta(seconds=diff / 100)

            doc = [
                {'hostname': ipsla_processed['hostname']},
                {'ipsla_index': ipsla_processed['ipsla_index']},
                {'type': ipsla_processed['type']},
                {'threshold': ipsla_processed['threshold']},
                {'timeout': ipsla_processed['timeout']},
                {'frequency': ipsla_processed['frequency']},
                {'tag': ipsla_processed['tag']},
                {'target_address': str(IPv4Address(ipsla_processed['target_address'].encode('latin-1')))},
                {'source_address': str(IPv4Address(ipsla_processed['source_address'].encode('latin-1')))},
                {'latest_rtt': ipsla_processed['latest_rtt']},
                {'return_code': ipsla_processed['return_code']},
                {'time': ipsla_processed['time']},
            ]

            query = col.find(
                {'$and': doc},
                {
                    '_id': 1
                }
            )

            if query.count() == 0:
                doc = {
                    'hostname': ipsla_processed['hostname'],
                    'ipsla_index': ipsla_processed['ipsla_index'],
                    'sysuptime': ipsla_processed['sysuptime'],
                    'type': ipsla_processed['type'],
                    'threshold': ipsla_processed['threshold'],
                    'timeout': ipsla_processed['timeout'],
                    'frequency': ipsla_processed['frequency'],
                    'tag': ipsla_processed['tag'],
                    'target_address': str(IPv4Address(ipsla_processed['target_address'].encode('latin-1'))),
                    'source_address': str(IPv4Address(ipsla_processed['source_address'].encode('latin-1'))),
                    'latest_rtt': ipsla_processed['latest_rtt'],
                    'return_code': ipsla_processed['return_code'],
                    'time': ipsla_processed['time'],
                    'datetime': converted_ticks
                }
                col.insert(doc)

            client.close()

            for key in ipsla_processed:
                if key == 'target_address' or key == 'source_address':
                    print("key: {key}, value: {value}".format(key=key,
                                                              value=IPv4Address(
                                                                  ipsla_processed[key].encode('latin-1'))))
                else:
                    print("key: {key}, value: {value}".format(key=key, value=ipsla_processed[key]))

            print("key: 'datetime', value: {value}".format(key=key,
                                                      value=converted_ticks.strftime("%Y-%m-%d %H:%M:%S")))

    return


if __name__ == "__main__":
    # Reading the Config File
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Creating the queue to shared between processes
    poll_queue = Queue()
    ipsla_results_queue = Queue()

    while True:
        try:
            print("Initiating Polling")
            # Querying DB for all polls
            polls = grab_all_polls()

            # Load polls in the queue
            for i in polls.index:
                poll_queue.put(polls.iloc[i])

            # Launching all the SNMP Processes
            snmp_jobs = []
            for i in range(config['number_of_snmp_processes']):
                snmp_process = Process(name="ipsla_worker-" + str(i), target=ipsla_worker, args=(poll_queue,
                                                                                                 ipsla_results_queue))
                snmp_process.daemon = True
                snmp_jobs.append(snmp_process)
                snmp_process.start()

            time.sleep(config['db_process_delay'])

            # Launching all the db inserting processes
            db_jobs = []
            for j in range(config['number_of_db_processes']):
                db_process = Process(name="db_worker-" + str(j), target=db_worker, args=(ipsla_results_queue, ))
                db_process.daemon = True
                db_jobs.append(db_process)
                db_process.start()

            for snmp_job in snmp_jobs:
                snmp_job.join()

            for db_job in db_jobs:
                db_job.join()

            print("Ending Polling")
            time.sleep(config['poll_frequency']*60)

        except KeyboardInterrupt:
            print("Keyboard interrupt waiting for all processes to be done")

            for snmp_job in snmp_jobs:
                snmp_job.join()

            for db_job in db_jobs:
                db_job.join()

            print("Exiting")

            sys.exit(0)