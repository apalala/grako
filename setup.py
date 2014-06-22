# -*- coding: utf-8 -*-
from setuptools import setup

try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON = False
else:
    CYTHON = True

setup(
    name='grako',
    version='3.0.1',
    author='Juancarlo Añez',
    author_email='apalala@gmail.com',
    packages=['grako', 'grako.test'],
    scripts=['scripts/grako'],
    url='http://bitbucket.org/apalala/grako',
    license='BSD License',
    description='A generator of PEG/Packrat parsers from EBNF grammars.',
    long_description=open('README.rst').read(),
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
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing :: General'
    ],
    ext_modules=cythonize(
        "grako/**/*.py",
        exclude=[
            'grako/__main__.py',
            'grako/test/__main__.py',
            'grako/test/*.py'
        ]
    ) if CYTHON else [],
)
