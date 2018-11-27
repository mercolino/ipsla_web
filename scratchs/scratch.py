import sqlite3
from random import *
import datetime


SAMPLES = 100000

db = sqlite3.connect('/home/mercolino/PycharmProjects/ipsla_web/db/ipsla.db')
cursor = db.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS ipsla_polling( id INTEGER PRIMARY KEY, hostname TEXT, ipsla_index TEXT,
                    ipsla_type TEXT, ipsla_tag TEXT, snmp_version TEXT, snmp_community TEXT, snmp_security_level TEXT,
                    snmp_security_username TEXT, snmp_auth_protocol TEXT, snmp_auth_password TEXT, snmp_priv_protocol TEXT,
                    snmp_priv_password TEXT)
                ''')

db.commit()

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.1.100', '1', '1', 'tag 1', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.1.100', '10', '1', 'tag 10', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.1.100', '100', '1', 'tag 100', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.2.3', '5', '1', 'tag 5', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.2.3', '7', '1', 'tag 7', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.5.1', '1', '1', 'tag 1', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.5.20', '12', '1', 'tag 12', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.5.20', '15', '1', 'tag 15', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.5.20', '20', '1', 'tag 20', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))

cursor.execute('''INSERT INTO ipsla_polling(hostname, ipsla_index, ipsla_type, ipsla_tag, snmp_version,
                        snmp_community, snmp_security_level, snmp_security_username, snmp_auth_protocol, snmp_auth_password,
                        snmp_priv_protocol, snmp_priv_password) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (
    '192.168.5.20', '25', '1', 'tag 25', '3', '', 'auth_with_priv', 'ro-user', 'SHA', 'askdh', 'AES128', 'aksldfjh'
))
db.commit()

# Create sql to create table based on the keys of the ipsla template
sql = 'CREATE TABLE IF NOT EXISTS echo ( id INTEGER PRIMARY KEY, hostname TEXT, ipsla_index TEXT, sysuptime TEXT, ' \
      'type TEXT, threshold TEXT, timeout TEXT, frequency TEXT, tag TEXT, target_address TEXT, source_address TEXT, ' \
      'latest_rtt TEXT, return_code TEXT, time TEXT, datetime TEXT)'

db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(1,3)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.1.100', '1', '123456', '1', '2000', '2000', " \
          "'60', 'tag 1', '192.168.1.1', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"

    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(3,12)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.1.100', '10', '123456', '1', '2000', '2000', " \
          "'60', 'tag 10', '192.168.1.1', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.1.100', '100', '123456', '1', '2000', '2000', " \
          "'60', 'tag 100', '192.168.1.1', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()
######################################
for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.2.3', '5', '123456', '1', '2000', '2000', " \
          "'60', 'tag 5', '192.168.2.3', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.2.3', '7', '123456', '1', '2000', '2000', " \
          "'60', 'tag 7', '192.168.2.3', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.5.1', '1', '123456', '1', '2000', '2000', " \
          "'60', 'tag 1', '192.168.5.1', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.5.20', '12', '123456', '1', '2000', '2000', " \
          "'60', 'tag 12', '192.168.5.20', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.5.20', '15', '123456', '1', '2000', '2000', " \
          "'60', 'tag 15', '192.168.5.20', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.5.20', '20', '123456', '1', '2000', '2000', " \
          "'60', 'tag 20', '192.168.5.20', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

for i in range(SAMPLES):
    latest_rtt = randint(700,720)
    date_time = datetime.datetime.now() - i * datetime.timedelta(seconds=60)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO echo (hostname, ipsla_index, sysuptime, type, threshold, timeout, frequency, tag, target_address, " \
          "source_address, latest_rtt, return_code, time, datetime) VALUES ('192.168.5.20', '25', '123456', '1', '2000', '2000', " \
          "'60', 'tag 25', '192.168.5.20', '192.168.1.100', " + str(latest_rtt) + ", '1', '123456', '" + date_time + "')"
    db.execute(sql)

db.commit()

db.close()

