# Generated by Django 2.1 on 2018-08-31 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0006_guest_is_plus_one'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]
