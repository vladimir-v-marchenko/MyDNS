# -*- encoding: utf-8 -*-
# Create your views here.

from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404, render, render_to_response
from django.template import Context, RequestContext, Template

import subprocess

from web2dns.models import *

from contentcheck import contentcheck


def params2rrobject(url_object):
	objectparts = url_object.split('.')
	if len(objectparts) < 3:
		raise Http404

	url_domain = '.'.join(objectparts[-2:])
	domain = get_object_or_404(Domain, domain=url_domain)

	url_host = '.'.join(objectparts[:-2])
	rrobject = get_object_or_404(RRObject, domain=domain, name=url_host)

	return rrobject



def params2user(url_user, url_pass):
	user = authenticate(username=url_user, password=url_pass)
	return user



def auth_user_or_userkey_for_rrobject(user, url_user, url_pass, rrobject):
	if user is not None:
		if not user.is_active:
			return False

	if rrobject.user == user:
		return 'username/password'

	if (rrobject.user.username == url_user and rrobject.updatekey == url_pass):
		return 'username/rrobject key'

	return False



def build_dnsupdaterequest(opts, delete=True):
	if type(opts) != dict:
		return None
	opts['serverip'] = '89.238.82.158'

	command_start = 'server %(serverip)s\nzone %(domain)s\n'
	command_delete = 'update delete %(hostname)s %(rrtype)s\n'
	command_add = 'update add %(newcontent)s\n'
	command_send = 'send\nquit\n'

	commands = ''
	try:
		commands += command_start % opts
	except KeyError:
		return None

	if delete:
		try:
			commands += command_delete % opts
		except KeyError:
			return None

	if opts.get('hostname') != '-':
		try:
			commands += command_add % opts
		except KeyError:
			return None

	commands += command_send

	return commands



##############################################################################

def ip(Request):
	env = {}
	env['REMOTE_ADDR'] = Request.META.get('REMOTE_ADDR') or ''
	env['FWD_FOR'] = Request.META.get('X-FORWARDED-FOR') or ''

	return render_to_response('ip.html', RequestContext(Request, env), mimetype='text/plain')



def update(Request):
	# .../update.php?username=<username>&password=<pass>&hostname=<domain>&ip=<ipaddr>
	url_user = Request.GET.get('username')
	url_pass = Request.GET.get('password')
	url_object = Request.GET.get('hostname')
	url_rrtype = Request.GET.get('rrtype') or 'A'
	url_content = Request.GET.get('ip') or Request.GET.get('content')

	url_rrtype = url_rrtype.upper()

	rrobject = params2rrobject(url_object)

	user = params2user(url_user, url_pass)

	authenticated = auth_user_or_userkey_for_rrobject(user, url_user, url_pass, rrobject)
	if not authenticated:
		env = {'textcontent':'Authentication error'}
		return render_to_response('plain.txt', RequestContext(Request, env), mimetype='text/plain')

	rrs = rrobject.resourcerecord_set.filter(type=url_rrtype)
	env = {}
	if len(rrs) == 0:
		# Erzeugen
		rr = ResourceRecord(type=url_rrtype, name=rrobject, content='(Fresh RR)')
	elif len(rrs) == 1:
		# Ersetzen
		rr = rrs[0]
	else:
		raise Http404


	# ResourceRecord existiert genau 1x, entweder frisch oder alt
	if rr.content != url_content:
		if contentcheck(url_rrtype, url_content):
			if rr.id:
				old_content = unicode(rr)
			else:
				old_content = rr.content
			rr.content = url_content
			rr.save()

			opts = {}
			opts['domain'] = rrobject.domain.domain
			opts['hostname'] = unicode(rrobject)
			opts['rrtype'] = url_rrtype
			opts['newcontent'] = unicode(rr)
			nsupdate_command = build_dnsupdaterequest(opts)

			proc = subprocess.Popen(['/usr/bin/nsupdate', '-k', '/opt/etc/DYNDNS.key'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output = proc.communicate(input=nsupdate_command)
			env['textcontent'] = 'New: %s\nOld: %s\nUser: %s, identified by %s' % (rr, old_content, user or url_user, authenticated)
			if output != ('', ''):
				env['textcontent'] += '\nnsupdate stdout: %s\nnsupdate stderr: %s' % output
		else:
			env['textcontent'] = 'No valid update data'
	else:
		env['textcontent'] = 'No update, same data as before'

	return render_to_response('plain.txt', RequestContext(Request, env), mimetype='text/plain')



def profile(Request):
	env = {'rrobjects':Request.user.rrobject_set.all()}
	return render_to_response('profile.html', RequestContext(Request, env))
	
