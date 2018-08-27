from django.db import models


class Invitation(models.Model):
    rehearsal_dinner = models.BooleanField(default=False)
    plus_one = models.BooleanField(default=False)
    address = models.TextField()
    music_pref = models.TextField(blank=True)

    def __str__(self):
        return self.address


class Guest(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    is_plus_one = models.BooleanField(default=False)

    wedding_rsvp = models.BooleanField(null=True)
    rehearsal_rsvp = models.BooleanField(null=True)
    sunday_brunch = models.BooleanField(null=True)

    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='guests')

    def __str__(self):
        return "{0.first_name} {0.last_name}".format(self)
