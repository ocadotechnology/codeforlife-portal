from setuptools import find_packages, setup
setup(name='portal',
      version='1.0',
      packages=find_packages(),
      install_requires = [
        'django-appconf==0.6',
        'django-casper==0.0.2',
        'djangorestframework==2.3.9',
        'unittest2==0.5.1',
        'pyyaml==3.11',
        'six==1.6.1',
        'docutils==0.11',
        'django-recaptcha==1.0',
        'reportlab==3.1.8',
        'django-jquery==1.9.1',
        'postcodes==0.1',
      ],
      dependency_links = [
        'https://www.djangoproject.com/download/1.7c1/tarball/',
      ],
)