#!/usr/bin/env python

"""Perform an LDAP bind with an LDAP server.

Example execution:

$ ./ldap.py
Connecting to ldap.forumsys.com:389... done.
{'messageID': 1,
 'protocolOp': {'bindRequest': {'authentication': {'simple': b'password'},
                                'name': b'uid=tesla,dc=example,dc=com',
                                'version': 3}}}
Sending LDAP bind request to the server... done.
Receiving LDAP bind response from the server... done.
{'messageID': 1,
 'protocolOp': {'bindResponse': {'diagnosticMessage': bytearray(b''),
                                 'matchedDN': bytearray(b''),
                                 'resultCode': 'success'}}}
$

"""

from __future__ import print_function
import os
import socket
from pprint import pprint
import asn1tools

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RFC4511_ASN_PATH = os.path.join(SCRIPT_DIR,
                                '..',
                                'tests',
                                'files',
                                'ietf',
                                'rfc4511.asn')
HOST = 'ldap.forumsys.com'
PORT = 389
db = asn1tools.compile_files(RFC4511_ASN_PATH)

# Connect to the LDAP server.
sock = socket.socket()
print('Connecting to {}:{}... '.format(HOST, PORT), end='')
sock.connect((HOST, PORT))
print('done.')

# Encode the LDAP bind request and send it to the server.
bind_request = {
    'messageID': 1,
    'protocolOp': {
        'bindRequest': {
            'version': 3,
            'name': b'uid=tesla,dc=example,dc=com',
            'authentication': {
                'simple': b'password'
            }
        }
    }
}

encoded_bind_request = db.encode('LDAPMessage', bind_request)

pprint(bind_request)
print('Sending LDAP bind request to the server... ', end='')
sock.sendall(encoded_bind_request)
print('done.')

# Receive the bind response, decode it, and print it.
print('Receiving LDAP bind response from the server... ', end='')
encoded_bind_response = sock.recv(2)
length = db.decode_length(encoded_bind_response)
encoded_bind_response += sock.recv(length - 2)
print('done.')

bind_response = db.decode('LDAPMessage', encoded_bind_response)
pprint(bind_response)
sock.close()
