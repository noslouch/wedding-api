from django.contrib import admin
from .models import Invitation, Guest

admin.site.register(Invitation)
admin.site.register(Guest)

class WeddingAdmin(admin.AdminSite):
    site_header = 'Melissa and Brian are Getting Married!'
    site_title = 'Melissa and Brian are Getting Married!'
    site_url = 'https://melissaandbriangetmarried.com'

admin_site = WeddingAdmin()
