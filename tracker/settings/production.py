from .common import *
import dj_database_url
import os


ALLOWED_HOSTS = ['127.0.0.1', 'herokuapp.com']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL')) 
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'jfissuetracker@gmail.com'
EMAIL_HOST_PASSWORD = env.str('EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
