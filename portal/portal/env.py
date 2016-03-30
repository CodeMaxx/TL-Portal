import sqlite3

conn = sqlite3.connect('db.sqlite3')
SECRET_KEY = 'i^1h9k7aiks%+$g7%dkes_h-o0$ql-d$&=fji6swmrgxyjkn%4'
redirecturl = 'http://tinker.tl/redirect'
clientid = 'LEdwtHLmG59vmQAh3O8YE1MyeuEUQo0vF59BHN4y'
clientsecret = 'Ojxvb3sPNZhBa5kdvQeznMGMJf0EhRNqehMBKEkLRX68tzFkpt7X3kbXSSaaVP16aD7HUoi6Py142sCrfVnqawIhKZwDoRsTu4Hb9vnpkwW6K8SeiE7ezwARlPRU7fUJ'
password = "87asyadg36b26ccncy287292mu7gdsasdjiiecm"

TECHINICIAN_NAME = 'Vinayak Shelar'
POST = 'TL Technician'
INSTITUTE = 'IIT Bombay'



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Host for sending e-mail.
EMAIL_HOST = 'smtp-auth.iitb.ac.in'

# Port for sending e-mail.
EMAIL_PORT = 25

ADMINS = [('Siddharth', 'siddharth.bulia@gmail.com')]
MANAGERS = [('Siddharth','siddharth.bulia@gmail.com')]

c = conn.cursor()
c.execute("select secondary_email,password from issuestuff_member where secondary_email='siddharth.';")

SERVER_EMAIL = 'admin@tinker.tl'
EMAIL_HOST_USER, EMAIL_HOST_PASSWORD =  c.fetchone()
conn.close()

EMAIL_USE_TLS = True

# Email Id which will appear in From header in email
EMAIL_FROM = "admin@tinker.tl"

EMAIL_BACKEND = "core.notification.IITBEmailBackend"

EMAIL_SUBJECT_PREFIX = "[Tinkerers' Lab]"
# SERVER_EMAIL = ""

USE_L10N=False

APPEND_SLASH = True