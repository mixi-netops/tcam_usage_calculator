import io
import os
from setuptools import find_packages, setup

# Package meta-data.
NAME = 'tcam_usage_calculator'
DESCRIPTION = 'Predict TCAM usage of router.'
URL = 'https://github.com/xflagstudio/tcam_usage_calculator'
EMAIL = 'hiroki.ito@mixi.co.jp'
AUTHOR = 'hekki'
REQUIRED = []

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': [
            'tcam_usage_calculator=tcam_usage_calculator.main:main'
            ],
    },
    install_requires=REQUIRED,
    python_requires='>=3.6',
    license='MIT'
)
