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

import os
import math
import time
from glob import iglob

from .config import *
from .utils import parseXml, parseMrc, parseTif, parseMdoc


class Parser:
    """ Main parser class. """
    def __init__(self):
        # set default values
        self.mdPath = METADATA_PATH
        self.prjPath = PROJECT_PATH
        self.software = DEF_SOFTWARE
        self.user = None
        self.fn = None
        self.pipeline = DEF_PIPELINE
        self.picker = DEF_PICKER
        self.symmetry = DEF_SYMMETRY
        self.size = DEF_PARTICLE_SIZES

        self.acqDict = {
            'Mode': 'Linear',
            'NumSubFrames': '0',
            'Dose': '0',
            'OpticalGroup': 'opticsGroup1',
            'PhasePlateUsed': 'false',
            'GainReference': 'None',
            'DefectFile': 'None',
            'MTF': 'None'
        }

    def setMdPath(self, path):
        self.mdPath = path

    def getMdPath(self):
        return self.mdPath

    def setPipeline(self, choice):
        self.pipeline = choice

    def getPipeline(self):
        return self.pipeline

    def setPicker(self, choice):
        self.picker = choice

    def getPicker(self):
        return self.picker

    def setSymmetry(self, choice):
        self.symmetry = choice

    def getSymmetry(self):
        return self.symmetry

    def getSize(self):
        return self.size

    def setSize(self, *args):
        self.size = args

    def getPrjPath(self):
        return self.prjPath

    def setPrjPath(self, path):
        self.prjPath = path

    def getUser(self):
        return self.user

    def setUser(self, login, uid):
        self.user = (login, uid)

    def getSoftware(self):
        return self.software

    def setSoftware(self, soft):
        self.software = soft

    def setFn(self, fn):
        self.fn = fn

    def getFn(self):
        return self.fn

    def guessFn(self, prog="EPU"):
        """ Return the first matching filename. """
        regex = PATTERN_EPU if prog == "EPU" else PATTERN_SEM

        print("\nUsing regex: ", regex)

        files = iglob(os.path.join(self.getMdPath(), regex))
        img = next(files, None)

        return img

    def parseMetadata(self, fn):
        """ Parse metadata file and return updated acqDict. """
        if fn.endswith("xml"):
            acqDict = parseXml(fn)
        elif fn.endswith("tif") or fn.endswith("tiff"):
            acqDict = parseTif(fn)
        elif fn.endswith("mdoc"):
            acqDict = parseMdoc(fn)
        elif fn.endswith("mrc") or fn.endswith("mrcs"):
            acqDict = parseMrc(fn)
        else:
            raise Exception("Metadata format not recognized.")
        self.acqDict.update(acqDict)

    def calcDose(self):
        """ Calculate dose rate per unbinned px per s. """
        numFr = int(self.acqDict['NumSubFrames'])
        dose_total = float(self.acqDict['Dose'])  # e/A^2
        exp = float(self.acqDict['ExposureTime'])  # s

        if self.acqDict['Mode'] == 'Super-resolution':
            pix = 2 * float(self.acqDict['PixelSpacing']) / int(self.acqDict['Binning'])  # A
        else:
            pix = float(self.acqDict['PixelSpacing']) / int(self.acqDict['Binning'])  # A

        if numFr:  # not 0
            dose_per_frame = dose_total / numFr  # e/A^2/frame
        else:
            dose_per_frame = 0
        dose_on_camera = dose_total * math.pow(pix, 2) / exp  # e/unbinned_px/s

        self.acqDict['DosePerFrame'] = str(dose_per_frame)
        self.acqDict['DoseOnCamera'] = str(dose_on_camera)

    def calcBox(self):
        """ Calculate box, mask, downsample. """
        minSize, maxSize = self.acqDict['PtclSizes']
        angpix = float(self.acqDict['PixelSpacing'])

        if self.acqDict['Mode'] == 'Super-resolution' and self.acqDict['Binning'] == '1':
            # since we always bin by 2 in mc if using super-res and bin 1
            angpix *= 2

        ptclSizePx = float(maxSize) / angpix
        # use +20% for mask size
        self.acqDict['MaskSize'] = str(math.ceil(1.2 * ptclSizePx))
        # use +30% for box size, make it even
        boxSize = 1.3 * ptclSizePx
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

    def guessDataDir(self, wait=False, testmode=False):
        """ Guess folder name with movies, gain and defects files. """
        movieDir, gainFn, defFn = 'None', 'None', 'None'
        camera = self.acqDict['Detector']
        scopeID = self.acqDict['MicroscopeID']
        voltage = self.acqDict['Voltage']

        # get MTF file
        if camera == 'EF-CCD':
            model = SCOPE_DICT[scopeID][3]
            if model is not None:
                self.acqDict['MTF'] = MTF_DICT[model] % voltage
        else:
            model = SCOPE_DICT[scopeID][2]
            if self.acqDict['Mode'] == 'Linear':
                self.acqDict['MTF'] = MTF_DICT['%s-linear' % model] % voltage
            else:
                self.acqDict['MTF'] = MTF_DICT['%s-count' % model] % voltage

        # update with real camera name
        self.acqDict['Detector'] = model

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
                # Falcon 4 gain reference
                if model == "Falcon4":
                    gainFn = GAIN_DICT[model]

            if wait:  # in daemon mode wait for movie folder to appear
                while True:
                    if not os.path.exists(movieBaseDir):
                        print("Movie folder %s not found, waiting for 60 s.." % movieBaseDir)
                        time.sleep(60)
                    else:
                        print("Movie folder found! Continuing..")
                        break
            else:  # GUI mode
                if not os.path.exists(movieBaseDir) and not testmode:
                    raise FileNotFoundError("Movie folder %s does not exist!" % movieBaseDir)

        else:  # SerialEM
            movieDir = os.path.join(self.getMdPath(), PATTERN_SEM_MOVIES)
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
