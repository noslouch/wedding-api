from rest_framework import serializers
from .models import Invitation, Guest


class GuestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    wedding_rsvp = serializers.NullBooleanField()
    rehearsal_rsvp = serializers.NullBooleanField(required=False)

    class Meta:
        model = Guest
        fields = (
            'id',
            'first_name',
            'last_name',
            'wedding_rsvp',
            'rehearsal_rsvp',
            'invitation')


class InvitationSerializer(serializers.ModelSerializer):
    guests = GuestSerializer(many=True)
    plus_one = serializers.BooleanField(read_only=True)
    rehearsal_dinner = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = ('id', 'plus_one', 'rehearsal_dinner', 'music_pref', 'guests')
