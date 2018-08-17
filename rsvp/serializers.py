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

    def validate(self, data):
        if self.context['request'].method == 'POST':
            invitation = data.get('invitation')
            # assert that given invitation allows for a plus one
            if invitation and not invitation.plus_one:
                raise serializers.ValidationError("Guest cannot be added to given invitation. Invitation does not provide for a plus one.")
        return super().validate(data)


class InvitationSerializer(serializers.ModelSerializer):
    guests = GuestSerializer(many=True)
    plus_one = serializers.BooleanField(read_only=True)
    rehearsal_dinner = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = ('id', 'plus_one', 'rehearsal_dinner', 'music_pref', 'guests')
