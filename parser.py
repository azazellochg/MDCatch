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
        self.rawPath = default_path
        self.prjPath = os.getcwd()
        self.software = 'EPU'
        self.ptclSizeShort = part_size_short
        self.ptclSizeLong = part_size_long
        self.fn = None
        self.pipeline = 'Relion'
        self.acqDict = dict()
        # set default values
        self.acqDict['Mode'] = 'Linear'
        self.acqDict['NumSubFrames'] = '0'
        self.acqDict['Dose'] = '0'
        self.acqDict['OpticalGroup'] = 'opticsGroup1'
        self.acqDict['PhasePlateUsed'] = 'false'
        self.acqDict['NoCl2D'] = 'false'

    def setRawPath(self, path):
        self.rawPath = path

    def getRawPath(self):
        return self.rawPath

    def setPipeline(self, choice):
        self.pipeline = choice

    def getPipeline(self):
        return self.pipeline

    def getPrjPath(self):
        return self.prjPath

    def setPrjPath(self, path):
        self.prjPath = path

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

    def guessFn(self, ftype="xml"):
        img = None
        regex = reg_xml if ftype == 'xml' else reg_mdoc

        if DEBUG:
            print("\nUsing regex: ", regex)

        # check if Images-DicsX exists in the path
        if ftype == 'xml':
            check1 = os.path.exists(os.path.join(self.getRawPath(), 'Images-Disc1'))
            check2 = os.path.exists(os.path.join(self.getRawPath(), 'Images-Disc2'))
            if not check1 and not check2:
                return None

        for root, _, files in os.walk(self.getRawPath()):
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
        # schema depends on EPU version
        schema = '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}'

        if root[6][0][2][4].tag == '%sExposureTime' % schema:
            self.acqDict['ExposureTime'] = root[6][0][2][4].text

        if root[6][0][2][6].tag == '%sName' % schema:
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
                    self.acqDict['NumSubFrames'] = str(len(list(root[6][0][2][2][5][1][0])))
                elif root[6][0][2][2][3][0].text == 'FractionationSettings':
                    self.acqDict['NumSubFrames'] = str(len(list(root[6][0][2][2][3][1][0])))
                # check if counting is enabled
                if root[6][0][2][2][2][0].text == 'ElectronCountingEnabled' or \
                        root[6][0][2][2][0][0].text == 'ElectronCountingEnabled':
                    if root[6][0][2][2][2][1].text == 'true' or \
                            root[6][0][2][2][0][1].text == 'true':
                        self.acqDict['Mode'] = 'Counting'

        if root[5][1].tag == '%spixelSize' % schema:
            self.acqDict['PixelSpacing'] = str(float(root[5][1][0][0].text) * math.pow(10, 10))
            if self.acqDict['Mode'] == 'Super-resolution':
                self.acqDict['PixelSpacing'] /= 2.0

        if root[6][2][0].tag == '%sAccelerationVoltage' % schema:
            self.acqDict['Voltage'] = str(int(root[6][2][0].text) / 1000)

        if root[6][3][3].tag == '%sInstrumentID' % schema:
            self.acqDict['MicroscopeID'] = root[6][3][3].text

            value = self.acqDict['MicroscopeID']
            if value in cs_dict:
                self.acqDict['Cs'] = cs_dict[value][0]

        if root[6][4][3].tag == '%sBeamTilt' % schema:
            self.acqDict['BeamTiltX'] = root[6][4][3][0].text
            self.acqDict['BeamTiltY'] = root[6][4][3][1].text

        if root[6][4][28][0].tag == '%sNominalMagnification' % schema:
            self.acqDict['Magnification'] = root[6][4][28][0].text

        # get customData: Dose, DoseOnCamera, PhasePlateUsed, AppliedDefocus etc.
        if root[2].tag == '%sCustomData' % schema:
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
            self.acqDict['AppliedDefocus'] = str(float(self.acqDict['AppliedDefocus']) * math.pow(10, 6))
        if 'Dose' in self.acqDict:
            self.acqDict['Dose'] = str(float(self.acqDict['Dose']) / math.pow(10, 20))

        # convert all to str
        for key in self.acqDict:
            self.acqDict[key] = str(self.acqDict[key])

    def parseImgMdoc(self, fn):
        # SerialEM is used only for K2/K3 cameras
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
            # T = SerialEM: Acquired on Tecnai Polara D304
            match = re.search("D[0-9]{3,4}", self.acqDict['T'])
            if match:
                value = match.group().replace('D', '')
                self.acqDict['MicroscopeID'] = value
                self.acqDict.pop('T')
                if value in cs_dict:
                    self.acqDict['Cs'] = str(cs_dict[value][0])

            self.acqDict['Dose'] = self.acqDict.pop('ExposureDose')
            self.acqDict['AppliedDefocus'] = self.acqDict.pop('TargetDefocus')
            self.acqDict['Mode'] = 'Super-resolution' if self.acqDict['Binning'] == '0.5' else 'Counting'
            self.acqDict['PhasePlateUsed'] = self.acqDict.pop('PhasePlateInserted')
            self.acqDict.pop('Binning')
        except KeyError:
            pass

    def calcDose(self):
        # calculate dose rate per unbinned px
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
        # calculate box, mask, downsample
        minSize = self.acqDict['PtclSizeShort']
        maxSize = self.acqDict['PtclSizeLong']
        ptclSizeAng = max(minSize, maxSize)
        # use +10% for mask size
        self.acqDict['MaskSize'] = str(1.1 * float(ptclSizeAng))

        angpix = float(self.acqDict['PixelSpacing'])
        if self.acqDict['Mode'] == 'Super-resolution':
            angpix = angpix * 2
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
        # guess folder name with movies on cista1, gain and defects for Krios
        # the code below is LMB-specific
        movieDir, gainFn, defFn = 'None', 'None', 'None'
        self.acqDict['MTF'] = ''
        camera = self.acqDict['Detector']
        scope = cs_dict[self.acqDict['MicroscopeID']][1]

        if self.getSoftware() == 'EPU':
            if 'Krios' in scope:
                p1 = pathDict[camera] % scope
                session = os.path.basename(self.getRawPath())

                if camera == 'EF-CCD':
                    # get gain file
                    movieDir = os.path.join(p1, "DoseFractions", session, epu_movies_path)
                    f1 = fnList.replace('.xml', '-gain-ref.MRC')  # TODO: check if gain is always named this way
                    f2 = f1.split('Images-Disc')[1]
                    gainFn = os.path.join(p1, "DoseFractions", session, "Images-Disc" + f2)

                    # get MTF file for Gatan
                    if scope == 'Krios3':
                        self.acqDict['MTF'] = mtf_dict['K3']
                    else:
                        self.acqDict['MTF'] = mtf_dict['K2']
                else:
                    movieDir = os.path.join(p1, session, epu_movies_path)

                    # get MTF file for Falcon
                    if self.acqDict['Mode'] == 'Linear':
                        self.acqDict['MTF'] = mtf_dict['Falcon3-linear']
                    else:
                        self.acqDict['MTF'] = mtf_dict['Falcon3-count']

            elif scope == 'Polara1':
                movieDir = pathDict[scope]
                self.acqDict['MTF'] = mtf_dict['Falcon3-linear']

        else:  # SerialEM
            movieDir = os.path.join(self.getRawPath(), "*.tif")
            gainFn = os.path.join(self.getRawPath(), self.acqDict['GainReference'])
            if 'DefectFile' in self.acqDict:
                defFn = os.path.join(self.getRawPath(), self.acqDict['DefectFile'])

            if camera == 'EF-CCD':
                # get MTF file for Gatan
                if scope in ['Krios3', 'Polara2']:
                    self.acqDict['MTF'] = mtf_dict['K3']
                else:
                    self.acqDict['MTF'] = mtf_dict['K2']
            else:
                # get MTF file for Falcon
                if self.acqDict['Mode'] == 'Linear':
                    self.acqDict['MTF'] = mtf_dict['Falcon3-linear']
                else:
                    self.acqDict['MTF'] = mtf_dict['Falcon3-count']

        # populate dict
        self.acqDict['Software'] = self.getSoftware()
        self.acqDict['PrjPath'] = self.getPrjPath()
        self.acqDict['MoviePath'] = movieDir
        self.acqDict['GainReference'] = gainFn
        self.acqDict['DefectFile'] = defFn
