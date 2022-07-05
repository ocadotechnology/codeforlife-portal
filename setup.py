# -*- coding: utf-8 -*-
import re
import sys

from setuptools import find_packages, setup

with open("portal/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name="codeforlife-portal",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django==3.2.14",
        "django-countries==7.3.1",
        "djangorestframework==3.13.1",
        "django-pipeline==2.0.8",
        "django-recaptcha==2.0.6",
        "pyyaml==5.4.1",
        "rapid-router>=4",
        "aimmo>=2",
        "reportlab==3.6.1",
        "django-formtools==2.2",
        "django-otp==1.0.2",  # we needed to fix this due to a wide ranged dependency in django-two-factor-auth
        "requests==2.25.0",
        "django-treebeard==4.3.1",
        "django-sekizai==2.0.0",
        "django-classy-tags==2.0.0",
        "sqlparse==0.4.2",
        "libsass==0.21.0",
        "phonenumbers==8.12.12",
        "more-itertools==8.6.0",
        "future==0.18.2",
        f"cfl-common=={version}",
        "django-ratelimit==3.0.1",
        "django-preventconcurrentlogins==0.8.2",
        "django-csp==3.7",
        "setuptools==62.1.0",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
    ],
    zip_safe=False,
)
