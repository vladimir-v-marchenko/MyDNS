from django.contrib import admin
from models import *

admin.site.register(Domain)
admin.site.register(RRObject)
admin.site.register(ResourceRecord)

