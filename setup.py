#!/usr/bin/env python

from distutils.core import setup

setup(
    name='cloc',
    version='1.0',
    author='Oliver Hulett',
    author_email='oliver.hulett@gmail.com',
    url='https://github.com/oliverhulett/classify_lines_of_code',
    description='Classify Lines Of Code',
    package_dir={'': "src"},
    packages=['cloc'],
    package_data={'cloc': ["cloc/config/*"]},
    entry_points={'console_scripts': ['cloc=cloc.__main__:main']},
    install_requires=[
        'pyyaml',
    ],
)
