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

""" This script parses BigTIFF file header from SerialEM movies. """

from struct import unpack

from .dtypes import bigtiff_tags
from ..config import DEBUG, SCOPE_DICT


def parseTif(fn):
    header_dict = dict()
    with open(fn, 'rb') as fin:
        fin.seek(0)
        header = fin.read(16)
        try:
            byteorder = {b'II': '<', b'MM': '>'}[header[:2]]
        except KeyError:
            raise NotImplemented('Not a TIFF file!')

        version = unpack(byteorder + 'H', header[2:4])[0]  # 43 = BigTIFF
        if version == 42:
            raise NotImplemented('Only BigTIFF files are supported!')

        ifd_offset = unpack(byteorder + 'Q', header[8:16])[0]  # offset to the first IFD
        # find number of tags in the first IFD
        fin.seek(ifd_offset)
        num_tags = unpack(byteorder + 'Q', fin.read(8))[0]
        start = int(ifd_offset) + 8

        for _ in range(1, num_tags+1):
            fin.seek(start)
            tag = fin.read(20)  # every tag takes 20 bytes
            tagnum = unpack(byteorder + 'H', tag[:2])[0]  # IFD tag
            tagname = bigtiff_tags[tagnum][0]
            dtype = unpack(byteorder + 'H', tag[2:4])[0]  # IFD type

            if dtype in [3, 16]:  # SHORT 2-byte uint / LONG8 8-byte uint
                header_dict[tagname] = unpack(byteorder + 'Q', tag[12:20])[0]  # IFD value
            elif dtype == 5:  # RATIONAL 2x 4-byte uint
                header_dict[tagname] = unpack(byteorder + 'L', tag[12:16])[0]
            elif dtype == 2:  # ASCII 8-byte
                count = unpack(byteorder + 'Q', tag[4:12])[0]
                offset = unpack(byteorder + 'Q', tag[12:20])[0]
                header_dict[tagname] = (count, offset)
            elif dtype == 1:  # BYTE 1-byte uint
                header_dict[tagname] = unpack(byteorder + 'B', tag[12:13])[0]
            start += 20

        # parse tags 270=ImageDescription, 306=DateTime && update dict
        for i in ["ImageDescription", "DateTime"]:
            count_desc, offset_desc = header_dict[i]
            fin.seek(offset_desc)
            part = fin.read(count_desc)
            res = unpack(byteorder + '%ds' % count_desc,
                         part[:count_desc+1])[0]
            header_dict[i] = res.decode('utf-8').strip('\x00')

        # count number of IFDs
        c = 0
        next_offset = ifd_offset
        while next_offset != 0:
            fin.seek(next_offset)
            num_tags = int(unpack(byteorder + 'Q', fin.read(8))[0])
            fin.seek(next_offset + num_tags * 20 + 8)
            next_offset = int(unpack(byteorder + 'Q', fin.read(8))[0])
            c += 1
    header_dict["nimg"] = c

    newDict = _standardizeDict(header_dict)

    if DEBUG:
        for k, v in sorted(newDict.items()):
            print("%s = %s" % (k, v))

    return newDict


def _standardizeDict(acqDict):
    """Convert values to expected format. """
    stdDict = {
        'MicroscopeID': "3593",
        'Detector': "EF-CCD",
        'Mode': 'Counting',
        'NumSubFrames': acqDict['nimg'],
        'ExposureTime': 1,
        'Dose': '0',
        'OpticalGroup': 'opticsGroup1',
        'PhasePlateUsed': 'false',
        'MTF': 'None',
        'Voltage': 300,
    }

    print("Warning: tif headers do not contain enough metadata, "
          "so some default values were used.\n")

    desc = acqDict['ImageDescription'].split("\n")
    stdDict['GainReference'] = desc[1].strip()

    if len(desc) == 3:
        stdDict['DefectFile'] = desc[2].strip()

    sr = 1.0
    if acqDict['ImageLength'] in ['7676', '11520']:
        sr = 2.0
        stdDict["Mode"] = 'Super-resolution'

    stdDict['PixelSpacing'] = float(acqDict['XResolution']) / 2.54e+8 / sr
    stdDict['Cs'] = SCOPE_DICT[stdDict['MicroscopeID']][1]

    # convert all to str
    for key in stdDict:
        stdDict[key] = str(stdDict[key])

    return stdDict
