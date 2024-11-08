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
        "django-recaptcha==4.0.0",
        "pyyaml==6.0.2",
        "importlib-metadata==4.13.0",
        "reportlab==3.6.13",
        "django-formtools==2.5.1",
        "django-otp==1.5.4",
        "requests==2.32.2",
        "django-treebeard==4.7.1",
        "django-sekizai==4.1.0",
        "django-classy-tags==4.1.0",
        "phonenumbers==8.12.12",
        "django-ratelimit==3.0.1",
        "django-preventconcurrentlogins==0.8.2",
        "setuptools==74.0.0",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
    ],
    zip_safe=False,
)
