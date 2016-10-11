import os
import sys
from setuptools import setup, find_packages

version = __import__('fiber').__version__

if sys.version_info[0] > 2:
    sys.exit('Python > 2 is unsupported.')

if sys.argv[-1] == 'publish':  # upload to pypi
    os.system("python setup.py register sdist bdist_egg bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

setup(
    name='django-fiber',
    version=version,
    license='Apache License, Version 2.0',

    install_requires=[
        'Pillow>=2.2.1',
        'django-mptt>=0.6.1',
        'django_compressor>=1.4,<2.0',
        # Cannot use drf < 3.1 as pagination has completely changed.
        'djangorestframework>=3.1.0,<=3.4.7',
        'easy-thumbnails>=2.2',
    ],

    description='Django Fiber - a simple, user-friendly CMS for all your Django projects',
    long_description=open('README.md').read(),

    author='Dennis Bunskoek',
    author_email='dbunskoek@leukeleu.nl',

    url='https://github.com/ridethepony/django-fiber',
    download_url='https://github.com/ridethepony/django-fiber/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
