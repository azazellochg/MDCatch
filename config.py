#!/usr/bin/env python3

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

# Config vars and dicts

DEBUG = 1

#default_path = "/home/azazello/MEGA/application/acquisition_patterns"
default_path = "/home/gsharov/soft/application/acquisition_patterns"
#default_path = "/net/em-support3/Krios1/Gregory"
movies_path = 'Images-Disc*/GridSquare_*/Data/FoilHole_*.mrc'
reg_xml = 'FoilHole_[0-9]{7,8}_Data_[0-9]{7,8}_[0-9]{7,8}_[0-9]{8}_[0-9]{4,6}.xml'
reg_mdoc = "frames.mdoc"
mdocPattern = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

# scopeID: Cs aberration and scope name
cs_dict = {
    '3299': (2.7, 'Krios1'),
    '3413': (2.7, 'Krios2'),
    '3593': (2.7, 'Krios3'),
    '316': (2.25, 'Polara1'),
    '304': (2.25, 'Polara2'),
    '2366': (2.0, 'F20')
}

# path to raw movies folder on Krios
kriosDict = {
    'EF-CCD': '/net/cista1/%sGatan/',
    'BM-Falcon': '/net/cista1/%sFalcon/'
}

# SerialEM mdoc params to parse
paramsList = [
    'T',  # Microscope ID
    #'TiltAngle',
    'Voltage',
    'Magnification',
    'ExposureDose',
    'PixelSpacing',
    'ExposureTime',
    'Binning',
    'TargetDefocus',
    'NumSubFrames',
    #'DateTime',
    'DefectFile',
    'GainReference'
]
