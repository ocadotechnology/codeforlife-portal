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
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django-pipeline==2.0.8",
        "django-recaptcha==2.0.6",
        "pyyaml==6.0.2",
        "importlib-metadata==4.13.0",
        "rapid-router>=6.3.6",
        "reportlab==3.6.13",
        "django-formtools==2.2",
        "django-otp==1.0.2",  # we needed to fix this due to a wide ranged dependency in django-two-factor-auth
        "requests==2.32.2",
        "django-treebeard==4.3.1",
        "django-sekizai==2.0.0",
        "django-classy-tags==2.0.0",
        "libsass==0.23.0",
        "phonenumbers==8.12.12",
        "more-itertools==8.7.0",
        f"cfl-common=={version}",
        "django-ratelimit==3.0.1",
        "django-preventconcurrentlogins==0.8.2",
        "django-csp==3.7",
        "setuptools==74.0.0",
        "django-import-export",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
    ],
    zip_safe=False,
)
