from easysnmp import Session

# Create an SNMP session to be used for all our requests
session = Session(hostname='192.168.5.2', community='test', version=2)


# And of course, you may use the numeric OID too
print("Min Positive SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.6.5').value))
print("Min Negative SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.11.5').value))
print("#"*20)
print("Avg SD Jitter is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.47.5').value))
print("#"*20)
print("Max Positive SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.7.5').value))
print("Max Negative SD is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.12.5').value))
print("#"*20)
print("#"*20)
print("#"*20)
print("Min Positive DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.16.5').value))
print("Min Negative DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.21.5').value))
print("#"*20)
print("Avg DS Jitter is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.5').value))
print("#"*20)
print("Max Positive DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.17.5').value))
print("Max Negative DS is {}".format(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.22.5').value))
print("#"*20)
print('Source to Destination Latency one way Min/Avg/Max: {}/{}/{} milliseconds'.format(
    min(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.6.5').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.11.5').value)),
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.47.5').value,
    max(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.7.5').value, session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.12.5').value)
))
print('Destination to Source Jitter Min/Avg/Max: {}/{}/{} milliseconds'.format(
    min(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.16.5').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.21.5').value)),
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.5').value,
    max(int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.17.5').value), int(session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.22.5').value))
))
print('Jitter Min/Avg/Max: {}/{}/{} milliseconds'.format(
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.4.5').value,
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.48.5').value,
    session.get('.1.3.6.1.4.1.9.9.42.1.5.2.1.5.5').value
))