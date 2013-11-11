import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pymongo',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_layout',
    'pyramid_deform',
    'deform',
    'deform_bootstrap',
    'deform_bootstrap_extra',
    'pyramid_persona',
    'authomatic',
    'python-openid',
    #'WebHelpers',
    'Mako',
    'OWSLib',
    'lxml',
    'esgf-pyclient',
    'MyProxyClient',
    'python-dateutil',
    #'egenix-mx-base',
    ]

setup(name='Phoenix',
      version='0.2',
      description='Phoenix',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='phoenix',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = phoenix:main
      """,
      )
