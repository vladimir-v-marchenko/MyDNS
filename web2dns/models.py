# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from random import choice
import string

# From http://stackoverflow.com/questions/367586/generating-random-text-strings-of-a-given-pattern
def GenUpdateKey(length=64, chars=string.letters + string.digits):
	return ''.join([choice(chars) for i in range(length)])

##############################################################################

class Domain(models.Model):
	domain = models.CharField(max_length=255)
	user = models.ForeignKey(User, blank=True, null=True, default=None)

	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)


	class Meta:
		ordering = ['domain', ]

	def __unicode__(self):
		return '%s' % self.domain



class RRObject(models.Model):
	name = models.CharField(max_length=128)
	domain = models.ForeignKey(Domain)
	user = models.ForeignKey(User)
	updatekey = models.CharField(max_length=128, default=GenUpdateKey)

	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)


	class Meta:
		ordering = ['domain', 'name',]

	def __unicode__(self):
		return '%s.%s' % (self.name, self.domain)

	def full(self):
		return '%s (owned by %s)' % (self, self.user)



RRTYP = (
	('A', 'A'),
	('AAAA', 'AAAA'),
	('CNAME', 'CNAME'),
	('HINFO', 'HINFO'),
	('MX', 'MX'),
	('SSHFP', 'SSHFP'),
	('TXT', 'TXT'),
)

class ResourceRecord(models.Model):
	name = models.ForeignKey(RRObject)
	type = models.CharField(max_length=255, choices=RRTYP)
	ttl = models.IntegerField(default=60)
	content = models.CharField(max_length=255)

	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)


	class Meta:
		ordering = ['name', 'type',]

	def __unicode__(self):
		return '%s. %s IN %s %s' % (self.name, self.ttl, self.type, self.content)

