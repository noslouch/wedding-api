from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html_join
from .models import Invitation, Guest


class WeddingAdmin(admin.AdminSite):
    site_header = 'Melissa and Brian are Getting Married!'
    site_title = 'Melissa and Brian are Getting Married!'
    site_url = 'https://melissaandbriangetmarried.com'


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('address', 'rehearsal_dinner', 'plus_one', 'guests')
    ordering = ['address']
    search_fields = ['address']
    list_filter = ['rehearsal_dinner', 'plus_one']

    def guests(self, invite):
        return format_html_join(
            ', ',
            "<a href=\"{0}\">{1} {2}</a>",
            [(reverse('admin:rsvp_guest_change', args=[g.pk]), g.first_name, g.last_name)
                for g in invite.guests.all()])


class GuestAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'wedding_rsvp',
        'sunday_brunch',
        'rehearsal_rsvp',
        'is_plus_one',
    )
    list_filter = ['wedding_rsvp', 'rehearsal_rsvp', 'sunday_brunch', 'is_plus_one']

    ordering = ['first_name']
    search_fields = ['first_name', 'last_name', 'email']


admin_site = WeddingAdmin()

admin_site.register(Invitation, InvitationAdmin)
admin_site.register(Guest, GuestAdmin)
