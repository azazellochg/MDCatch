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

from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QMessageBox,
                             QComboBox, QRadioButton, QPushButton,
                             QLineEdit, QFileDialog, QApplication)
from PyQt5.QtCore import Qt

import sys
import re
import os
import math
import xml.etree.cElementTree as ET

from config import *


'''

TODO:

1) figure out counting vs super-res mode for EPU: ElectronCountingEnabled=True?
2) add full path to gain / defects file in acqDict
3) add pattern for movies, guessed from EPU session name or tifs location

'''


class App(QWidget):
    """ GUI & validator """
    def __init__(self):
        super().__init__()
        self.title = 'MDCatch v0.4'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 180
        self.model = Model()
        self.mainLayout = QGridLayout()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.addSoftware('Software')
        self.addDirBrowser('Path')
        self.addPtclSize('Particle diameter (A)', '200')
        self.addRunButton('RUN!', 3, 0, 75, True)

        self.setLayout(self.mainLayout)
        self.show()

    def addLabel(self, name, r, c):
        lb = QLabel(name)
        self.mainLayout.addWidget(lb, r, c, 1, 1)

    def addScope(self, keys, name, r, c, rows=1, cols=1):
        self.cb = QComboBox()
        self.cb.addItems(keys)

        cbLabel = QLabel(name)
        cbLabel.setBuddy(self.cb)

        self.mainLayout.addWidget(cbLabel, r, c, rows, cols)
        self.mainLayout.addWidget(self.cb, r, c+1, rows, cols)

    def addRadioButton(self, choice, r, c, rows=1, cols=1, default=False):
        rb = QRadioButton(choice)
        if default:
            rb.setChecked(True)

        rb.toggled.connect(lambda: self.btnstate(rb))

        self.mainLayout.addWidget(rb, r, c, rows, cols)

    def btnstate(self, bt):
        if bt.isChecked():
            self.model.setSoftware(bt.text())

    def addSoftware(self, name):
        self.addLabel(name, 0, 0)
        self.addRadioButton('EPU', 0, 1, default=True)
        self.addRadioButton('SerialEM', 0, 2)

    def addPtclSize(self, label, size='200'):
        self.addLabel(label, 2, 0)
        self.le = QLineEdit()
        self.le.setValidator(QIntValidator())
        self.le.setMaxLength(4)
        self.le.setText(size)
        self.le.setAlignment(Qt.AlignRight)

        self.mainLayout.addWidget(self.le, 2, 1, 1, 1)

    def addRunButton(self, name, r, c, weight, bold=False):
        bt = QPushButton(name)

        font = QFont()
        font.setBold(bold)
        font.setWeight(weight)
        bt.setFont(font)

        bt.clicked.connect(self.runApp)
        bt.setDefault(True)

        self.mainLayout.addWidget(bt, r, c)

    def addDirBrowser(self, name):
        self.addLabel(name, 1, 0)

        self.lineEdit = QLineEdit()
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setText(default_path)

        bt = QPushButton('Browse')
        bt.clicked.connect(self.browseSlot)

        self.mainLayout.addWidget(self.lineEdit, 1, 1, 1, 2)
        self.mainLayout.addWidget(bt, 1, 3)

    def browseSlot(self):
        # called when user pressed Browse
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                default_path,
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.model.setPath(path)
            self.refreshPath()

    def refreshPath(self):
        # update line widget with selected path
        self.lineEdit.setText(self.model.getPath())

    @staticmethod
    def showDialog(title, text, extra=None):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        if extra is not None:
            msg.setDetailedText(extra)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def runApp(self):
        # RUN pressed
        self.model.setSize(self.le.text())
        if self.model.getSoftware() is None:
            self.model.setSoftware('EPU')
        if self.model.getPath() is None:
            self.model.setPath(default_path)

        if DEBUG:
            print("\n\nInput params: ",
                  [self.model.getSoftware(),
                  self.model.getPath(),
                  self.model.getSize()])

        matchDict = {'EPU': 'xml',
                     'SerialEM': 'mdoc'}

        prog = self.model.getSoftware()
        fnList = self.model.guessFn(matchDict[prog])

        if DEBUG:
            print("Files found: ", fnList)

        if fnList is not None:
            if prog == 'EPU':
                self.model.parseImgXml(fnList[0])
                if fnList[1] is not None:
                    self.model.parseSessionXml(fnList[1])
            else:  # SerialEM
                self.model.parseImgMdoc(fnList[0])

            self.model.acqDict['PtclSize'] = self.model.getSize()
            print("Results: ", self.model.acqDict.items())
            self.model.calcDose()


