from .base import *

DEBUG = True
ALLOWED_HOSTS = ['bvm83.cci.drexel.edu', 'www.bvm83.cci.drexel.edu']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'production_db',
    }
}
