# -*- coding: utf-8 -*-
import re

from setuptools import find_packages, setup

with open("../portal/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setup(
    name="cfl-common",
    packages=find_packages(),
    version=version,
    include_package_data=True,
    install_requires=[
        "django==2.2.17",
        "djangorestframework==3.12.2",
        "django-two-factor-auth==1.13",
        "django-countries==6.1.3",
        "wagtail==2.11.*",
    ],
    tests_require=[],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
