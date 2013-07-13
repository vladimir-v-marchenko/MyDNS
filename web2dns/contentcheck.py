# -*- encoding: utf-8 -*-

import socket

def contentcheck(rrtype, content):
	rrtype = rrtype.upper()

	if rrtype == 'A':
		try:
			socket.inet_aton(content)
		except socket.error:
			return False
		return True

	else:
		return False

