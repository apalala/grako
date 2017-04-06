# -*- coding: utf-8 -*-
# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg

import sys
import io
import setuptools
import grako


SHORT_DESCRIPTION = (
    '{toolname} takes a grammar'
    ' in a variation of EBNF as input, and outputs a memoizing'
    ' PEG/Packrat parser in Python.'
).format(toolname=grako.__toolname__)

try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON = False
else:
    CYTHON = 'bdist_wheel' not in sys.argv

setuptools.setup(
    zip_safe=False,
    name='grako',
    version=grako.__version__,
    url='https://bitbucket.org/neogeny/{package}'.format(
        package=grako.__toolname__.lower(),
    ),
    author='Juancarlo Añez',
    author_email='apalala@gmail.com',
    description=SHORT_DESCRIPTION,
    long_description=io.open('README.rst', encoding='utf-8').read(),
    license='BSD License',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'grako = grako:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Cython',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing :: General'
    ],
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'future-regex': ['regex']
    },
    ext_modules=cythonize(
        "grako/**/*.py",
        exclude=[
            'grako/__main__.py',
            'grako/__init__.py',
            'grako/codegen/__init__.py',
            'grako/test/__main__.py',
            'grako/test/*.py'
        ]
    ) if CYTHON else [],
)
