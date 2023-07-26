from .base import *

DEBUG = True

INSTALLED_APPS += [

]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEBUG_TOOLBAR_CONFIG = {
    "JQUERY_URL": "",
}
