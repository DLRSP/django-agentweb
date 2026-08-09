"""Test settings for django-agentweb.

All five domains are enabled here so the full URLconf is exercised. Real sites
enable only what they opt into.
"""

import os

DEBUG = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SECRET_KEY = "NOTASECRET"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "agentweb",
]

SITE_ID = 1

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

ROOT_URLCONF = "tests.urls"

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "agentweb.discovery.middleware.AgentwebDiscoveryMiddleware",
)

USE_TZ = True
LANGUAGE_CODE = "en"
USE_I18N = True

STATIC_URL = "/static/"

# Enable every agent-web domain for the test suite.
AGENTWEB = {
    "LLMS": {
        "ENABLED": True,
        "TITLE": "Test Site",
        "DESCRIPTION": "Test site for django-agentweb.",
        "CACHE_TIMEOUT": 0,
        "SECTIONS": [
            {
                "heading": "Docs",
                "links": [
                    {
                        "title": "About",
                        "url": "https://example.com/about/",
                        "notes": "About this site",
                    }
                ],
            }
        ],
    },
    "JSONLD": {
        "ENABLED": True,
        "PROFILES": [
            "sitewide",
            "breadcrumb",
            "article",
            "faq",
            "lodging",
            "lodging_room",
        ],
    },
    "DISCOVERY": {"ENABLED": True, "WEB_BOT_AUTH": False},
    "WEBMCP": {
        "ENABLED": True,
        "DATA_SOURCE": "proxy",
        "REMOTE_BRIDGE": False,
    },
    "COMMERCE": {"ENABLED": True, "VENDOR": "example-booking-vendor"},
    "SDF": {"ENABLED": True},
}
