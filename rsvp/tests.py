import requests_mock

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rsvp.models import Invitation, Guest


class InvitationTestCase(APITestCase):
    def setUp(self):
        self.invitation = Invitation.objects.create(address='123 Main St')
        self.plus_one = Invitation.objects.create(address='456 Plus One Blvd',
                                                  plus_one=True)
        self.rehearsal_dinner = Invitation.objects.create(address='789 Rehearsal Drive',
                                                          rehearsal_dinner=True)

        self.mom = Guest.objects.create(
            first_name='Sandy',
            last_name='Esner',
            invitation=self.invitation)

        self.dad = Guest.objects.create(
            first_name='Bill',
            last_name='Esner',
            email='dad@wedding.com',
            invitation=self.invitation)

        self.sis = Guest.objects.create(
            first_name='Laura',
            last_name='Esner',
            invitation=self.plus_one)

        self.best_man = Guest.objects.create(
            first_name='Brad',
            last_name='Farberman',
            invitation=self.rehearsal_dinner)

    def test_invitation_lookup(self):
        url = reverse('invitation-list')

        response = self.client.get(url, {'q': 'farberman'})
        invite = response.data[0]
        self.assertEqual(invite['id'], self.rehearsal_dinner.id,
                         'can look up invitation by last name')
        self.assertEqual(len(invite['guests']), 1, 'includes just the one guest')

        response = self.client.get(url, {'q': 'dad@wedding.com'})
        invite = response.data[0]
        self.assertEqual(invite['id'], self.invitation.id, 'can look up invitation by email')
        self.assertEqual(len(invite['guests']), 2, 'includes correct number of guests')
        self.assertEqual(
            [g['first_name'] for g in invite['guests']],
            [self.dad.first_name, self.mom.first_name],
            'includes expected guests')

        response = self.client.get(url, {'q': 'esner'})
        self.assertEqual(len(response.data), 2,
                         'multiple matches can be returned')

    def test_lookup_by_full_name(self):
        url = reverse('invitation-list')

        response = self.client.get(url, {'q': 'brad farberman'})
        self.assertEqual(len(response.data), 1, 'should return one invitation')
        invite = response.data[0]
        self.assertEqual(invite['id'], self.rehearsal_dinner.id,
                         'can look up invitation by last name')
        self.assertEqual(len(invite['guests']), 1, 'includes just the one guest')

    @requests_mock.mock()
    def test_sending_rsvp(self, r_mock):
        url = reverse('invitation-detail', kwargs={'pk': self.invitation.id})
        data = {
            'music_pref': 'david bowie',
            'guests': [{
                'id': self.mom.id,
                'wedding_rsvp': True,
            }, {
                'id': self.dad.id,
                'wedding_rsvp': True,
            }]
        }

        r_mock.post("{}".format(settings.MAILGUN_API))

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invite = Invitation.objects.get(pk=self.invitation.id)
        mom = Guest.objects.get(pk=self.mom.id)
        dad = Guest.objects.get(pk=self.dad.id)

        self.assertEqual(invite.music_pref, 'david bowie', 'updates music pref')

        self.assertEqual(mom.wedding_rsvp, True, 'updates associated rsvp')
        self.assertEqual(dad.wedding_rsvp, True, 'updates associated rsvp')

        one_and_one = {
            'guests': [{
                'id': self.mom.id,
                'wedding_rsvp': True,
            }, {
                'id': self.dad.id,
                'wedding_rsvp': False,
            }]
        }
        response = self.client.patch(url, one_and_one, format='json')

        mom = Guest.objects.get(pk=self.mom.id)
        dad = Guest.objects.get(pk=self.dad.id)

        # can update guests with different RSVP values
        # and can update a guest after they've RSVP'd
        self.assertEqual(mom.wedding_rsvp, True)
        self.assertEqual(dad.wedding_rsvp, False)

    @requests_mock.mock()
    def test_plus_one(self, r_mock):
        invite_url = reverse('invitation-detail', kwargs={'pk': self.plus_one.id})
        new_guest_url = reverse('guest-list')
        rsvp_data = {
            'guests': [{
                'id': self.sis.id,
                'wedding_rsvp': True,
            }]
        }
        plus_one_data = {
            'first_name': 'Johnny',
            'last_name': 'McCullough',
            'wedding_rsvp': True,
            'invitation': self.plus_one.id
        }

        r_mock.post("{}".format(settings.MAILGUN_API))

        rsvp_response = self.client.patch(invite_url, rsvp_data, format='json')
        guest_response = self.client.post(new_guest_url, plus_one_data, format='json')

        self.assertEqual(rsvp_response.status_code, status.HTTP_200_OK)
        self.assertEqual(guest_response.status_code, status.HTTP_201_CREATED, 'response with 201')

        invite = Invitation.objects.get(pk=self.plus_one.id)
        sis = Guest.objects.get(pk=self.sis.id)
        johnny = Guest.objects.get(pk=guest_response.data['id'])

        self.assertEqual(invite.guests.count(), 2)
        self.assertEqual(sis.invitation.pk, invite.pk)
        self.assertEqual(johnny.invitation.pk, invite.pk)

        self.assertEqual(sis.wedding_rsvp, True)
        self.assertEqual(johnny.wedding_rsvp, True)

        update_date_name = {
            'guests': [{
                'id': johnny.id,
                'first_name': 'Benny',
                'last_name': 'The Dog'
            }]
        }
        updated_date = self.client.patch(invite_url, update_date_name, format='json')
        self.assertEqual(updated_date.status_code, status.HTTP_200_OK)

        invite = Invitation.objects.get(pk=self.plus_one.id)
        benny = Guest.objects.get(pk=johnny.id)
        self.assertEqual(benny.first_name, 'Benny')
        self.assertEqual(benny.last_name, 'The Dog')
        self.assertEqual(benny.invitation.pk, invite.pk)
        self.assertEqual(benny.wedding_rsvp, True)

    @requests_mock.mock()
    def test_rehearsal_dinner(self, r_mock):
        url = reverse('invitation-detail', kwargs={'pk': self.rehearsal_dinner.id})
        data = {
            'guests': [{
                'id': self.best_man.id,
                'rehearsal_rsvp': True,
            }]
        }

        r_mock.post("{}".format(settings.MAILGUN_API))

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        best_man = Guest.objects.get(pk=self.best_man.id)

        self.assertEqual(best_man.rehearsal_rsvp, True, 'updates associated rsvp')

    @requests_mock.mock()
    def test_protect_rsvp(self, r_mock):
        basic_invite = reverse('invitation-detail', kwargs={'pk': self.invitation.id})
        rehearsal_rsvp = reverse('invitation-detail', kwargs={'pk': self.rehearsal_dinner.id})
        new_guest_url = reverse('guest-list')

        wants_two_dinners = {
            'guests': [{
                'id': self.mom.id,
                'rehearsal_rsvp': True
            }]
        }

        r_mock.post("{}".format(settings.MAILGUN_API))

        no_rehearsal = self.client.patch(rehearsal_rsvp, wants_two_dinners, format='json')
        self.assertEqual(
            no_rehearsal.status_code, status.HTTP_400_BAD_REQUEST,
            """
            server will not accept an attempt to rsvp for a
            rehearsal dinner on an invite that is not a rehearsal dinner invite
            """)

        crasher = {
            'first_name': 'Alan',
            'last_name': 'Eckstein',
            'wedding_rsvp': True,
            'invitation': self.invitation.id,
        }

        no_invite = self.client.post(new_guest_url, crasher, format='json')
        self.assertEqual(
            no_invite.status_code, status.HTTP_400_BAD_REQUEST,
            """
            server will not accept an attempt to rsvp a new
            guest with an invitation that does not provide for a plus one
            """)

        change_my_invite = {
            'plus_one': True,
            'rehearsal_dinner': True
        }
        self.client.post(basic_invite, change_my_invite, format='json')
        invite = Invitation.objects.get(pk=self.invitation.id)
        self.assertEqual(invite.plus_one, False, 'plus_one remains false')
        self.assertEqual(invite.rehearsal_dinner, False, 'rehearsal_dinner remains false')

        # and again for patch
        self.client.patch(basic_invite, change_my_invite, format='json')
        invite = Invitation.objects.get(pk=self.invitation.id)
        self.assertEqual(invite.plus_one, False, 'plus_one remains false')
        self.assertEqual(invite.rehearsal_dinner, False, 'rehearsal_dinner remains false')

        too_many_guests = {
            'guests': [{
                'id': self.mom.id,
                'wedding_rsvp': True
            }, {
                'id': self.dad.id,
                'wedding_rsvp': True
            }, {
                'id': self.sis.id,
                'wedding_rsvp': True
            }]
        }

        too_many = self.client.patch(basic_invite, too_many_guests, format='json')
        invite = Invitation.objects.get(pk=self.invitation.id)
        self.assertEqual(too_many.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invite.guests.count(), 2, 'guests are not changed')
