from .common import *
import dj_database_url
import os
import sys

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'jf-issue-tracker.herokuapp.com']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

if 'test' in sys.argv or SECRET_KEY=="travis":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
    }
else:
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

    AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = 'us-east-2'
    AWS_STORAGE_BUCKET_NAME = 'jf-issue-tracker-attachments'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    DEFAULT_FILE_STORAGE = 'storage_backends.MediaStorage'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, 'media')

    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)
