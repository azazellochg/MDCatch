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

""" This script parses MRC 2014 FEI1 file header. """

import numpy as np
import math
from struct import unpack

from .dtypes import mrc_tags, fei_tags
from ..config import DEBUG, SCOPE_DICT


def parseMrc(fn):
    with open(fn, 'rb') as fin:
        fin.seek(0)
        header = fin.read(1024)
        map = header[208:212]
        machst = header[212:214]
        exttyp = header[104:108]

        if map != b'MAP ' or machst != b'DD':  # 0x44 0x44 is little endian
            print("Not a MRC file or not little endian byte order!")
            return None
        if exttyp != b'FEI1':
            print("No FEI1 extended header found!")
            return None

        fin.seek(1024)
        md_size = unpack('<L', fin.read(4))[0]
        fin.seek(1024)
        ext_header = fin.read(md_size)

    # parse main header
    header_arr = np.frombuffer(header[:52], dtype=mrc_tags)
    keys = header_arr.dtype.names
    header_dict = [dict(zip(keys, value)) for value in header_arr][0]

    header_dict["apix_x"] = header_dict["CELLA"]["X"] / header_dict["NX"]
    header_dict["apix_y"] = header_dict["CELLA"]["Y"] / header_dict["NY"]

    # parse extended header
    ext_header_arr = np.frombuffer(ext_header, dtype=fei_tags)
    keys = ext_header_arr.dtype.names
    ext_header_dict = [dict(zip(keys, value)) for value in ext_header_arr][0]

    acqDict = {**header_dict, **ext_header_dict}
    newDict = _standardizeDict(acqDict)

    if DEBUG:
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
    }

    sr = 1
    stdDict['PixelSpacing'] = float(acqDict['Pixel size X']) * math.pow(10, 10) / sr

    if stdDict['MicroscopeID'] in SCOPE_DICT:
        stdDict['Cs'] = SCOPE_DICT[stdDict['MicroscopeID']][1]

    # convert all to str
    for key in stdDict:
        stdDict[key] = str(stdDict[key])

    return stdDict
