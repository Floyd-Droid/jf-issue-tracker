from .common import *
import dj_database_url
import os

DEBUG = False

ALLOWED_HOSTS = ['jf-issue-tracker.herokuapp.com']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

DATABASES = {
    'default': env.db('DATABASE_URL')
}

MAILGUN_SMTP_SERVER = env.str('MAILGUN_SMTP_SERVER')
MAILGUN_SMTP_PORT = env.str('MAILGUN_SMTP_PORT')
MAILGUN_SMTP_LOGIN = env.str('MAILGUN_SMTP_LOGIN')
MAILGUN_SMTP_PASSWORD = env.str('MAILGUN_SMTP_PASSWORD')

EMAIL_HOST = MAILGUN_SMTP_SERVER
EMAIL_PORT = MAILGUN_SMTP_PORT
EMAIL_HOST_USER = MAILGUN_SMTP_LOGIN
EMAIL_HOST_PASSWORD = MAILGUN_SMTP_PASSWORD

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
