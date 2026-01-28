import sys

# This must run before Django or any other module imports sqlite3
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("Success: Pytest is using pysqlite3-binary")
except ImportError:
    print("Warning: pysqlite3-binary not found, using system sqlite")

# Only after the swap do we let Django/Pytest proceed
import os
import django
from django.conf import settings
