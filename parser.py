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

import re
import os
import math
import xml.etree.ElementTree as ET

from config import *


class Parser:
    """ XML / MDOC parser. """
    def __init__(self):
        # set default values
        self.mdPath = METADATA_PATH
        self.prjPath = PROJECT_PATH
        self.software = 'EPU'
        self.user = None, None, None
        self.ptclSizeShort = part_size_short
        self.ptclSizeLong = part_size_long
        self.fn = None
        self.pipeline = 'Relion'

        self.acqDict = dict()
        self.acqDict['Mode'] = 'Linear'
        self.acqDict['NumSubFrames'] = '0'
        self.acqDict['Dose'] = '0'
        self.acqDict['OpticalGroup'] = 'opticsGroup1'
        self.acqDict['PhasePlateUsed'] = 'false'
        self.acqDict['NoCl2D'] = 'false'
        self.acqDict['GainReference'] = 'None'
        self.acqDict['DefectFile'] = 'None'
        self.acqDict['MTF'] = ''
        self.acqDict['User'] = 'Unknown', 0, 0

    def setMdPath(self, path):
        self.mdPath = path

    def getMdPath(self):
        return self.mdPath

    def setPipeline(self, choice):
        self.pipeline = choice

    def getPipeline(self):
        return self.pipeline

    def getPrjPath(self):
        return self.prjPath

    def setPrjPath(self, path):
        self.prjPath = path

    def getUser(self):
        return self.user

    def setUser(self, login, uid, gid):
        self.user = login, uid, gid

    def getSizes(self):
        return self.ptclSizeShort, self.ptclSizeLong

    def setSizes(self, size1, size2):
        self.ptclSizeShort = size1
        self.ptclSizeLong = size2

    def getSoftware(self):
        return self.software

    def setSoftware(self, soft):
        self.software = soft

    def setFn(self, fn):
        self.fn = fn

    def getFn(self):
        return self.fn

    def guessFn(self, prog="EPU"):
        img = None
        regex = PATTERN_XML if prog == "EPU" else PATTERN_MDOC

        if DEBUG:
            print("\nUsing regex: ", regex)

        # check if Images-DicsX exists in the path
        if prog == "EPU":
            check1 = os.path.exists(os.path.join(self.getMdPath(), 'Images-Disc1'))
            check2 = os.path.exists(os.path.join(self.getMdPath(), 'Images-Disc2'))
            if not check1 and not check2:
                return None

        for root, _, files in os.walk(self.getMdPath()):
            for f in files:
                m = re.compile(regex).match(f)
                if m is not None:
                    img = os.path.join(root, f)
                    break
            if img is not None:
                break

        return img

    def parseImgXml(self, fn):
        """ Main XML parser for EPU files. """
        tree = ET.parse(fn)
        root = tree.getroot()
        schema = {'so': '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}',
                  'ar': '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}',
                  'fr': '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}'}

        elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}ExposureTime"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['ExposureTime'] = e.text

        elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}Name"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['Detector'] = e.text

        # get cameraSpecificInput: ElectronCountingEnabled, SuperResolutionFactor etc.
        customDict = dict()
        keys = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Key"
        values = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value"
        for k, v in zip(root.findall(keys.format(**schema)), root.findall(values.format(**schema))):
            customDict[k.text] = v.text

        # check if counting/super-res is enabled
        if customDict['ElectronCountingEnabled'] == 'true':
            sr = customDict['SuperResolutionFactor']  # 1 - counting, 2 - super-res
            self.acqDict['Mode'] = 'Counting' if sr == '1' else 'Super-resolution'

        if self.acqDict['Detector'] == 'EF-CCD':
            elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value/{fr}NumberOffractions"
            for e in root.findall(elem.format(**schema)):
                self.acqDict['NumSubFrames'] = e.text
        else:
            # count number of DoseFractions for Falcon 3
            elem = "./{so}microscopeData/{so}acquisition/{so}camera/{so}CameraSpecificInput/{ar}KeyValueOfstringanyType/{ar}Value/{fr}DoseFractions"
            for e in root.findall(elem.format(**schema)):
                self.acqDict['NumSubFrames'] = len(e)

        elem = "./{so}SpatialScale/{so}pixelSize/{so}x/{so}numericValue"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['PixelSpacing'] = str(float(e.text) * math.pow(10, 10))
            if self.acqDict['Mode'] == 'Super-resolution':
                self.acqDict['PixelSpacing'] /= 2.0

        elem = "./{so}microscopeData/{so}gun/{so}AccelerationVoltage"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['Voltage'] = int(e.text) // 1000

        elem = "./{so}microscopeData/{so}instrument/{so}InstrumentID"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['MicroscopeID'] = e.text
            if e.text in CS_DICT:
                self.acqDict['Cs'] = CS_DICT[e.text][0]

        elem = "./{so}microscopeData/{so}optics/{so}BeamTilt"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['BeamTiltX'] = e[0].text
            self.acqDict['BeamTiltY'] = e[1].text

        elem = "./{so}microscopeData/{so}optics/{so}TemMagnification/{so}NominalMagnification"
        for e in root.findall(elem.format(**schema)):
            self.acqDict['Magnification'] = e.text

        # get customData: Dose, DoseOnCamera, PhasePlateUsed, AppliedDefocus
        customDict = dict()
        keys = "./{so}CustomData/{ar}KeyValueOfstringanyType/{ar}Key"
        values = "./{so}CustomData/{ar}KeyValueOfstringanyType/{ar}Value"
        for k, v in zip(root.findall(keys.format(**schema)), root.findall(values.format(**schema))):
            customDict[k.text] = v.text

        if 'AppliedDefocus' in customDict:
            self.acqDict['AppliedDefocus'] = float(customDict['AppliedDefocus']) * math.pow(10, 6)
        if 'Dose' in customDict:
            self.acqDict['Dose'] = float(customDict['Dose']) / math.pow(10, 20)
        if 'PhasePlateUsed' in customDict:
            self.acqDict['PhasePlateUsed'] = customDict['PhasePlateUsed']
        if 'DoseOnCamera' in customDict:
            self.acqDict['DoseOnCamera'] = customDict['DoseOnCamera']

        # convert all to str
        for key in self.acqDict:
            self.acqDict[key] = str(self.acqDict[key])

    def parseImgMdoc(self, fn):
        """ SerialEM is used only for K2/K3 cameras. """
        self.acqDict['Detector'] = 'EF-CCD'

        with open(fn, 'r') as fname:
            regex = re.compile(REGEX_MDOC_VAR)

            for line in fname:
                match = regex.match(line)
                if match and match.groupdict()['var'] in SERIALEM_PARAMS:
                    key = match.groupdict()['var']
                    self.acqDict[key] = match.groupdict()['value'].strip()

        try:
            # rename a few keys to match EPU
            # T = SerialEM: Acquired on Tecnai Polara D304
            match = re.search("D[0-9]{3,4}", self.acqDict['T'])
            if match:
                value = match.group().replace('D', '')
                self.acqDict['MicroscopeID'] = value
                self.acqDict.pop('T')
                if value in CS_DICT:
                    self.acqDict['Cs'] = str(CS_DICT[value][0])

            self.acqDict['Dose'] = self.acqDict.pop('ExposureDose')
            self.acqDict['AppliedDefocus'] = self.acqDict.pop('TargetDefocus')
            self.acqDict['Mode'] = 'Super-resolution' if self.acqDict['Binning'] == '0.5' else 'Counting'
            self.acqDict['PhasePlateUsed'] = self.acqDict.pop('PhasePlateInserted')
            self.acqDict.pop('Binning')
        except KeyError:
            pass

    def calcDose(self):
        """ Calculate dose rate per unbinned px. """
        dose_per_frame, dose_on_camera = 0, 0
        numFr = int(self.acqDict['NumSubFrames'])
        dose_total = float(self.acqDict['Dose'])  # e/A^2
        exp = float(self.acqDict['ExposureTime'])  # s
        if self.acqDict['Mode'] == 'Super-resolution':
            pix = 2 * float(self.acqDict['PixelSpacing'])  # A
        else:
            pix = float(self.acqDict['PixelSpacing'])  # A

        if numFr and dose_total:
            dose_per_frame = dose_total / numFr  # e/A^2/frame
            if exp and pix:
                dose_on_camera = dose_total * math.pow(pix, 2) / exp  # e/ubpx/s

        self.acqDict['DosePerFrame'] = str(dose_per_frame)
        self.acqDict['DoseOnCamera'] = str(dose_on_camera)

    def calcBox(self):
        """ Calculate box, mask, downsample. """
        minSize = self.acqDict['PtclSizeShort']
        maxSize = self.acqDict['PtclSizeLong']
        ptclSizeAng = max(minSize, maxSize)
        angpix = float(self.acqDict['PixelSpacing'])

        if self.acqDict['Mode'] == 'Super-resolution':
            angpix = angpix * 2

        # use +10% for mask size
        self.acqDict['MaskSize'] = str(math.ceil(1.1 * float(ptclSizeAng) / angpix))
        ptclSizePx = float(ptclSizeAng) / angpix
        # use +20% for box size, make it even
        boxSize = 1.2 * ptclSizePx
        self.acqDict['BoxSize'] = str(math.ceil(boxSize / 2.) * 2)

        # from relion_it.py script
        # Authors: Sjors H.W. Scheres, Takanori Nakane & Colin M. Palmer
        for box in (48, 64, 96, 128, 160, 192, 256, 288, 300, 320,
                    360, 384, 400, 420, 450, 480, 512, 640, 768,
                    896, 1024):
            # Don't go larger than the original box
            if box > boxSize:
                self.acqDict['BoxSizeSmall'] = str(boxSize)
                break
            # If Nyquist freq. is better than 8.5 A, use this
            # downscaled box, otherwise continue to next size up
            small_box_angpix = angpix * boxSize / box
            if small_box_angpix < 4.25:
                self.acqDict['BoxSizeSmall'] = str(box)
                break

    def guessDataDir(self, fnList):
        """ Guess folder name with movies, gain and defects for Krios. """
        # code below may be LMB-specific
        movieDir, gainFn, defFn = 'None', 'None', 'None'
        camera = self.acqDict['Detector']
        scope = CS_DICT[self.acqDict['MicroscopeID']][1]

        # get MTF file
        if camera == 'EF-CCD':
            self.acqDict['MTF'] = MTF_DICT['K3'] if scope == 'Krios3' else MTF_DICT['K2']
        else:
            if self.acqDict['Mode'] == 'Linear':
                self.acqDict['MTF'] = MTF_DICT['Falcon3-linear']
            else:
                self.acqDict['MTF'] = MTF_DICT['Falcon3-count']

        if self.getSoftware() == 'EPU':
            p1 = MOVIE_PATH_DICT[camera] % scope
            session = os.path.basename(self.getMdPath())

            if camera == 'EF-CCD':
                # get gain file
                movieDir = os.path.join(p1, "DoseFractions", session, EPU_MOVIES_PATH)
                # TODO: check if gain is always named this way
                f1 = fnList.replace('.xml', '-gain-ref.MRC')
                f2 = f1.split('Images-Disc')[1]
                gainFn = os.path.join(p1, "DoseFractions", session, "Images-Disc" + f2)
            else:
                movieDir = os.path.join(p1, session, EPU_MOVIES_PATH)

        else:  # SerialEM
            movieDir = os.path.join(self.getMdPath(), "*.tif")
            gainFn = os.path.join(self.getMdPath(), self.acqDict['GainReference'])
            if 'DefectFile' in self.acqDict:
                defFn = os.path.join(self.getMdPath(), self.acqDict['DefectFile'])

        # populate dict
        self.acqDict['Software'] = self.getSoftware()
        self.acqDict['PrjPath'] = self.getPrjPath()
        self.acqDict['MoviePath'] = movieDir
        if os.path.exists(gainFn):
            self.acqDict['GainReference'] = gainFn
        if os.path.exists(defFn):
            self.acqDict['DefectFile'] = defFn
