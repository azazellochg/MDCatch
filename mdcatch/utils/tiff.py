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

""" This script parses TIFF file header. """

from tifffile import TiffFile

from ..config import DEBUG, SCOPE_DICT


# See https://www.awaresystems.be/imaging/tiff/tifftags/baseline.html

tif_tags = {
    # IFD tag code: name
    256: "ImageWidth",  # nx
    257: "ImageLength",  # ny
    258: "BitsPerSample",  # data type
    259: "Compression",  # 5=LZW, 65000=EER compressed data 8-bit, 65001=EER compressed data 7-bit
    262: "PhotometricInterpretation",  # The color space of the image data.
    270: "ImageDescription",
    273: "StripOffsets",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    279: "StripByteCounts",
    282: "XResolution",  # The number of pixels per ResolutionUnit in the ImageWidth direction.
    283: "YResolution",  # The number of pixels per ResolutionUnit in the ImageLength direction.
    284: "PlanarConfiguration",
    296: "ResolutionUnit",  # The unit of measurement for XResolution and YResolution. 2=inch, 3=cm.
    306: "DateTime",  # YYYY:MM:DD HH:MM:SS
    339: "SampleFormat",
    340: "MinSampleValue",  # min
    341: "MaxSampleValue",  # max
    65001: "TFS EER Metadata",  # Movie metadata,
    65100: "TFS EER gain Metadata",  # Camera defects
}


def parseTif(fn):
    acqDict = {"ImageDescription": "None\n",
               "DateTime": "None",
               "XResolution": (1, 1),
               "ResolutionUnit": 1,
               "ExposureTime": 1.0
               }

    with TiffFile(fn) as tif:
        for page in tif.pages:
            for tag in page.tags:
                acqDict[tif_tags[tag.code]] = tag.value
                # print(tag.code, tag.dtype)
            break

        acqDict["nimg"] = len(tif.pages)

    if 'TFS EER Metadata' in acqDict:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(acqDict["TFS EER Metadata"].decode('utf-8'))
        tmp = {}
        for item in root:
            tmp[item.get('name')] = item.text

        acqDict['ExposureTime'] = float(tmp['exposureTime'])
        acqDict['Dose_e/px'] = float(tmp['totalDose'])

    newDict = _standardizeDict(acqDict)

    if DEBUG:
        for k, v in sorted(acqDict.items()):
            if k != "StripByteCounts" and k != "StripOffsets":
                print("%s = %s" % (k, v))
        print(40 * "=")
        for k, v in sorted(newDict.items()):
            print("%s = %s" % (k, v))

    return newDict


def _standardizeDict(acqDict):
    """Convert values to expected format. """
    stdDict = {
        'MicroscopeID': "3593",
        'Detector': 'EF-CCD',
        'Mode': 'Counting',
        'NumSubFrames': acqDict['nimg'],
        'ExposureTime': acqDict['ExposureTime'],
        'Dose': 0,
        'OpticalGroup': 'opticsGroup1',
        'PhasePlateUsed': 'false',
        'MTF': 'None',
        'Voltage': 300,
        'Binning': 1,
        'Warning': 'TIF header does not contain enough metadata, please check these values!'
    }

    desc = acqDict['ImageDescription'].split("\n")
    stdDict['GainReferenceTransform'] = desc[0].split("r/f")[-1]
    stdDict['GainReference'] = desc[1].strip() or None

    if len(desc) == 3:
        stdDict['DefectFile'] = desc[2].strip()

    # find mode/detector from image size
    sr = 1.0
    if acqDict['ImageLength'] in [7676, 11520]:
        sr = 2.0
        stdDict['Mode'] = 'Super-resolution'
    elif acqDict['ImageLength'] == acqDict['ImageWidth'] == 4096:
        stdDict['Detector'] = 'BM-Falcon'

    # find pixel size A/px
    if acqDict['ResolutionUnit'] == 1:  # unknown
        stdDict['PixelSpacing'] = 1.0
    elif acqDict['ResolutionUnit'] == 2:  # inch
        stdDict['PixelSpacing'] = float(acqDict['XResolution'][0]) / 2.54e+8 / sr
    else:  # cm
        stdDict['PixelSpacing'] = float(acqDict['XResolution'][0]) / 1e+8 / sr

    if 'Dose_e/px' in acqDict:
        stdDict['Dose'] = acqDict['Dose_e/px'] / (stdDict['PixelSpacing']) ** 2  # e/A^2

    stdDict['Cs'] = SCOPE_DICT[stdDict['MicroscopeID']][1]

    # convert all to str
    for key in stdDict:
        stdDict[key] = str(stdDict[key])

    return stdDict
