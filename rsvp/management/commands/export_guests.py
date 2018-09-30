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
        parser.add_argument('-o', '--out', action='store', dest='csvfile', help='output file path')
        parser.add_argument('-p', '--print', action='store_true', default=False)

    def handle(self, *args, **options):
        choice = options['set']
        out = options['csvfile']
        export = not options['print']

        if choice == 'yes':
            query = dict(wedding_rsvp=True)
        elif choice == 'no':
            query = dict(wedding_rsvp=False)
        elif choice == 'noresponse':
            query = dict(wedding_rsvp__isnull=True)

        if export:
            if not out:
                self.stderr.write("Outfile required")
                return
            self.export(query, out)
        else:
            self.print_out(query)

    def export(self, query, outfile):
        self.stdout.write("running query: {}={}".format(*query, *query.values()))
        guests = Guest.objects.filter(**query)

        self.stdout.write('found {} guests'.format(guests.count()))
        with open(outfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDS)

            writer.writeheader()
            for guest in guests:
                writer.writerow({key: getattr(guest, key) for key in FIELDS})

    def print_out(self, query):
        guests = Guest.objects.filter(**query)

        self.stdout.write("\n".join(["{} {}".format(g.first_name, g.last_name)
                          for g in guests]))
        self.stdout.write(self.style.SUCCESS("%d Guests" % guests.count()))
