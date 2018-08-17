from .base import *

ALLOWED_HOSTS = ['localhost']
CORS_ORIGIN_ALLOW_ALL = True
DEBUG = True

INSTALLED_APPS += ['django_extensions']

# keep the html browseable api in dev
from rest_framework import routers
ROUTER = routers.DefaultRouter(trailing_slash=False)
