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

""" This script parses FEI EPU xml file. """

import math
import xml.etree.ElementTree as ET

from ..config import DEBUG, SCOPE_DICT


def parseXml(fn):
    acqDict = dict()
    tree = ET.parse(fn)
    root = tree.getroot()
    nspace = {'so': '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}',
              'ar': '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}',
              'fr': '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}',
              'tp': '{http://schemas.datacontract.org/2004/07/Fei.Types}',
              'dr': '{http://schemas.datacontract.org/2004/07/System.Drawing}'}

    items = {'ExposureTime': "./{so}microscopeData/{so}acquisition/{so}camera/{so}ExposureTime",
             'Detector': "./{so}microscopeData/{so}acquisition/{so}camera/{so}Name",
             'GunLens': "./{so}microscopeData/{so}gun/{so}GunLens",
             'SpotSize': "./{so}microscopeData/{so}optics/{so}SpotIndex",
             'ProbeMode': "./{so}microscopeData/{so}optics/{so}ProbeMode",
             'Magnification': "./{so}microscopeData/{so}optics/{so}TemMagnification/{so}NominalMagnification",
             'BeamSize': "./{so}microscopeData/{so}optics/{so}BeamDiameter",
             'Voltage': "./{so}microscopeData/{so}gun/{so}AccelerationVoltage",
             'ExtractorVoltage': "./{so}microscopeData/{so}gun/{so}ExtractorVoltage",
             'MicroscopeID': "./{so}microscopeData/{so}instrument/{so}InstrumentID",
             'PixelSpacing': "./{so}SpatialScale/{so}pixelSize/{so}x/{so}numericValue",
             'EnergySelectionSlitWidth': "./{so}microscopeData/{so}optics/{so}EnergyFilter/{so}EnergySelectionSlitWidth",
             'Binning': "./{so}microscopeData/{so}acquisition/{so}camera/{so}Binning/{dr}x",
             'EPUversion': "./{so}microscopeData/{so}core/{so}ApplicationSoftwareVersion",
             'BeamTiltX': "./{so}microscopeData/{so}optics/{so}BeamTilt/{tp}_x",
             'BeamTiltY': "./{so}microscopeData/{so}optics/{so}BeamTilt/{tp}_y",
             'BeamShiftX': "./{so}microscopeData/{so}optics/{so}BeamShift/{tp}_x",
             'BeamShiftY': "./{so}microscopeData/{so}optics/{so}BeamShift/{tp}_y",
             'ImageShiftX': "./{so}microscopeData/{so}optics/{so}ImageShift/{tp}_x",
             'ImageShiftY': "./{so}microscopeData/{so}optics/{so}ImageShift/{tp}_y",
             }

    for key in items:
        try:
            acqDict[key] = root.find(items[key].format(**nspace)).text
        except:
            pass

    if acqDict['MicroscopeID'] in SCOPE_DICT:
        acqDict['Cs'] = SCOPE_DICT[acqDict['MicroscopeID']][1]

    acqDict['BeamSize'] = float(acqDict['BeamSize']) * math.pow(10, 6)
    acqDict['Voltage'] = int(acqDict['Voltage']) // 1000
    acqDict['Binning'] = int(acqDict['Binning'])

    # get cameraSpecificInput: ElectronCountingEnabled, SuperResolutionFactor etc.
    customDict = dict()
    keys = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Key"
    values = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value"
    for k, v in zip(root.findall(keys.format(**nspace)), root.findall(values.format(**nspace))):
        customDict[k.text] = v.text

    # check if counting/super-res is enabled
    sr = 1.0
    acqDict['Mode'] = 'Linear'
    if customDict['ElectronCountingEnabled'] == 'true':
        sr = float(customDict['SuperResolutionFactor'])  # 1 - counting, 2 - super-res
        acqDict['Mode'] = 'Counting' if sr == 1.0 else 'Super-resolution'

    # EPU's pixel size refers to a physical pixel, which is already multiplied by Binning factor
    acqDict['PixelSpacing'] = float(acqDict['PixelSpacing']) * math.pow(10, 10) / sr

    if acqDict['Detector'] == 'EF-CCD':
        elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value/{fr}NumberOffractions"
        acqDict['NumSubFrames'] = root.find(elem.format(**nspace)).text
    else:
        # count number of DoseFractions for Falcon 3
        elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value/{fr}DoseFractions"
        try:
            acqDict['NumSubFrames'] = len(root.find(elem.format(**nspace)))
        except:
            pass

    # get customData: Dose, DoseOnCamera, PhasePlateUsed, AppliedDefocus
    customDict = dict()
    keys = "./{so}CustomData/{ar}KeyValueOfstringanyType/{ar}Key"
    values = "./{so}CustomData/{ar}KeyValueOfstringanyType/{ar}Value"
    for k, v in zip(root.findall(keys.format(**nspace)), root.findall(values.format(**nspace))):
        customDict[k.text] = v.text

    if 'Detectors[BM-Falcon].EerGainReference' in customDict:
        acqDict['NumSubFrames'] = int(float(acqDict['ExposureTime']) * 248)
        acqDict['Mode'] = "EER"
    if 'AppliedDefocus' in customDict:
        acqDict['AppliedDefocus'] = float(customDict['AppliedDefocus']) * math.pow(10, 6)
    if 'Dose' in customDict:
        acqDict['Dose'] = float(customDict['Dose']) * math.pow(10, -20)
    if 'PhasePlateUsed' in customDict:
        acqDict['PhasePlateUsed'] = customDict['PhasePlateUsed']
    if 'Aperture[C2].Name' in customDict:
        acqDict['C2Aperture'] = customDict['Aperture[C2].Name']
    if 'Aperture[OBJ].Name' in customDict:
        acqDict['ObjAperture'] = customDict['Aperture[OBJ].Name']

        if customDict['PhasePlateUsed'] == 'true':
            acqDict['PhasePlateNumber'] = customDict['PhasePlateApertureName'].split(" ")[-1]
            acqDict['PhasePlatePosition'] = customDict['PhasePlatePosition']

    if DEBUG:
        for k, v in sorted(acqDict.items()):
            print("%s = %s" % (k, v))

    # convert all to str
    for key in acqDict:
        acqDict[key] = str(acqDict[key])

    return acqDict
