#!/usr/bin/env python

"""Perform a LDAP bind with an LDAP server.

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

db = asn1tools.compile_files(RFC4511_ASN_PATH)

# Connect to the LDAP server.
sock = socket.socket()
sock.connect(('ldap.forumsys.com', 389))

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

print('Sending LDAP bind request:')
print()
pprint(bind_request)
print()

sock.sendall(encoded_bind_request)

# Receive the bind response, decode it, and print it.
encoded_bind_response = sock.recv(2)
length = db.decode_length(encoded_bind_response)
encoded_bind_response += sock.recv(length - 2)

bind_response = db.decode('LDAPMessage', encoded_bind_response)

print('Received LDAP bind response:')
print()
pprint(bind_response)

sock.close()
