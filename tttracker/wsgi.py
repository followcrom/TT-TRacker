import os
import sys

sys.path.append("/home/bitnami/djangoapp/tttracker")
os.environ.setdefault("PYTHON_EGG_CACHE", "/home/bitnami/djangoapp/tttracker/egg_cache")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tttracker.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()