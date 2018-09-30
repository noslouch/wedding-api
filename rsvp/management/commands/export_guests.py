import csv

from django.core.management.base import BaseCommand

from rsvp.models import Invitation, Guest

FIELDS = [
    'first_name',
    'last_name',
    'is_plus_one',
    'wedding_rsvp',
    'sunday_brunch',
    'rehearsal_rsvp',
]


class Command(BaseCommand):
    help = 'Export guests based on predefined option sets'

    def add_arguments(self, parser):
        parser.add_argument('set', choices=['yes', 'no', 'noresponse'])
        parser.add_argument('csvfile', help='output file path')
        parser.add_argument('-d', '--dry-run', action='store_true', default=False)

    def handle(self, *args, **options):
        choice = options['set']
        out = options['csvfile']
        if choice == 'yes':
            self.export(dict(wedding_rsvp=True), out)
        elif choice == 'no':
            self.export(dict(wedding_rsvp=False), out)
        elif choice == 'noresponse':
            self.export(dict(wedding_rsvp__isnull=True), out)

    def export(self, query, outfile):
        print("running query: {}={}".format(*query, *query.values()))
        guests = Guest.objects.filter(**query)

        print('found {} guests'.format(guests.count()))
        with open(outfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDS)

            writer.writeheader()
            for guest in guests:
                writer.writerow({key: getattr(guest, key) for key in FIELDS})
