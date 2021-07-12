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

""" This script parses MRC 2014 FEI1/FEI2 file header. """

import mrcfile
import math

from ..config import DEBUG, SCOPE_DICT


def parseMrc(fn):
    acqDict = {}
    with mrcfile.open(fn, header_only=True) as mrc:
        main = mrc.header
        ext = mrc.extended_header

    for item in main.dtype.names:
        acqDict[item] = main[item]

    if len(ext):
        for item in ext.dtype.names:
            acqDict[item] = ext[item][0]

    newDict = _standardizeDict(acqDict)

    if DEBUG:
        for k, v in sorted(acqDict.items()):
            print("%s = %s" % (k, v))
        print(40 * "=")
        for k, v in sorted(newDict.items()):
            print("%s = %s" % (k, v))

    return newDict


def _standardizeDict(acqDict):
    """Convert values to expected format. """
    stdDict = {
        'AppliedDefocus': float(acqDict['Applied defocus']) * math.pow(10, 6),
        'BeamShiftX': acqDict['Shift X'],  # TEM beam-image shift
        'BeamShiftY': acqDict['Shift Y'],
        'ImageShiftX': acqDict['Shift offset X'],  # TEM pure image shift
        'ImageShiftY': acqDict['Shift offset Y'],
        'BeamSize': float(acqDict['Illuminated area']) * math.pow(10, 6),
        'Detector': acqDict['Camera name'].decode("utf-8"),
        'Dose': float(acqDict['Dose']) * math.pow(10, -20),
        'EPUversion': acqDict['Application version'].decode("utf-8"),
        'ExposureTime': acqDict['Integration time'],
        'Magnification': acqDict['Magnification'],
        'MicroscopeID': acqDict['D-Number'].decode("utf-8"),
        # no way to find super-res?
        'Mode': 'Counting' if bool(acqDict['Direct detector electron counting']) else 'Linear',
        # no way to find frames number?
        'NumSubFrames': 0,
        'SpotSize': acqDict['Spot index'],
        'Voltage': float(acqDict['HT']) // 1000,
        'PhasePlateUsed': bool(acqDict['Phase Plate']),
        'Warning': 'MRC header does not contain frame number, please check the fluence!'
    }

    sr = 1
    stdDict['PixelSpacing'] = float(acqDict['Pixel size X']) * math.pow(10, 10) / sr

    if stdDict['MicroscopeID'] in SCOPE_DICT:
        stdDict['Cs'] = SCOPE_DICT[stdDict['MicroscopeID']][1]

    if 'Phase plate position index' in acqDict:
        stdDict['PhasePlatePosition'] = acqDict['Phase plate position index']

    # convert all to str
    for key in stdDict:
        stdDict[key] = str(stdDict[key])

    return stdDict
