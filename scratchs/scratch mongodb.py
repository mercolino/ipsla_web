import pymongo
import random
import datetime
from multiprocessing import Process, Queue

SAMPLES = 500000
CHUNKS = 1000

list_ipsla =[
    [
        1,
        3,
        '192.168.1.100',
        '1'
    ],
    [
        12,
        20,
        '192.168.1.100',
        '10'
    ],
    [
        700,
        760,
        '192.168.1.100',
        '100'
    ],
    [
        1,
        10,
        '192.168.5.1',
        '2'
    ],
    [
        45,
        50,
        '192.168.5.1',
        '30'
    ],
    [
        120,
        130,
        '192.168.100.250',
        '5'
    ],
    [
        756,
        768,
        '192.168.3.3',
        '10'
    ],
    [
        84,
        95,
        '192.168.3.3',
        '11'
    ],
    [
        2,
        20,
        '192.168.3.3',
        '15'
    ],
    [
        200,
        300,
        '192.168.3.3',
        '16'
    ],
]


def insert_data_worker(q, chunks, datetime_now):
    # Create Url to connect to mongo database
    url = "mongodb://{username}:{password}@{host}:{port}".format(
        username='ipsla',
        password='ipsla',
        host='127.0.0.1',
        port='27017'
    )
    # Create conenction
    client1 = pymongo.MongoClient(url)
    # Create database
    db1 = client1['ipsla']
    col1 = db1['echo']
    # Create datetime index
    col1.create_index([("datetime", pymongo.DESCENDING)], background=True)

    while q.qsize() != 0:
        ipsla_doc = q.get()
        for c in chunks:
            docs = []
            for i in c:
                doc1 = {
                    'sysuptime': '12341324',
                    'type': '1',
                    'threshold': '2000',
                    'timeout': '2000',
                    'frequency': '60',
                    'target_address': '1.1.1.1',
                    'source_address': '0.0.0.0',
                    'return_code': '0',
                    'time': '34563'
                }
                latest_rtt = random.randint(ipsla_doc[0], ipsla_doc[1])
                date_time = datetime_now - i * datetime.timedelta(seconds=60)
                doc1['hostname'] = ipsla_doc[2]
                doc1['ipsla_index'] = ipsla_doc[3]
                doc1['tag'] = 'tag ' + ipsla_doc[3]
                doc1['latest_rtt'] = latest_rtt
                doc1['datetime'] = date_time
                docs.append(doc1)

            col1.insert_many(docs)

    client.close()


if __name__ == "__main__":

    start_time = datetime.datetime.now()

    # Create Url to connect to mongo database
    url = "mongodb://{username}:{password}@{host}:{port}".format(
        username='ipsla',
        password='ipsla',
        host='127.0.0.1',
        port='27017'
    )
    # Create conenction
    client = pymongo.MongoClient(url)
    # Drop Database first
    client.drop_database('ipsla')
    # Create database
    db = client['ipsla']
    # Create Collection
    col = db['ipsla_polling']

    datetime_now = datetime.datetime.now() + datetime.timedelta(days=3)

    doc = {
        'hostname': '192.168.1.100',
        'ipsla_index': '1',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 1',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.1.100',
        'ipsla_index': '10',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 10',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.1.100',
        'ipsla_index': '100',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 100',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.5.1',
        'ipsla_index': '2',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 2',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.5.1',
        'ipsla_index': '30',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 30',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.100.250',
        'ipsla_index': '5',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 5',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.3.3',
        'ipsla_index': '10',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 10',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.3.3',
        'ipsla_index': '11',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 11',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.3.3',
        'ipsla_index': '15',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 15',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    doc = {
        'hostname': '192.168.3.3',
        'ipsla_index': '16',
        'ipsla_type': '1',
        'ipsla_tag': 'tag 16',
        'snmp_version': 3,
        'snmp_community': '',
        'snmp_security_level': 'auth_with_privacy',
        'snmp_security_username': 'ro-user',
        'snmp_auth_protocol': 'SHA',
        'snmp_auth_password': 'auth_password',
        'snmp_priv_protocol': 'AES128',
        'snmp_priv_password': 'priv_password'
    }

    col.insert(doc)

    client.close()

    q = Queue()

    for l in list_ipsla:
        q.put(l)

    data = range(SAMPLES)
    chunks = [data[x:x + CHUNKS] for x in range(0, len(data), CHUNKS)]

    # Launching all the SNMP Processes
    insert_data_jobs = []

    insert_time = start_time + datetime.timedelta(days=2)
    for i in range(6):
        insert_data_process = Process(name="insert_data_process-" + str(i), target=insert_data_worker, args=(q, chunks, insert_time, ))
        insert_data_process.daemon = True
        insert_data_jobs.append(insert_data_process)
        insert_data_process.start()

    for insert_data_job in insert_data_jobs:
        insert_data_job.join()

    end_time = datetime.datetime.now()

    print('It took {seconds} s to load {elements} elements in the database'.format(
        seconds=(end_time-start_time).total_seconds(), elements=10*SAMPLES
    ))
