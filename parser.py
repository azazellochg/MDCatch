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
import xml.etree.cElementTree as ET

from config import *


class Parser:
    """ XML / MDOC parser """
    def __init__(self):
        self.path = None
        self.software = None
        self.ptclSize = None
        self.fn = None
        self.acqDict = dict()

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path

    def getSize(self):
        return self.ptclSize

    def setSize(self, size):
        self.ptclSize = size

    def getSoftware(self):
        return self.software

    def setSoftware(self, soft):
        self.software = soft

    def setFn(self, fn):
        self.fn = fn

    def getFn(self):
        return self.fn

    def guessFn(self, ftype="xml"):
        img = None
        regex = reg_xml if ftype == 'xml' else reg_mdoc

        if DEBUG:
            print("\nUsing regex: ", regex)

        for root, _, files in os.walk(self.getPath()):
            for f in files:
                m = re.compile(regex).match(f)
                if m is not None:
                    img = os.path.join(root, f)
                    break
            if img is not None:
                break

        return img

    def parseImgXml(self, fn):
        tree = ET.parse(fn)
        root = tree.getroot()
        # default values
        self.acqDict['Mode'] = 'Linear'
        self.acqDict['NumSubFrames'] = '0'
        self.acqDict['Dose'] = '0'

        if root[6][0][2][4].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ExposureTime':
            self.acqDict['ExposureTime'] = root[6][0][2][4].text

        if root[6][0][2][6].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Name':
            self.acqDict['Detector'] = root[6][0][2][6].text

        if self.acqDict['Detector'] == 'EF-CCD' and root[6][0][2][2][3][0].text == 'FractionationSettings':
            self.acqDict['NumSubFrames'] = root[6][0][2][2][3][1][0].text

            # check if counting is enabled, check if super-res is enabled
            if root[6][0][2][2][0][0].text == 'ElectronCountingEnabled':
                if root[6][0][2][2][0][1].text == 'true':
                    if root[6][0][2][2][2][0].text == 'SuperResolutionFactor':
                        sr = root[6][0][2][2][2][1].text  # 1 - counting, 2 - super-res
                        self.acqDict['Mode'] = 'Counting' if sr == '1' else 'Super-resolution'

        else:
            # count number of b:DoseFractionDefinition occurrences for Falcon 3
            if len(list(root[6][0][2][2])) > 2:
                if root[6][0][2][2][5][0].text == 'FractionationSettings':
                    self.acqDict['NumSubFrames'] = len(list(root[6][0][2][2][5][1][0]))
                elif root[6][0][2][2][3][0].text == 'FractionationSettings':
                    self.acqDict['NumSubFrames'] = len(list(root[6][0][2][2][3][1][0]))
                # check if counting is enabled
                if root[6][0][2][2][2][0].text == 'ElectronCountingEnabled' or \
                        root[6][0][2][2][0][0].text == 'ElectronCountingEnabled':
                    if root[6][0][2][2][2][1].text == 'true' or \
                            root[6][0][2][2][0][1].text == 'true':
                        self.acqDict['Mode'] = 'Counting'

        if root[5][1].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}pixelSize':
            self.acqDict['PixelSpacing'] = float(root[5][1][0][0].text) * math.pow(10, 10)
            if self.acqDict['Mode'] == 'Super-resolution':
                self.acqDict['PixelSpacing'] /= 2.0

        if root[6][2][0].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage':
            self.acqDict['Voltage'] = int(root[6][2][0].text) / 1000

        if root[6][3][3].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID':
            self.acqDict['MicroscopeID'] = root[6][3][3].text

            value = self.acqDict['MicroscopeID']
            if value in cs_dict:
                self.acqDict['Cs'] = cs_dict[value][0]

        if root[6][4][3].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamTilt':
            self.acqDict['BeamTiltX'] = root[6][4][3][0].text
            self.acqDict['BeamTiltY'] = root[6][4][3][1].text

        if root[6][4][28][0].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}NominalMagnification':
            self.acqDict['Magnification'] = root[6][4][28][0].text

        # get customData: Dose, DoseOnCamera, PhasePlateUsed, AppliedDefocus etc.
        if root[2].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}CustomData':
            i = 0
            while i < 8:
                try:
                    self.acqDict[root[2][i][0].text] = root[2][i][1].text
                    i += 1
                except IndexError:
                    break

        if 'BinaryResult.Detector' in self.acqDict:
            self.acqDict.pop('BinaryResult.Detector')
        if 'AppliedDefocus' in self.acqDict:
            self.acqDict['AppliedDefocus'] = float(self.acqDict['AppliedDefocus']) * math.pow(10, 6)
        if 'Dose' in self.acqDict:
            self.acqDict['Dose'] = float(self.acqDict['Dose']) / math.pow(10, 20)

        # convert all to str
        for key in self.acqDict:
            self.acqDict[key] = str(self.acqDict[key])

    def parseImgMdoc(self, fn):
        # set default values
        self.acqDict['PhasePlateUsed'] = 'false'
        self.acqDict['Detector'] = 'EF-CCD'

        with open(fn, 'r') as fname:
            regex = re.compile(mdocPattern)

            for line in fname:
                match = regex.match(line)
                if match and match.groupdict()['var'] in paramsList:
                    key = match.groupdict()['var']
                    self.acqDict[key] = match.groupdict()['value'].strip()

        try:
            # rename a few keys to match EPU
            match = re.search("D[0-9]{3,4}", self.acqDict['T'])
            if match:
                value = match.group().replace('D', '')
                self.acqDict['MicroscopeID'] = value
                self.acqDict.pop('T')
                if value in cs_dict:
                    self.acqDict['Cs'] = str(cs_dict[value][0])

            self.acqDict['Dose'] = self.acqDict.pop('ExposureDose')
            self.acqDict['AppliedDefocus'] = self.acqDict.pop('TargetDefocus')
            self.acqDict['Voltage'] = self.acqDict['Voltage']
            self.acqDict['PixelSpacing'] = self.acqDict['PixelSpacing']
            self.acqDict['Mode'] = 'Super-resolution' if self.acqDict['Binning'] == '0.5' else 'Counting'
            self.acqDict.pop('Binning')
        except KeyError:
            pass

    def calcDose(self):
        # calculate dose
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

    def guessDataDir(self, fnList):
        # guess folder name with movies on cista1, gain and defects for Krios
        movieDir, gainFn, defFn = 'None', 'None', 'None'

        if self.getSoftware() == 'EPU':
            scope = cs_dict[self.acqDict['MicroscopeID']][1]
            camera = self.acqDict['Detector']

            if 'Krios' in scope:
                p1 = pathDict[camera] % scope
                session = os.path.basename(self.getPath())

                if camera == 'EF-CCD':
                    # get gain file
                    movieDir = os.path.join(p1, "DoseFractions", session, movies_path)
                    f1 = fnList.replace('.xml', '-gain-ref.MRC')
                    f2 = f1.split('Images-Disc')[1]
                    gainFn = os.path.join(p1, "DoseFractions", session, "Images-Disc" + f2)
                else:
                    movieDir = os.path.join(p1, session, movies_path)

            elif 'Polara1' in scope:
                movieDir = pathDict[scope]

        else:  # SerialEM
            movieDir = os.path.join(self.getPath(), "*.tif")
            gainFn = os.path.join(self.getPath(), self.acqDict['GainReference'])
            defFn = os.path.join(self.getPath(), self.acqDict['DefectFile'])

        # populate dict
        self.acqDict['MoviePath'] = movieDir
        self.acqDict['GainReference'] = gainFn
        self.acqDict['DefectFile'] = defFn
