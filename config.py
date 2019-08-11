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

default_path = "/home/azazello/MEGA/application/acquisition_patterns"
#default_path = "/home/soft/gsharov/application/acquisition_patterns"
#default_path = "/net/em-support3"
#reg_xml = 'Images-Disc[0-9]{1}/GridSquare_[0-9]{7}/Data/FoilHole_[0-9]{7}_Data_[0-9]{7}_[0-9]{7}_[0-9]{8}_[0-9]{4,6}.xml'
#reg_xml = 'FoilHole_[0-9]{7,8}_Data_[0-9]{7,8}_[0-9]{7,8}_[0-9]{8}_[0-9]{4,6}.xml'
#reg_xml = 'k2.xml'
#reg_xml = 'f3.xml'
#reg_xml = 'FoilHole_1711113_Data_1709829_1709831_20190803_000431.xml'
#reg_xml = 'FoilHole_30456232_Data_30455071_30455072_20190530_1902.xml'
reg_xml = "FoilHole_11636390_Data_11626959_11626960_20190314_0619.xml"
reg_xml2 = "acquisition_patterns/EpuSession.dm"
#reg_xml2 = 'EpuSession-F3.xml'
#reg_xml2 = 'EpuSession-K2.xml'
reg_mdoc = "frames.mdoc"
mdocPattern = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

cs_dict = {
    '3299': 2.7,  # Krios 1
    '3413': 2.7,  # Krios 2
    '3593': 2.7,  # Krios 3
    '316': 2.25,  # Polara 1
    '304': 2.25,  # Polara 2
    '2366': 2.0  # F20
}

# SerialEM mdoc params
paramsList = [
    'T',
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
