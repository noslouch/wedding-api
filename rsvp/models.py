from django.db import models


class Invitation(models.Model):
    rehearsal_dinner = models.BooleanField()
    address = models.TextField()
    music_pref = models.TextField(blank=True)


class Guest(models.Model):
    MR = 'mr'
    MRS = 'mrs'
    MS = 'ms'
    DR = 'dr'
    CMMR = 'cmmr'
    TITLE_CHOICES = (
        (MR, 'Mr.'),
        (MRS, 'Mrs.'),
        (MS, 'Ms.'),
        (DR, 'Dr.'),
        (CMMR, 'Cmmr.'),
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    title = models.CharField(max_length=4, choices=TITLE_CHOICES)
    wedding_rsvp = models.BooleanField(null=True)
    rehearsal_rsvp = models.BooleanField(null=True)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE)
