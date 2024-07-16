# api/admin.py

from django.contrib import admin
from .models import Investor, Bill, CapitalCall

admin.site.register(Investor)
admin.site.register(Bill)
admin.site.register(CapitalCall)