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
        "django>=1.10.8, <= 1.11.24",
        "django-appconf==1.0.1",
        "django-countries==5.4",
        "djangorestframework>=3.8.2, < 3.9.0",
        "django-jquery==1.9.1",
        "django-autoconfig==0.8.0",
        "django-pipeline==1.6.14",
        "django-recaptcha==1.3.1",  # 1.4 dropped support for < 1.11
        "pyyaml==4.2b1",
        "rapid-router >= 1.0.0.post.dev1",
        "six==1.11.0",
        "aimmo",
        "reportlab==3.2.0",
        "django-formtools==2.1",
        "django-two-factor-auth>=1.6.2,<1.7.0",
        "django-otp<=0.7.0",  # we needed to fix this due to a wide ranged dependency in django-two-factor-auth
        "urllib3==1.24.2",
        "requests==2.20.0",
        "django-treebeard==4.3",
        "django-sekizai==1.0.0",
        "Pillow==5.4.1",
        "sqlparse",
        "libsass",
        "django-forms-bootstrap",
        "phonenumbers>=8.11.0, <8.12.0",
        "more-itertools==5.0.0",  # 8.0.2 doesn't support Python <=3.4
        "future"
    ],
    zip_safe=False,
)
