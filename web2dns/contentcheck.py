# -*- encoding: utf-8 -*-

import re
import socket


re_txt = re.compile(r'^[ "0-9a-zA-Z_!?&+-]+$')



def contentcheck(rrtype, content):
	rrtype = rrtype.upper()

	if rrtype == 'A':
		try:
			socket.inet_pton(socket.AF_INET, content)
		except socket.error:
			return False
		return True

	elif rrtype == 'AAAA':
		try:
			socket.inet_pton(socket.AF_INET6, content)
		except socket.error:
			return False
		return True

	elif rrtype == 'TXT':
		if re_txt.search(content):
			return True
		else:
			return False

	else:
		return False

