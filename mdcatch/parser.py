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
from glob import iglob

from .config import *
from .utils import parseXml, parseMrc


class Parser:
    """ XML / MDOC parser. """
    def __init__(self):
        # set default values
        self.mdPath = METADATA_PATH
        self.prjPath = PROJECT_PATH
        self.software = 'EPU'
        self.user = USER, 0, 0
        self.fn = None
        self.pipeline = 'Relion'

        self.acqDict = dict()
        self.acqDict['Mode'] = 'Linear'
        self.acqDict['NumSubFrames'] = '0'
        self.acqDict['Dose'] = '0'
        self.acqDict['OpticalGroup'] = 'opticsGroup1'
        self.acqDict['PhasePlateUsed'] = 'false'
        self.acqDict['GainReference'] = 'None'
        self.acqDict['DefectFile'] = 'None'
        self.acqDict['MTF'] = ''

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

    def getSoftware(self):
        return self.software

    def setSoftware(self, soft):
        self.software = soft

    def setFn(self, fn):
        self.fn = fn

    def getFn(self):
        return self.fn

    def guessFn(self, prog="EPU"):
        regex = PATTERN_EPU if prog == "EPU" else PATTERN_MDOC

        if DEBUG:
            print("\nUsing regex: ", regex)

        files = iglob(os.path.join(self.getMdPath(), regex))
        img = next(files, None)

        return img

    def parseImgEpu(self, fn):
        acqDict = parseXml(fn) if fn.endswith("xml") else parseMrc(fn)
        self.acqDict.update(acqDict)

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
            # T = SerialEM: Acquired on Titan Krios D3593
            match = re.search("D[0-9]{3,4}", self.acqDict['T'])
            if match:
                value = match.group().replace('D', '')
                self.acqDict['MicroscopeID'] = value
                self.acqDict.pop('T')
                if value in SCOPE_DICT:
                    self.acqDict['Cs'] = str(SCOPE_DICT[value][1])

            self.acqDict['Dose'] = self.acqDict.pop('ExposureDose')
            self.acqDict['AppliedDefocus'] = self.acqDict.pop('TargetDefocus')
            self.acqDict['Mode'] = 'Super-resolution' if self.acqDict['Binning'] == '0.5' else 'Counting'
            if 'PhasePlateInserted' in self.acqDict:
                self.acqDict['PhasePlateUsed'] = self.acqDict.pop('PhasePlateInserted')
            self.acqDict.pop('Binning')
        except KeyError:
            pass

        if DEBUG:
            for k, v in sorted(self.acqDict.items()):
                print("%s = %s" % (k, v))

    def calcDose(self):
        """ Calculate dose rate per unbinned px. """
        numFr = int(self.acqDict['NumSubFrames'])
        dose_total = float(self.acqDict['Dose'])  # e/A^2
        exp = float(self.acqDict['ExposureTime'])  # s

        if self.acqDict['Mode'] == 'Super-resolution':
            pix = 2 * float(self.acqDict['PixelSpacing'])  # A
        else:
            pix = float(self.acqDict['PixelSpacing'])  # A

        if numFr:  # not 0
            dose_per_frame = dose_total / numFr  # e/A^2/frame
        else:
            dose_per_frame = 0
        dose_on_camera = dose_total * math.pow(pix, 2) / exp  # e/ubpx/s

        self.acqDict['DosePerFrame'] = str(dose_per_frame)
        self.acqDict['DoseOnCamera'] = str(dose_on_camera)

    def guessDataDir(self):
        """ Guess folder name with movies, gain and defects files. """
        movieDir, gainFn, defFn = 'None', 'None', 'None'
        camera = self.acqDict['Detector']
        scopeID = self.acqDict['MicroscopeID']

        # get MTF file
        if camera == 'EF-CCD':
            model = SCOPE_DICT[scopeID][3]
            if model is not None:
                self.acqDict['MTF'] = MTF_DICT[model]
        else:
            model = SCOPE_DICT[scopeID][2]
            if self.acqDict['Mode'] == 'Linear':
                self.acqDict['MTF'] = MTF_DICT['%s-linear' % model]
            else:
                self.acqDict['MTF'] = MTF_DICT['%s-count' % model]

        if self.getSoftware() == 'EPU':
            p1 = MOVIE_PATH_DICT[camera] % (SCOPE_DICT[scopeID][0], model)
            session = os.path.basename(self.getMdPath())

            if camera == 'EF-CCD':
                movieDir = os.path.join(p1, "DoseFractions", session, EPU_MOVIES_DICT[model])
                movieBaseDir = os.path.join(p1, "DoseFractions", session)
                gainFiles = iglob(os.path.join(os.path.dirname(movieDir), GAIN_DICT[model]))
                gainFn = next(gainFiles, 'None')
            else:
                movieDir = os.path.join(p1, session, EPU_MOVIES_DICT[model])
                movieBaseDir = os.path.join(p1, session)

            if not os.path.exists(movieBaseDir):
                raise FileNotFoundError("Movie folder %s does not exist!" % movieBaseDir)

        else:  # SerialEM
            movieDir = os.path.join(self.getMdPath(), "*.tif")
            gainFn = os.path.join(self.getMdPath(), self.acqDict['GainReference'])
            defFn = os.path.join(self.getMdPath(), self.acqDict['DefectFile'])

        # populate dict
        self.acqDict['Software'] = self.getSoftware()
        self.acqDict['PrjPath'] = self.getPrjPath()
        self.acqDict['MoviePath'] = movieDir
        if os.path.exists(gainFn):
            self.acqDict['GainReference'] = gainFn
        if os.path.exists(defFn):
            self.acqDict['DefectFile'] = defFn
