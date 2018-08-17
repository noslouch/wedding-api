from rest_framework import viewsets
from .models import Invitation, Guest
from .serializers import InvitationSerializer, GuestSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
