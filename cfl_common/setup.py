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
        "django>=1.10.8, <= 1.11.24",
        "djangorestframework>=3.8.2, < 3.9.0",
        "django-two-factor-auth>=1.9.1,<1.10.0",
        "django-countries==5.4",
        "wagtail==2.3.*",
    ],
    tests_require=[],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
