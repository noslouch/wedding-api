from django.db.models import Q
from rest_framework import viewsets
from .models import Invitation, Guest
from .serializers import InvitationSerializer, GuestSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            return Invitation.objects.filter(
                Q(address__icontains=query) |
                Q(guests__last_name__icontains=query) |
                Q(guests__first_name__icontains=query) |
                Q(guests__email__icontains=query)
            ).distinct()
        else:
            return Invitation.objects.all()


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
