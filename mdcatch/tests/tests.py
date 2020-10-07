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
from glob import glob
import unittest

from ..config import *
from ..utils.misc import getUsername, setParticleSizes
from ..parser import Parser


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.epuDir = os.path.join(os.path.dirname(__file__), "../Metadata-examples/EPU")
        cls.semDir = os.path.join(os.path.dirname(__file__), "../Metadata-examples/SerialEM/")

    def test_epu(self):
        print("=" * 80, "\nTesting xml or mrc parser...")
        xmlFns = glob(os.path.join(self.epuDir, "*/%s" % PATTERN_EPU), recursive=True)
        xmlFns = [os.path.abspath(x) for x in xmlFns]

        for mdFn in xmlFns:
            mdPath = "/".join(mdFn.split("/")[:-4])
            model = Parser()
            model.setSoftware("EPU")
            self._runParser(model, mdPath, mdFn)

    def test_sem(self):
        print("=" * 80, "\nTesting mdoc or tif parser...")
        mdocFns = glob(os.path.join(self.semDir, PATTERN_SEM))
        mdocFns = [os.path.abspath(x) for x in mdocFns]

        for mdFn in mdocFns:
            mdPath = "/".join(mdFn.split("/")[:-1])
            model = Parser()
            model.setSoftware("SerialEM")
            self._runParser(model, mdPath, mdFn)

    def _runParser(self, model, mdPath, mdFn):
        """ Run the parser and return model acqDict. """
        model.setPipeline(DEF_PIPELINE)
        model.setMdPath(mdPath)
        model.setFn(mdFn)

        username, uid = getUsername(mdPath)
        model.setUser(username, uid)
        model.acqDict['User'] = model.getUser()

        print("\n\nInput params: ",
              model.getSoftware(),
              model.getMdPath(),
              model.getUser(),
              model.getPipeline())
        print("\nFiles found: %s\n" % mdFn)

        if model.getSoftware() == 'EPU':
            model.parseImgEpu(mdFn)
        else:  # SerialEM
            model.parseImgSem(mdFn)

        model.calcDose()
        model.guessDataDir(testmode=True)
        model.acqDict['Picker'] = DEF_PICKER
        setParticleSizes(model)

        print("\nFinal parameters:\n")
        for k, v in sorted(model.acqDict.items()):
            print(k, v)
        print('\n')
