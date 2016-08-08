# -*- coding: utf-8 -*-
import sys
import io
import setuptools
import grako

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
    url='http://bitbucket.org/apalala/grako',
    author='Juancarlo Añez',
    author_email='apalala@gmail.com',
    description='Grako (for "grammar compiler") takes a grammar'
                ' in a variation of EBNF as input, and outputs a memoizing'
                ' PEG/Packrat parser in Python.',
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
            'grako/__init__.py',
            'grako/codegen/__init__.py',
            'grako/test/__main__.py',
            'grako/test/*.py'
        ]
    ) if CYTHON else [],
)
