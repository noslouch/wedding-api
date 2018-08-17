from django.shortcuts import get_object_or_404
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

    def update(self, instance, validated_data):
        # remove nested serialization from data before calling super
        guests = validated_data.pop('guests', [])
        super().update(instance, validated_data)

        for guest in guests:
            g = Guest.objects.get(pk=guest['id'])

            for attr, value in guest.items():
                setattr(g, attr, value)

            g.save()
        return instance

    def validate_guests(self, guests):
        """
        validates given guests:
         - no more than 2 guests per invite
         - ignore any included values for invitation so guests can't switch invite
         - ensure all guests have an id
         - ensure given IDs exist
         - only guests already associated with an invite are accepted
         - make sure a guest can't rsvp to the rehearsal dinner if they weren't invited
        """
        if len(guests) > 2:
            raise serializers.ValidationError("Only two guests per invite.")

        invite = get_object_or_404(Invitation, pk=self.instance.pk)
        valid_guests = invite.guests.values_list('id', flat=True)

        for guest in guests:
            # disregard given invitation, prevents guests swtching invites
            guest.pop('invitation', None)

            if not guest.get('id'):
                raise serializers.ValidationError("All guests must have an id.")

            if not Guest.objects.filter(pk=guest['id']).exists():
                raise serializers.ValidationError(
                    "Guest with id {} does not exist in the database.".format(guest['id']))

            if guest['id'] not in valid_guests:
                raise serializers.ValidationError("Guest does not belong to this invitation.")

            if not invite.rehearsal_dinner:
                if guest.get('rehearsal_rsvp'):
                    raise serializers.ValidationError(
                        "Invitation does not provide for a rehearsal dinner. Please remove 'rehearsal_rsvp' key."
                    )
        return guests
