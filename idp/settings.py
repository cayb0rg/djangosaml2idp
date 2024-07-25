import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'jp+hvkp_$@(774h6=zljw1kd+els6q!u8@1agj!=%h*7vt&t=y'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosaml2idp',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'idp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'idp.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
    },
  },
  'loggers': {
    '': {
      'handlers': ['console'],
      'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
    },
  },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# SAML2 IdP settings

import saml2
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary

SESSION_COOKIE_NAME = 'sessionid_idp'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SAML_IDP_BASE_URL = 'http://localhost:9000/idp'

SAML_IDP_CONFIG = {
    'debug' : DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/usr/bin/xmlsec1']),
    'entityid': '{}/metadata'.format(SAML_IDP_BASE_URL),
    'description': 'Django SAML2 IdP',

    'service': {
        'idp': {
            'name': 'Django SAML2 IdP',
            'endpoints': {
                'single_sign_on_service': [
                    ('{}/sso/post'.format(SAML_IDP_BASE_URL), saml2.BINDING_HTTP_POST),
                    ('{}/sso/redirect'.format(SAML_IDP_BASE_URL), saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
            # 'sign_response': True,
            # 'sign_assertion': True,
        },
    },

    'metadata': {
        'local': [os.path.join(BASE_DIR, 'metadata/metadata.xml')],
    },

    # Signing
    'key_file': os.path.join(BASE_DIR, 'certificates/private.key'),
    'cert_file': os.path.join(BASE_DIR, 'certificates/public.cert'),
    # Encryption
    'encryption_keypairs': [{
        'key_file': os.path.join(BASE_DIR, 'certificates/private.key'),
        'cert_file': os.path.join(BASE_DIR, 'certificates/public.cert'),
    }],
    'valid_for': 365 * 24,
}

# Each key in this dictionary is a SP our IDP will talk to

SAML_IDP_SPCONFIG = {
    'http://localhost/saml2/metadata': {
        'entity_id': 'http://localhost/saml2/metadata',
        'processor': 'djangosaml2idp.processors.BaseProcessor',
        'nameid_field': 'username',
        'attribute_mapping': {
            'uid': 'username',
            'mail': 'email',
            'eduPersonAffiliation': 'role',
            'givenName': 'first_name',
            'sn': 'last_name',
            'displayName': 'display_name',
        },
        'assertion_consumer_service': {
            'url': 'http://localhost/saml2/acs/',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
        },
        'single_logout_service': {
            'url': 'http://localhost/saml2/logout/?sls=1/',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
        },
        'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
        'sign_response': False,
        'sign_assertion': False,
        'signing_algorithm': saml2.xmldsig.SIG_RSA_SHA256,
        'digest_algorithm': saml2.xmldsig.DIGEST_SHA256,
        'encrypt_saml_responses': False,
    },
    'bare_minimum_config': {}
}