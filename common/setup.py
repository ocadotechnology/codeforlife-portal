# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="cfl-common-test",
    packages=find_packages(),
    version="0.0.0",
    include_package_data=True,
    tests_require=[],
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
