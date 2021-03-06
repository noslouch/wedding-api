from .base import *

ALLOWED_HOSTS = ['localhost']
CORS_ORIGIN_ALLOW_ALL = True
DEBUG = True

# keep the html browseable api in dev
from rest_framework import routers
ROUTER = routers.DefaultRouter(trailing_slash=False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
    }
}
