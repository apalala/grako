# -*- coding: utf-8 -*-
import setuptools
import grako

try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON = False
else:
    CYTHON = True

setuptools.setup(
    zip_safe=True,
    name='grako',
    version=grako.__version__,
    url='http://bitbucket.org/apalala/grako',
    author='Juancarlo Añez',
    author_email='apalala@gmail.com',
    description='A generator of PEG/Packrat parsers from EBNF grammars.',
    long_description=open('README.rst').read(),
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
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing :: General'
    ],
    extras_require={
        'future-regex': ['regex']
    },
    ext_modules=cythonize(
        "grako/**/*.py",
        exclude=[
            'grako/__main__.py',
            'grako/test/__main__.py',
            'grako/test/*.py'
        ]
    ) if CYTHON else [],
)
