# Getting started

## Install

```bash
pip install django-agentweb
```

## Configure

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "agentweb",
]

AGENTWEB = {
    "LLMS": {"ENABLED": True},
    "JSONLD": {"ENABLED": True},
    "DISCOVERY": {"ENABLED": True},
}
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path("", include("agentweb.urls")),
]
```

Only enabled domains register URLs or expose data.
