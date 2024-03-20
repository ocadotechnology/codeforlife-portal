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
        "django==3.2.25",
        "djangorestframework==3.13.1",
        "django-two-factor-auth==1.13.2",
        "django-countries==7.3.1",
        "pyjwt==2.6.0",
        "pgeocode==0.4.0",
    ],
    tests_require=[],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
