from .base import *

ALLOWED_HOSTS = ['api.melissaandbriangetmarried.com']

DEBUG = False

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# so the prod API isn't user navigable
from rest_framework import routers
ROUTER = routers.SimpleRouter(trailing_slash=False)
