#!/usr/bin/env python

from distutils.core import setup

setup(
    name='cloc',
    version='1.0',
    description='Classify Lines Of Code',
    author='Oliver Hulett',
    author_email='oliver.hulett@gmail.com',
    url='https://github.com/oliverhulett/classify_lines_of_code',
    package_dir={'': "src"},
    packages=['cloc'],
    package_data={'cloc': ["cloc/*.yml"]},
)
