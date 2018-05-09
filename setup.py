#!/usr/bin/env python

import os
from distutils.core import setup


def get_package_data_files():
    files = []
    pkgdir = os.path.join(os.path.dirname(__file__), "src", "cloc")
    for root, _, filenames in os.walk(os.path.join(pkgdir, "config")):
        for f in filenames:
            files.append(os.path.join(root[len(pkgdir) + 1:], f))  # plus 1 for the slash
    return files


print get_package_data_files()

setup(
    name='cloc',
    version='1.0',
    author='Oliver Hulett',
    author_email='oliver.hulett@gmail.com',
    url='https://github.com/oliverhulett/classify_lines_of_code',
    description='Classify Lines Of Code',
    package_dir={'': "src"},
    packages=['cloc'],
    package_data={'cloc': get_package_data_files()},
    entry_points={'console_scripts': ['cloc=cloc.__main__:main']},
    install_requires=[
        'pyyaml',
    ],
)
