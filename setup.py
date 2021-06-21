# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk) [1]
# *
# * [1] MRC Laboratory of Molecular Biology, MRC-LMB
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'gsharov@mrc-lmb.cam.ac.uk'
# *
# **************************************************************************

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from mdcatch import __version__

here = path.abspath(path.dirname(__file__))

setup(
    name='MDCatch',
    version=__version__,
    description='Fetch metadata from EPU / SerialEM and launch on-the-fly pre-processing',
    long_description='See https://github.com/azazellochg/MDCatch for more details',
    url='https://github.com/azazellochg/MDCatch',
    author='Grigory Sharov',
    author_email='gsharov@mrc-lmb.cam.ac.uk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3'
    ],
    keywords='cryo-em python qt5 epu serialem',
    packages=find_packages(),
    install_requires=['pyqt5', 'watchdog', 'mrcfile', 'tifffile', 'emtable'],
    entry_points={'console_scripts': ['mdcatch=mdcatch.run:main']},
    project_urls={
        'Bug Reports': 'https://github.com/azazellochg/MDCatch/issues',
        'Source': 'https://github.com/azazellochg/MDCatch',
    },
)
