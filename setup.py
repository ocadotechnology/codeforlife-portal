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
        "django==2.2.24",
        "django-countries==6.1.3",
        "djangorestframework==3.12.2",
        "django-pipeline==1.6.14",  # Setting this to 1.6.14 as 1.7 causes issue with compiling SCSS files
        "django-recaptcha==2.0.6",
        "pyyaml==5.4",
        "rapid-router >= 1.0.0.post.dev1",
        "aimmo",
        "reportlab==3.5.55",
        "django-formtools==2.2",
        "django-otp==1.0.2",  # we needed to fix this due to a wide ranged dependency in django-two-factor-auth
        "requests==2.25.0",
        "django-treebeard==4.3.1",
        "django-sekizai==2.0.0",
        "django-classy-tags==2.0.0",
        "Pillow==8.0.1",
        "sqlparse==0.4.1",
        "libsass==0.20.1",
        "phonenumbers==8.12.12",
        "more-itertools==8.6.0",
        "django-hijack==2.1.10",
        "django-hijack-admin==2.1.10",
        "future==0.18.2",
        f"cfl-common=={version}",
        "django-ratelimit==3.0.1",
        "django-preventconcurrentlogins==0.8.2",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
    ],
    zip_safe=False,
)
