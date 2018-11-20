import yaml
from multiprocessing import Process, current_process, Queue
from easysnmp import Session, EasySNMPConnectionError, EasySNMPTimeoutError, EasySNMPUnknownObjectIDError
from lib.utils import cons_ipsla_types, grab_all_polls
import time
from ipaddress import IPv4Address
from datetime import datetime, timedelta


def ipsla_worker(poll_q, ipsla_q):
    # Load config file
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

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
        snmp_auth_password = poll[10]
        snmp_priv_protocol = poll[11]
        snmp_priv_password = poll[12]

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
        # Grabbing data from queue
        ipsla_processed = ipsla_q.get()

        for key in ipsla_processed:
            if key == 'target_address':
                print("key: {key}, value: {value}".format(key=key,
                                                          value=IPv4Address(ipsla_processed[key].encode('latin-1'))))
            elif key == 'source_address':
                print("key: {key}, value: {value}".format(key=key,
                                                          value=IPv4Address(ipsla_processed[key].encode('latin-1'))))
            elif key == 'time':
                converted_ticks = datetime.now() + timedelta(microseconds=int(ipsla_processed[key]) / 10)
                print("key: {key}, value: {value}".format(key=key, value=converted_ticks.strftime("%Y-%m-%d %H:%M:%S")))
            else:
                print("key: {key}, value: {value}".format(key=key, value=ipsla_processed[key]))

        print('##########################################\n'*3)

    return


if __name__ == "__main__":
    # Reading the Config File
    f = open('config.yaml', 'r')
    config = yaml.load(f)

    f.close()

    # Creating the queue to shared between processes
    poll_queue = Queue()
    ipsla_results_queue = Queue()

    # Querying DB for all polls
    polls = grab_all_polls()

    # Load polls in the queue
    for poll in polls:
        poll_queue.put(poll)

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