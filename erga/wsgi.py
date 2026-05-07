"""
WSGI config for the CBP/ERGA GTC project.
PROJECT_DIR is derived from this file's location — no deployment-specific edits needed.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erga.settings')

application = get_wsgi_application()
