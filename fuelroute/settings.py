"""Django settings: only what a JSON API with no database needs."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

SECRET_KEY = "dev-only-insecure-key"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = ["planner"]
MIDDLEWARE = ["django.middleware.common.CommonMiddleware"]
ROOT_URLCONF = "fuelroute.urls"
WSGI_APPLICATION = "fuelroute.wsgi.application"
DATABASES = {}
USE_TZ = True
