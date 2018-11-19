import yaml
from multiprocessing import Process, current_process, Queue
import time


def ipsla_worker(num, queue):
    print "Starting snmp process {p} with the name {name}".format(p=num, name=current_process().name)
    for ipsla in range(7):
        queue.put(current_process().name + ' ' + str(ipsla))
        time.sleep(1)
    queue.put('end')
    print "Ending snmp process {p} with the name {name}".format(p=num, name=current_process().name)


def db_worker(num, queue):
    print "Starting db process {p} with the name {name}".format(p=num, name=current_process().name)
    while True:
        ipsla_processed = queue.get()
        if ipsla_processed != 'end':
            print ipsla_processed
        else:
            break
    print "Ending db process {p} with the name {name}".format(p=num, name=current_process().name)


if __name__ == "__main__":
    f = file('config.yaml', 'r')
    config = yaml.load(f)

    q = Queue()

    snmp_jobs = []
    for i in range(config['number_of_snmp_processes']):
        snmp_process = Process(name="ipsla_worker-" + str(i), target=ipsla_worker, args=(i, q))
        snmp_process.daemon = True
        snmp_jobs.append(snmp_process)
        snmp_process.start()

    db_jobs = []
    for j in range(config['number_of_db_processes']):
        db_process = Process(name="db_worker-" + str(j), target=db_worker, args=(j, q))
        db_process.daemon = True
        db_jobs.append(db_process)
        db_process.start()

    for snmp_job in snmp_jobs:
        snmp_job.join()

    for db_job in db_jobs:
        db_job.join()