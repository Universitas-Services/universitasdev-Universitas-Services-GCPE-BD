"""Conftest global: Override DB a SQLite para tests locales."""


def pytest_configure(config):
    """Override DATABASES para usar SQLite en tests."""
    from django.conf import settings

    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "HOST": "",
        "OPTIONS": {},
        "PASSWORD": "",
        "PORT": "",
        "TEST": {"NAME": ":memory:", "MIRROR": None},
        "TIME_ZONE": None,
        "USER": "",
    }

    # Evitar envío real de emails en tests
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
