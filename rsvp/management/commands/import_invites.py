import csv
import re

from itertools import islice

from django.core.management.base import BaseCommand

from rsvp.models import Invitation, Guest

FIRST = 'First Name(s)'
LAST = 'Last Name(s)'
ADDY = 'Address'
EMAIL = 'Email'
FIELDS = [FIRST, LAST, ADDY, EMAIL]


class Command(BaseCommand):
    help = 'Imports guests from a given CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', help='file path to the csv file')

    def handle(self, *args, **options):
        rows = []
        with open(options['csvfile']) as file:
            reader = csv.DictReader(islice(file, 3, None))
            for row in islice(reader, 4, None):
                rows.append({col: row[col] for col in row if col in FIELDS})
        rows = self.find_pairs(rows)

        for row in rows:
            invite = self.make_invite(row)
            guest = self.make_guest(row, invite)
            print("Added {} to {}".format(guest, invite))

    def find_pairs(self, rows):
        new_rows = []
        last_row = {}
        for row in rows:
            if 'Guest' in row[LAST] or 'Guest' in row[FIRST]:
                # skip this row if they don't actually have a name
                continue
            if not (row.get(FIRST) or row.get(LAST)):
                # skip if they don't have names
                continue
            if 'Guest' in row.get(ADDY, ''):
                # mark this invite as having a plus one
                row['has_plus_one'] = True
            if not row.get(ADDY) and 'Guest' in last_row.get(ADDY, ''):
                # this person is a plus one if they don't have an address
                # and previous row listed a guest
                row['is_plus_one'] = True
            if not row.get(ADDY) and last_row.get(ADDY):
                # no address for this person
                # they're probably part of the previous invite
                row[ADDY] = last_row.get(ADDY)
            new_rows.append(row)
            last_row = row
        return new_rows

    def make_invite(self, row):
        try:
            invite = Invitation.objects.get(address=row[ADDY])
        except Invitation.DoesNotExist:
            invite = Invitation.objects.create(
                address=row[ADDY],
                plus_one=row.get('has_plus_one', False),
            )
        return invite

    def make_guest(self, row, invite):
        guest = Guest.objects.create(
            first_name=row[FIRST],
            last_name=row[LAST],
            email=row.get(EMAIL),
            is_plus_one=row.get('is_plus_one', False),
            invitation=invite,
        )
        return guest
