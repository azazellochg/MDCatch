# -*- coding: utf-8 -*-
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

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QGridLayout, QLabel, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QRadioButton,
                             QPushButton, QWizard, QGroupBox,
                             QSizePolicy, QLineEdit, QFileDialog,
                             QComboBox, QApplication, QWizardPage,
                             QCheckBox)
from PyQt5.QtCore import Qt

import os
import sys
import subprocess

from config import *
from parser import Parser


'''
The app returns self.acqDict with all metadata.
Tested with:

 - EPU 1.10.0.77, 2.3.0.79, 2.0.13
 - SerialEM 3.7, 3.8

Units:
 - Dose, e/A^2 - total dose
 - DoseOnCamera, e/ubpx/s
 - DosePerFrame, e/A^2/
 - PixelSpacing, A
 - Voltage, keV
 - Defocus, um
 - Cs, mm
 - ExposureTime, s

'''


class App(QWizard):
    model = Parser()

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = 'MDCatch v0.6 - metadata parser'
        self.width = 640
        self.height = 280
        self.initUI()

    def initUI(self):
        self.page1 = Page1()
        self.addPage(self.page1)
        self.page2 = Page2()
        self.addPage(self.page2)
        self.button(QWizard.BackButton).clicked.connect(self.page1.reset)
        self.button(QWizard.FinishButton).clicked.connect(self.page2.onFinish)
        self.setWindowTitle(self.title)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(self.width, self.height)

    @staticmethod
    def showDialog(title, text, mtype='error', extra=None):
        msg = QMessageBox()
        if mtype == 'error':
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        if extra is not None:
            msg.setDetailedText(extra)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class Page1(QWizardPage):
    def __init__(self, parent=None):
        super(Page1, self).__init__(parent)
        self.setSubTitle("Input parameters")
        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(self.group1(), 0, 0)
        self.mainLayout.addLayout(self.group2(), 0, 1)
        self.setLayout(self.mainLayout)

    def group1(self):
        vbox = QVBoxLayout()
        label1 = QLabel('Software')
        label2 = QLabel('Path')
        label3 = QLabel('Particle diameter (A)')
        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(label3)

        return vbox

    def group2(self):
        grid = QVBoxLayout()

        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignLeft)
        b1 = self.addRadioButton("EPU", default=True)
        b2 = self.addRadioButton("SerialEM")
        hbox1.addWidget(b1)
        hbox1.addWidget(b2)
        grid.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setReadOnly(True)
        self.path.setText(default_path)

        b3 = QPushButton('Browse')
        b3.clicked.connect(self.browseSlot)
        b4 = QPushButton('?')
        b4.setFixedSize(20, 20)
        b4.clicked.connect(self.helpSlot)

        hbox2.addWidget(self.path)
        hbox2.addWidget(b3)
        hbox2.addWidget(b4)
        grid.addLayout(hbox2)

        self.size = QLineEdit()
        self.size.setValidator(QIntValidator())
        self.size.setMaxLength(4)
        self.size.setText('200')
        self.size.setAlignment(Qt.AlignRight)
        self.size.setFixedSize(60, 20)
        grid.addWidget(self.size)

        return grid

    def addRadioButton(self, choice, default=False):
        rb = QRadioButton(choice)
        if default:
            rb.setChecked(True)

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        rb.setSizePolicy(sizePolicy)

        rb.toggled.connect(lambda: self.btnstate(rb))

        return rb

    def btnstate(self, bt):
        if bt.isChecked():
            App.model.setSoftware(bt.text())

    def browseSlot(self):
        # called when user pressed Browse
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                default_path,
                                                QFileDialog.ShowDirsOnly)
        if path:
            App.model.setPath(path)
            self.refreshPath()

    def refreshPath(self):
        # update line widget with selected path
        self.path.setText(App.model.getPath())

    def helpSlot(self):
        # called when pressed ?
        App.showDialog("Help", help_message, 'help')
        return

    def validatePage(self):
        # Next is pressed, returns True or False
        App.model.setSize(self.size.text())
        if App.model.getSoftware() is None:
            App.model.setSoftware('EPU')
        if App.model.getPath() is None:
            App.model.setPath(default_path)

        if DEBUG:
            print("\n\nInput params: ",
                  [App.model.getSoftware(),
                   App.model.getPath(),
                   App.model.getSize()])

        prog = App.model.getSoftware()
        fnList = App.model.guessFn(matchDict[prog])

        if fnList is None:
            App.showDialog("ERROR", error_message % matchDict[prog])
            return False
        else:
            print("\nFiles found: %s\n" % fnList) if DEBUG else ""
            App.model.setFn(fnList)
            return True

    def reset(self):
        # Back pressed
        App.model.acqDict.clear()


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.group1(), 0, 0)
        self.mainLayout.addWidget(self.group2(), 0, 1)
        self.mainLayout.addWidget(self.relionBox(), 1, 0)
        self.setLayout(self.mainLayout)

    def initializePage(self):
        # executed before showing page 2
        acqDict = App.model.acqDict
        prog = App.model.getSoftware()
        fnList = App.model.getFn()

        if prog == 'EPU':
            App.model.parseImgXml(fnList)
        else:  # SerialEM
            App.model.parseImgMdoc(fnList)

        acqDict['PtclSize'] = App.model.getSize()
        App.model.calcDose()
        App.model.guessDataDir(fnList)

        self.setSubTitle("Found the following metadata from %s session:" % prog)

        scopeID = acqDict['MicroscopeID']
        time = round(float(acqDict['ExposureTime']), 3)
        dosepf = round(float(acqDict['DosePerFrame']), 2)
        px = round(float(acqDict['PixelSpacing']), 3)

        self.name.setText(cs_dict[scopeID][1])
        self.kv.setText(acqDict['Voltage'])
        self.cs.setText(acqDict['Cs'])
        self.mag.setText(acqDict['Magnification'])

        vpp = acqDict['PhasePlateUsed']
        if vpp in ['true', 'True']:
            self.vpp.setCurrentIndex(0)
        else:
            self.vpp.setCurrentIndex(1)

        self.name2.setText(acqDict['Detector'])
        self.mode.setText(acqDict['Mode'])
        self.time.setText(str(time))
        self.frames.setText(acqDict['NumSubFrames'])
        self.dosepf.setText(str(dosepf))
        self.px.setText(str(px))
        self.gain.setText(os.path.basename(acqDict['GainReference']))
        self.defects.setText(os.path.basename(acqDict['DefectFile']))

    def group1(self):
        groupBox = QGroupBox("Microscope")

        name = QLabel("Name")
        kv = QLabel("Voltage")
        cs = QLabel("Cs")
        mag = QLabel("Magnification")
        vpp = QLabel("Phase plate")

        self.name = QLabel()
        self.kv = QLabel()
        self.cs = QLabel()
        self.mag = QLabel()

        self.vpp = QComboBox()
        vpp_values = ['true', 'false']
        self.vpp.addItems(vpp_values)
        self.vpp.setFixedSize(60, 20)

        vbox = QGridLayout()
        for num, i in enumerate([name, kv, cs, mag, vpp]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.name, self.kv,
                                 self.cs, self.mag,
                                 self.vpp]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def group2(self):
        groupBox = QGroupBox("Detector")

        name2 = QLabel("Name")
        mode = QLabel("Mode")
        time = QLabel("Exposure time, s")
        frames = QLabel("Frames")
        dosepf = QLabel("Dose per frame, e/A²")
        px = QLabel("Pixel size, A")
        gain = QLabel("Gain reference")
        defects = QLabel("Defects file")

        self.name2 = QLabel()
        self.mode = QLabel()
        self.time = QLabel()
        self.frames = QLabel()
        self.gain = QLabel()
        self.defects = QLabel()

        self.dosepf = QLineEdit()
        self.dosepf.setFixedSize(50, 20)
        self.dosepf.setMaxLength(4)
        self.dosepf.setAlignment(Qt.AlignRight)

        self.px = QLineEdit()
        self.px.setFixedSize(50, 20)
        self.px.setMaxLength(4)
        self.px.setAlignment(Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([name2, mode, time, frames,
                                 dosepf, px, gain, defects]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.name2, self.mode,
                                 self.time, self.frames,
                                 self.dosepf, self.px,
                                 self.gain, self.defects]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def relionBox(self):
        self.setRln = QCheckBox("Setup Relion scheduler")
        self.setRln.setChecked(True)

        return self.setRln

    def onFinish(self):
        # Finish pressed
        App.model.acqDict['DosePerFrame'] = self.dosepf.text()
        App.model.acqDict['PixelSpacing'] = self.px.text()
        App.model.acqDict['PhasePlateUsed'] = self.vpp.currentText()

        if DEBUG:
            for k, v in App.model.acqDict.items():
                print(k, v)

        if self.setRln.isChecked():
            self.setupSchedule(App.model.acqDict)

    def setupSchedule(self, paramDict):
        fnDir = os.path.join(schedule_dir, 'preprocess')
        bin = 2.0 if paramDict['Mode'] == 'Super-resolution' else 1.0
        vpp = True if paramDict['PhasePlateUsed'] in ['true', 'True'] else False
        gain = '' if paramDict['GainReference'] == 'None' else paramDict['GainReference']
        # set box_size = PtclSize + 10%
        box_size = round(int(paramDict['PtclSize']) / float(paramDict['PixelSpacing']) * 1.1, 0)

        mapDict = {'Cs': paramDict['Cs'],
                   'dose_rate': paramDict['DosePerFrame'],
                   'mask_diam': paramDict['PtclSize'],
                   'angpix': paramDict['PixelSpacing'],
                   'voltage': paramDict['Voltage'],
                   'motioncorr_bin': bin,
                   'box_size': box_size,
                   'is_VPP': vpp,
                   'gainref': gain,
                   'movies_wildcard': '"%s"' % paramDict['MoviePath'],
                   'mtf_file': paramDict['MTF'],
                   'optics_group': paramDict['OpticalGroup']}

        cmdList = list()

        for key in mapDict:
            cmd = 'relion_scheduler --schedule %s --set_var %s --value %s' % (
                fnDir, key, str(mapDict[key]))
            cmdList.append(cmd)
        cmdList.append('relion_scheduler --schedule %s --run ' % fnDir)

        if DEBUG:
            for cmd in cmdList:
                print(cmd)

        cmd = '\n'.join([line for line in cmdList])
        proc = subprocess.check_output(cmd, shell=True)
        proc.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wizard = App()
    wizard.show()
    sys.exit(app.exec_())
