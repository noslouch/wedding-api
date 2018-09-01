import requests

from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import ParseError

from .models import Invitation, Guest
from .serializers import InvitationSerializer, GuestSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        tokens = [t.title() for t in query.split(' ') if t]
        if len(tokens) > 100:  # basic guard
            return Invitation.objects.none()
        if query and tokens:
            return Invitation.objects.filter(
                Q(address__icontains=query) |
                Q(guests__last_name__in=tokens) |
                Q(guests__first_name__in=tokens) |
                Q(guests__email__icontains=query)
            ).distinct()
        else:
            return Invitation.objects.all()

    def list(self, request):
        if not self.request.query_params.get('q') and not settings.DEBUG:
            raise ParseError('Must supply a query parameter.')
        else:
            return super().list(request)

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)

        invite = self.get_object()
        guests = invite.guests.all()
        subject = " & ".join(
            ["{0.first_name} {0.last_name}".format(g) for g in guests]
        )

        guest_rsvps = []
        for g in guests:
            name = "{0.first_name} {0.last_name}".format(g)
            wedding = "Yes" if g.wedding_rsvp is True else "No" if g.wedding_rsvp is False else "No Response"
            brunch = "Yes" if g.sunday_brunch is True else "No" if g.sunday_brunch is False else "No Response"
            rehearsal = "Yes" if g.rehearsal_rsvp is True else "No" if g.rehearsal_rsvp is False else "No Response"

            guest_rsvps.append("""
{0}
Wedding: {1}
Brunch: {2}
Rehearsal: {3}
                """.format(name, wedding, brunch, rehearsal))

        guest_rsvps = "\n".join(guest_rsvps)

        text = """
Here's what they said:
{0}

Music Choice: {1}

Other note: {2}
""".format(guest_rsvps, invite.music_pref, invite.note)

        data = {
            'from': 'bots@melissaandbriangetmarried.com',
            'to': 'esnerwhitton@gmail.com',
            'subject': "{} just sent in an RSVP!".format(subject),
            'text': text,
        }

        requests.post(settings.MAILGUN_API,
                      auth=('api', settings.MAILGUN_KEY),
                      data=data)
        return res


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    http_method_names = ['post', 'patch']
