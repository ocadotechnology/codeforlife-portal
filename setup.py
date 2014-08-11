from setuptools import find_packages, setup
setup(name='portal',
      version='1.0',
      packages=find_packages(),
      include_package_data=True,
      install_requires = [
        'django-appconf==0.6',
        'django-casper==0.0.2',
        'djangorestframework==2.3.9',
        'unittest2==0.5.1',
        'pyyaml==3.11',
        'six==1.6.1',
        'docutils==0.11',
        'django-recaptcha==1.0',
        'django-jquery==1.9.1',
        'postcodes==0.1',
        'django-two-factor-auth==1.0.0-beta3',
        'django==1.7c1',
        'reportlab==3.1.29'
      ],
      dependency_links = [
        'https://www.djangoproject.com/download/1.7c1/tarball/#egg=django-1.7c1',
        'https://bitbucket.org/rptlab/reportlab/get/tip.zip#egg=reportlab-3.1.29',
      ],
)
