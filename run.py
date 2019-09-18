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

from PyQt5.QtWidgets import (QGridLayout, QLabel, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QRadioButton,
                             QPushButton, QWizard, QGroupBox, QSpinBox,
                             QSizePolicy, QLineEdit, QFileDialog,
                             QCheckBox, QApplication, QWizardPage)
from PyQt5.QtCore import Qt
import sys

from parser import Parser
from schedule import *


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
        self.title = 'MDCatch v0.8 - metadata parser'
        self.width = 640
        self.height = 480
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

        # software type
        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignLeft)
        b1 = self.addRadioButton("EPU", default=True)
        b2 = self.addRadioButton("SerialEM")
        hbox1.addWidget(b1)
        hbox1.addWidget(b2)
        grid.addLayout(hbox1)

        # path box
        hbox2 = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setReadOnly(True)
        self.path.setText(default_path)

        b3 = QPushButton('Browse')
        b3.clicked.connect(self.browseSlot)
        b4 = QPushButton('?')
        b4.setFixedSize(20, 25)
        b4.clicked.connect(self.helpSlot)

        hbox2.addWidget(self.path)
        hbox2.addWidget(b3)
        hbox2.addWidget(b4)
        grid.addLayout(hbox2)

        # size box
        hbox3 = QHBoxLayout()
        labelSizeMin = QLabel('from')
        hbox3.addWidget(labelSizeMin)

        self.size_short = QSpinBox()
        self.size_short.setRange(1, 999)
        self.size_short.setValue(part_size_short)
        self.size_short.setFixedSize(60, 25)
        hbox3.addWidget(self.size_short)

        labelSizeMax = QLabel('to')
        hbox3.addWidget(labelSizeMax)

        self.size_long = QSpinBox()
        self.size_long.setRange(1, 999)
        self.size_long.setValue(part_size_long)
        self.size_long.setFixedSize(60, 25)
        hbox3.addWidget(self.size_long)
        hbox3.setAlignment(Qt.AlignLeft)

        grid.addLayout(hbox3)

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
        folder = default_path if self.path.text() is None else self.path.text()
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                folder,
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
        App.model.setSizeShort(self.size_short.text())
        App.model.setSizeLong(self.size_long.text())
        if App.model.getSoftware() is None:
            App.model.setSoftware('EPU')
        if App.model.getPath() is None:
            App.model.setPath(default_path)

        if DEBUG:
            print("\n\nInput params: ",
                  [App.model.getSoftware(),
                   App.model.getPath(),
                   App.model.getSizeShort(),
                   App.model.getSizeLong()])

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
        App.model.__init__()


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.group1(), 0, 0)
        self.mainLayout.addWidget(self.group2(), 0, 1)
        self.mainLayout.addWidget(self.group3(), 1, 0)
        self.mainLayout.addWidget(self.group4(), 1, 1)
        self.mainLayout.addWidget(self.relionBt(), 2, 0)
        self.mainLayout.addWidget(self.scipionBt(), 2, 1)
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

        acqDict['PtclSizeShort'] = App.model.getSizeShort()
        acqDict['PtclSizeLong'] = App.model.getSizeLong()
        App.model.calcDose()
        App.model.calcBox()
        App.model.guessDataDir(fnList)

        self.setSubTitle("Found the following metadata from %s session:" % prog)

        scopeID = acqDict['MicroscopeID']
        time = round(float(acqDict['ExposureTime']), 3)
        dosepf = round(float(acqDict['DosePerFrame']), 2)
        px = round(float(acqDict['PixelSpacing']), 4)

        self.name.setText(cs_dict[scopeID][1])
        self.kv.setText(acqDict['Voltage'])
        self.cs.setText(acqDict['Cs'])
        self.px.setText(str(px))

        vpp = acqDict['PhasePlateUsed']
        if vpp in ['true', 'True']:
            self.vpp.setChecked(True)
        else:
            self.vpp.setChecked(False)

        self.name2.setText(acqDict['Detector'])
        self.mode.setText(acqDict['Mode'])
        self.time.setText(str(time))
        self.frames.setText(acqDict['NumSubFrames'])
        self.dosepf.setText(str(dosepf))
        self.gain.setText(os.path.basename(acqDict['GainReference']))
        self.defects.setText(os.path.basename(acqDict['DefectFile']))

        self.box.setText(acqDict['BoxSize'])
        self.mask.setText(acqDict['MaskSize'])
        self.box2.setText(acqDict['BoxSizeSmall'])

    def group1(self):
        groupBox = QGroupBox("Microscope")

        name = QLabel("Name")
        kv = QLabel("Voltage (kV)")
        cs = QLabel("Cs (mm)")
        vpp = QLabel("Phase plate")
        px = QLabel("Pixel size (A)")

        self.name = QLabel()
        self.kv = QLabel()
        self.cs = QLabel()
        self.vpp = QCheckBox()

        self.px = QLineEdit()
        self.px.setFixedSize(50, 20)
        self.px.setMaxLength(5)
        self.px.setAlignment(Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([name, kv, cs, px, vpp]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.name, self.kv,
                                 self.cs, self.px, self.vpp]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def group2(self):
        groupBox = QGroupBox("Detector")

        name2 = QLabel("Name")
        mode = QLabel("Mode")
        time = QLabel("Exposure time (s)")
        frames = QLabel("Frames")
        dosepf = QLabel("Dose per frame (e/A²)")
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

        vbox = QGridLayout()
        for num, i in enumerate([name2, mode, time, frames,
                                 dosepf, gain, defects]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.name2, self.mode,
                                 self.time, self.frames,
                                 self.dosepf, self.gain,
                                 self.defects]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def group3(self):
        groupBox = QGroupBox("Particle")

        box = QLabel("Box size (px)")
        mask = QLabel("Mask size (A)")
        box2 = QLabel("Downscale to (px)")

        self.box = QLineEdit()
        self.box.setFixedSize(50, 20)
        self.box.setMaxLength(5)
        self.box.setAlignment(Qt.AlignRight)

        self.mask = QLineEdit()
        self.mask.setFixedSize(50, 20)
        self.mask.setMaxLength(5)
        self.mask.setAlignment(Qt.AlignRight)

        self.box2 = QLineEdit()
        self.box2.setFixedSize(50, 20)
        self.box2.setMaxLength(5)
        self.box2.setAlignment(Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([box, mask, box2]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.box, self.mask,
                                 self.box2]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def group4(self):
        groupBox = QGroupBox("Preprocessing")

        self.runCtf = QRadioButton("Stop after CTF estimation?")
        self.runCl2d = QRadioButton("Do 2D classification?")
        self.runCl2d.setChecked(True)

        hbox = QGridLayout()
        hbox.addWidget(self.runCtf, 0, 0)
        hbox.addWidget(self.runCl2d, 1, 0)
        groupBox.setLayout(hbox)

        return groupBox

    def relionBt(self):
        self.setRln = QRadioButton("Start Relion scheduler")
        self.setRln.setChecked(True)

        return self.setRln

    def scipionBt(self):
        self.setScp = QRadioButton("Start Scipion workflow")

        return self.setScp

    def onFinish(self):
        # Finish pressed, we need to update all editable vars
        App.model.acqDict['DosePerFrame'] = self.dosepf.text()
        App.model.acqDict['PixelSpacing'] = self.px.text()
        App.model.acqDict['PhasePlateUsed'] = self.vpp.isChecked()
        App.model.acqDict['NoCl2D'] = self.runCtf.isChecked()
        App.model.acqDict['BoxSize'] = self.box.text()
        App.model.acqDict['MaskSize'] = self.mask.text()
        App.model.acqDict['BoxSizeSmall'] = self.box2.text()

        if DEBUG:
            for k, v in App.model.acqDict.items():
                print(k, v)
            print('\n')

        if self.setRln.isChecked():
            setupRelion(App.model.acqDict)
        else:
            setupScipion(App.model.acqDict)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wizard = App()
    wizard.show()
    sys.exit(app.exec_())
