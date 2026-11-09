import os

# Same settings as tests/conftest.py, so these tests also run with `--noconftest`
# (e.g. on Windows, where the full app cannot load without python-ldap).
os.environ.setdefault("PRODUCTION", "True")
os.environ.setdefault("TESTING", "True")
