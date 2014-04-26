# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'h/_version.py'
versioneer.versionfile_build = '_version.py'
versioneer.tag_prefix = 'v'
versioneer.parentdir_prefix = 'h-'

setup(
    name='h',
    version=versioneer.get_version(),
    packages=find_packages(),

    install_requires=[
        'BeautifulSoup4>=4.2.1',
        'SQLAlchemy>=0.8.0',
        'alembic>=0.6.3',
        'annotator>=0.11.1',
        'clik==0.3.1',
        'deform_bootstrap>=0.2.0',
        'gevent-websocket==0.3.6',
        'horus>=0.9.15',
        'jsonpointer==1.0',
        'jsonschema==1.3.0',
        'pyramid>=1.5',
        'pyramid-basemodel>=0.2',
        'pyramid_deform>=0.2',
        'pyramid_chameleon>=0.1',
        'pyramid-layout>=0.9',
        'pyramid_mailer>=0.13',
        'pyramid-multiauth>=0.4.0',
        'pyramid_tm>=0.7',
        'python-dateutil>=2.1',
        'pyramid-sockjs==0.3.9',
        'requests>=2.2.1',
        'webassets==0.8',
    ],

    author='Hypothes.is Project & contributors',
    maintainer='Randall Leeds',
    maintainer_email='tilgovi@hypothes.is',
    description='The Internet. Peer-reviewed.',
    long_description="A platform for collaborative evaluation of information.",
    license='Simplified (2-Clause) BSD License',
    keywords='annotation web javascript',

    url='http://hypothes.is/',
    download_url='https://github.com/hypothesis/h',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],

    package_data={
        'h': ['assets.yaml', 'development.ini', 'production.ini'],
    },
    include_package_data=True,
    zip_safe=False,

    entry_points={
        'paste.app_factory': [
            'main=h:main'
        ],
        'console_scripts': [
            'hypothesis=h.script:main'
        ],
    },

    cmdclass=versioneer.get_cmdclass(),

    test_suite='test'
)
