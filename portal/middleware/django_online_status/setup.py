#!/usr/bin/env python

from setuptools import setup, find_packages
 
setup(
    name = 'django-online-status',
    version = '0.1.0',
    packages = find_packages(),    
    author = 'Jakub Zalewski',
    author_email = 'zalew7@gmail.com',    
    description = '',
    url='http://bitbucket.org/zalew/django-online-status',    
    classifiers = [
        'Development Status :: Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)

