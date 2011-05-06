from setuptools import setup, find_packages

setup(
    name='django-fiber',
    version=__import__('fiber').__version__,
    license='Apache License, Version 2.0',

    install_requires=[
        'django-mptt>=0.4.2',
        'django-piston==0.2.3rc1',
        'django-staticfiles>=1.0.1',
        'beautifulsoup>=3.2.0',
        'django-compressor>=0.7.1',
    ],
    dependency_links=['http://bitbucket.org/jespern/django-piston/get/c4b2d21db51a.tar.gz#egg=django-piston-0.2.3rc1'],

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
