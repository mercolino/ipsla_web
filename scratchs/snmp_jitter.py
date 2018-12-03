from easysnmp import Session

# Create an SNMP session to be used for all our requests
#session = Session(hostname='192.168.5.2', community='test', version=2)

session = Session( hostname='hostname', version=3,
                                   security_level='auth_with_privacy',
                                   security_username='ro-user', auth_protocol='SHA',
                                   auth_password='test', privacy_protocol='AES128',
                                   privacy_password='test')


# And of course, you may use the numeric OID too
print("Min Positive SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.6.7').value))
print("Min Negative SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.11.7').value))
print("#"*20)
print("Avg SD Jitter is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.47.7').value))
print("#"*20)
print("Max Positive SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.7.7').value))
print("Max Negative SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.12.7').value))
print("#"*20)
print("#"*20)
print("#"*20)
print("Min Positive DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.16.7').value))
print("Min Negative DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.21.7').value))
print("#"*20)
print("Avg DS Jitter is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.7').value))
print("#"*20)
print("Max Positive DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.17.7').value))
print("Max Negative DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.22.7').value))
print("#"*20)
print('Source to Destination Latency one way Min/Avg/Max: {}/{}/{} milliseconds'.format(
    min(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.6.7').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.11.7').value)),
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.47.7').value,
    max(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.7.7').value, session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.12.7').value)
))
print('Destination to Source Jitter Min/Avg/Max: {}/{}/{} milliseconds'.format(
    min(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.16.7').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.21.7').value)),
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.7').value,
    max(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.17.7').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.22.7').value))
))
print('Jitter Min/Avg/Max: {}/{}/{} milliseconds'.format(
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.4.7').value,
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.7').value,
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.5.7').value
))

snmp_res = session.get('.1.3.6.1.4.1.9.9.42.1.2.1.1.4.5')
print('Type: {}'.format(snmp_res.value))