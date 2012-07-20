import os
import sys
from setuptools import setup, find_packages

version = __import__('fiber').__version__

if sys.argv[-1] == 'publish': # upload to pypi
    os.system("python setup.py register sdist upload")
    print "You probably want to also tag the version now:"
    print "  git tag -a %s -m 'version %s'" % (version, version)
    print "  git push --tags"
    sys.exit()

setup(
    name='django-fiber',
    version=version,
    license='Apache License, Version 2.0',

    install_requires=[
        'Pillow==1.7.7',
        'django-mptt==0.5.1',
        'django-compressor>=0.7.1',
        'djangorestframework==0.3.3'
    ],

    description='Django Fiber - a simple, user-friendly CMS for all your Django projects',
    long_description=open('README.rst').read(),

    author='Dennis Bunskoek',
    author_email='dbunskoek@leukeleu.nl',

    url='https://github.com/ridethepony/django-fiber',
    download_url='https://github.com/ridethepony/django-fiber/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
