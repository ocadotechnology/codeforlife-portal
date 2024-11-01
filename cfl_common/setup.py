# -*- coding: utf-8 -*-
import re

from setuptools import find_packages, setup

with open("../portal/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE,
    ).group(1)

setup(
    name="cfl-common",
    long_description="Common package for Code for Life",
    packages=find_packages(),
    version=version,
    include_package_data=True,
    install_requires=[
        "django==4.2.16",
        "djangorestframework==3.15.1",
        "django-two-factor-auth==1.15.1",
        "django-countries==7.6.1",
        "pyjwt==2.6.0",
        "pgeocode==0.4.0",
        "django-pipeline==3.1.0",
        "django-csp==3.8",
        "more-itertools==8.7.0",
        "libsass==0.23.0",
        "django-import-export==4.2.0",
    ],
    tests_require=[],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
