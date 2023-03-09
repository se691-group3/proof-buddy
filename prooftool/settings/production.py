from .base import *

DEBUG = False
ALLOWED_HOSTS = ['proofbuddy.cci.drexel.edu','129.25.203.33']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'production_db',
    }
}