class Model:
    """ XML / MDOC parser """
    def __init__(self):
        self.path = None
        self.software = None
        self.ptclSize = None
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

    def guessFn(self, ftype="xml"):
        img, session = None, None
        regex = reg_xml if ftype == 'xml' else reg_mdoc

        if DEBUG:
            print("Using regex: ", regex)

        for root, _, files in os.walk(self.getPath()):
            for f in files:
                m = re.compile(regex).match(f)
                if m is not None:
                    img = os.path.join(root, f)
                    break
            if img is not None:
                break

        if ftype == "xml" and img is not None:
            #session = os.path.join(img.split("Images-Disc")[0], reg_xml2)
            session = reg_xml2
            if not os.path.exists(session):
                session = None

        if img is None:
            App.showDialog("ERROR",
                           "NO %s FILES WERE FOUND!\n\n"
                           "Please make sure that you selected correct folder:\n"
                           "   1) For EPU session it will be the folder on "
                           "/net/em-support3/ with Images-DiscX folder inside.\n"
                           "   2) For SerialEM session it will be the folder "
                           "on /net/cista1/ that contains tif and mdoc files inside.\n"
                           % ftype)
            return

        return [img, session]

    def parseImgXml(self, fn):
        tree = ET.parse(fn)
        root = tree.getroot()

        if root[5][1].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}pixelSize':
            self.acqDict['PixelSpacing'] = float(root[5][1][0][0].text)

        if root[6][0][2][4].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ExposureTime':
            self.acqDict['ExposureTime'] = float(root[6][0][2][4].text)

        if root[6][0][2][6].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Name':
            self.acqDict['detector'] = root[6][0][2][6].text

            if self.acqDict['detector'] == 'EF-CCD' and root[6][0][2][2][3][0].text == 'FractionationSettings':
                self.acqDict['NumSubFrames'] = int(root[6][0][2][2][3][1][0].text)
            else:
                # count number of b:DoseFractionDefinition occurrences for Falcon 3
                if root[6][0][2][2][5][0].text == 'FractionationSettings':
                    self.acqDict['NumSubFrames'] = len(list(root[6][0][2][2][5][1][0]))
                elif root[6][0][2][2][3][0].text == 'FractionationSettings':
                    self.acqDict['NumSubFrames'] = len(list(root[6][0][2][2][3][1][0]))

        if root[6][2][0].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage':
            self.acqDict['Voltage'] = int(root[6][2][0].text)

        if root[6][3][3].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID':
            self.acqDict['microscopeID'] = int(root[6][3][3].text)

            value = str(self.acqDict['microscopeID'])
            if value in cs_dict:
                self.acqDict['Cs'] = cs_dict[value]

        if root[6][4][3].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamTilt':
            self.acqDict['beamTiltX'] = float(root[6][4][3][0].text)
            self.acqDict['beamTiltY'] = float(root[6][4][3][1].text)

        if root[6][4][28][0].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}NominalMagnification':
            self.acqDict['Magnification'] = int(root[6][4][28][0].text)

        # get customData: Dose, DoseOnCamera, PhasePlateUsed, AppliedDefocus etc.
        if root[2].tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}CustomData':
            i = 0
            while i < 8:
                try:
                    self.acqDict[root[2][i][0].text] = root[2][i][1].text
                    i += 1
                except IndexError:
                    break

    def parseSessionXml(self, fn):
        tree = ET.parse(fn)
        root = tree.getroot()

        if root[7].tag == '{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}DoseFractionsOutputFormat':
            self.acqDict['movieType'] = root[7].text

        elif root[4].tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Epu.Persistence}DoseFractionsOutputFormat':
            self.acqDict['movieType'] = root[4].text

    def parseImgMdoc(self, fn):
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
                self.acqDict['microscopeID'] = value
                self.acqDict.pop('T')
                if value in cs_dict:
                    self.acqDict['Cs'] = cs_dict[value]

            self.acqDict['Dose'] = float(self.acqDict.pop('ExposureDose')) / math.pow(10, -20)
            self.acqDict['AppliedDefocus'] = float(self.acqDict.pop('TargetDefocus')) * math.pow(10, -6)
            self.acqDict['Voltage'] = int(self.acqDict['Voltage']) * 1000
            self.acqDict['PixelSpacing'] = float(self.acqDict['PixelSpacing']) * math.pow(10, -10)
        except KeyError:
            pass

    def calcDose(self):
        # calculate dose
        dose_per_frame, dose_on_camera = 0, 0
        numFr = int(self.acqDict['NumSubFrames'])
        dose_total = float(self.acqDict['Dose'])  # e/m^2
        exp = float(self.acqDict['ExposureTime'])  # s
        if 'Binning' in self.acqDict and self.acqDict['Binning'] == '0.5':
            pix = 2 * float(self.acqDict['PixelSpacing'])  # m
        else:
            pix = float(self.acqDict['PixelSpacing'])  # m

        if numFr and dose_total:
            dose_per_frame = dose_total / math.pow(10, 20) / numFr  # e/A^2/frame
            if exp and pix:
                dose_on_camera = dose_total * math.pow(pix, 2) / exp  # e/px/s

        print("Extra output: dose per frame (e/A^2) = ", dose_per_frame,
              "\ndose on camera (e/ubpx/s) = ", dose_on_camera)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App()
    sys.exit(app.exec_())
