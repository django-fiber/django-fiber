import os
import sys
from setuptools import setup, find_packages

version = __import__('fiber').__version__

if sys.argv[-1] == 'publish':  # upload to pypi
    os.system("python setup.py register sdist bdist_egg bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print(f"  git tag -a {version} -m 'version {version}'")
    print("  git push --tags")
    sys.exit()

with open('requirements.txt') as file:
    reqs = [line for line in file.readlines() if not line.strip().startswith('#')]

setup(
    name='django-fiber',
    version=version,
    license='Apache License, Version 2.0',

    install_requires=reqs,
    python_requires='>=3.6',

    description='Django Fiber - a simple, user-friendly CMS for all your Django projects',
    long_description=open('README.rst').read(),

    author='Dennis Bunskoek',
    author_email='dbunskoek@leukeleu.nl',

    url='https://github.com/django-fiber/django-fiber',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
    ],
    keywords=['cms', 'django']
)
