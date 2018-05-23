# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
import versioneer


setup(name='codeforlife-portal',
      cmdclass=versioneer.get_cmdclass(),
      version=versioneer.get_version(),
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'django==1.8.3',
          'django-appconf==1.0.1',
          'django-countries==3.4.1',
          'djangorestframework==3.1.3',
          'django-jquery==1.9.1',
          'django-autoconfig==0.3.6',
          'django-pipeline==1.5.4',
          'django-recaptcha==1.3.1',  # 1.4 dropped support for < 1.11

          'pyyaml==3.10',
          'rapid-router >= 1.0.0.post.dev1',
          'six==1.11.0',
          'aimmo',
          'docutils==0.12',
          'reportlab==3.2.0',
          'postcodes==0.1',
          'django-formtools==1.0',
          'django-two-factor-auth==1.2.0',
          'urllib3==1.22',
          'requests==2.18.4',

          'django-classy-tags==0.6.1',
          'django-treebeard==3.0',
          'django-sekizai==0.8.2',

          'django-online-status==0.1.0',

          'Pillow==2.9.0',
          'django-reversion==1.9.3',
          'sqlparse',
          'libsass',
      ],
      tests_require=[
          'django-setuptest',
          'django-selenium-clean==0.2.1',
          'responses==0.4.0',
          'selenium==2.48.0',
      ],
      test_suite='setuptest.setuptest.SetupTestSuite',
      zip_safe=False,
      )
