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
from PyQt5.QtWidgets import (QGridLayout, QLabel, QMessageBox, QVBoxLayout,
                             QRadioButton, QPushButton, QWizard, QGroupBox,
                             QLineEdit, QFileDialog, QApplication, QWizardPage)
from PyQt5.QtCore import Qt

import sys
from config import *
from parser import Parser


'''
The app returns self.acqDict with all metadata.
Tested with:

 - EPU 1.10.0.77, 2.3.0.79, 2.0.13
 - SerialEM 3.7.0, 3.7.5

Units:
 - Dose, e/A^2 - total dose
 - DoseOnCamera, e/ubpx/s
 - DosePerFrame, e/A^2/
 - PixelSpacing, A
 - Voltage, keV
 - Defocus, um
 - Cs, mm
 - ExposureTime, s

TODO:
1) Get detector, beam tilt, vpp from SerialEM - add "AddToNextFrameStackMdoc key value" before R in SerialEM script
2) Validation of path etc
3) Reduce size of PtclSize path and Help button
'''


class App(QWizard):
    model = Parser()

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = 'MDCatch v0.5 - metadata parser'
        self.width = 640
        self.height = 280
        self.initUI()

    def initUI(self):
        self.page1 = Page1()
        self.addPage(self.page1)
        self.addPage(Page2(self))
        #self.button(QWizard.NextButton).clicked.connect(self.page2.runApp)
        self.button(QWizard.BackButton).clicked.connect(self.page1.reset)
        self.setWindowTitle(self.title)
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
        self.mainLayout = QGridLayout()
        self.renderPage1()

    def renderPage1(self):
        b1 = QLabel('Software')
        self.mainLayout.addWidget(b1, 0, 0)

        self.addRadioButton("EPU", 0, 1, default=True)
        self.addRadioButton("SerialEM", 0, 2)

        b2 = QLabel('Path')
        self.mainLayout.addWidget(b2, 1, 0)

        self.path = QLineEdit()
        self.path.setReadOnly(True)
        self.path.setText(default_path)
        self.mainLayout.addWidget(self.path, 1, 1, 1, 2)

        b3 = QPushButton('Browse')
        b3.clicked.connect(self.browseSlot)
        self.mainLayout.addWidget(b3, 1, 3)

        b4 = QLabel('Particle diameter (A)')
        self.mainLayout.addWidget(b4, 2, 0)

        self.size = QLineEdit()
        self.size.setValidator(QIntValidator())
        self.size.setMaxLength(4)
        self.size.setText('200')
        self.size.setAlignment(Qt.AlignRight)
        self.mainLayout.addWidget(self.size, 2, 1, 1, 1)

        b5 = QPushButton('Help')
        b5.clicked.connect(self.helpSlot)
        self.mainLayout.addWidget(b5, 3, 0)

        self.setLayout(self.mainLayout)

    def addRadioButton(self, choice, r, c, rows=1, cols=1, default=False):
        rb = QRadioButton(choice)
        if default:
            rb.setChecked(True)

        rb.toggled.connect(lambda: self.btnstate(rb))

        self.mainLayout.addWidget(rb, r, c, rows, cols)

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
        self.setLayout(self.mainLayout)

    def initializePage(self):
        # executed before showing page 2
        prog = App.model.getSoftware()
        fnList = App.model.getFn()

        if prog == 'EPU':
            App.model.parseImgXml(fnList)
        else:  # SerialEM
            App.model.parseImgMdoc(fnList)

        App.model.acqDict['PtclSize'] = App.model.getSize()
        App.model.calcDose()
        App.model.guessDataDir(fnList)

        if DEBUG:
            for k, v in App.model.acqDict.items():
                print(k, v)

        self.setSubTitle("Found the following metadata from %s session:" % prog)

        scopeID = str(App.model.acqDict['MicroscopeID'])
        time = round(float(App.model.acqDict['ExposureTime']), 3)
        dosepf = round(App.model.acqDict['DosePerFrame'], 2)
        px = round(App.model.acqDict['PixelSpacing'], 3)

        self.name.setText(cs_dict[scopeID][1])
        self.kv.setText(str(App.model.acqDict['Voltage']))
        self.cs.setText(str(App.model.acqDict['Cs']))
        self.mag.setText(str(App.model.acqDict['Magnification']))
        self.vpp.setText(str(App.model.acqDict['PhasePlateUsed']))

        self.name2.setText(str(App.model.acqDict['Detector']))
        self.mode.setText(str(App.model.acqDict['Mode']))
        self.time.setText(str(time))
        self.frames.setText(str(App.model.acqDict['NumSubFrames']))
        self.dosepf.setText(str(dosepf))
        self.px.setText(str(px))
        self.gain.setText(str(App.model.acqDict['GainReference']))
        self.defects.setText(str(App.model.acqDict['DefectFile']))

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
        self.vpp = QLabel()

        vbox = QGridLayout()
        vbox.addWidget(name, 0, 0)
        vbox.addWidget(self.name, 0, 1)
        vbox.addWidget(kv, 1, 0)
        vbox.addWidget(self.kv, 1, 1)
        vbox.addWidget(cs, 2, 0)
        vbox.addWidget(self.cs, 2, 1)
        vbox.addWidget(mag, 3, 0)
        vbox.addWidget(self.mag, 3, 1)
        vbox.addWidget(vpp, 4, 0)
        vbox.addWidget(self.vpp, 4, 1)
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
        self.dosepf = QLabel()
        self.px = QLabel()
        self.gain = QLabel()
        self.defects = QLabel()

        vbox = QGridLayout()
        vbox.addWidget(name2, 0, 0)
        vbox.addWidget(self.name2, 0, 1)
        vbox.addWidget(mode, 1, 0)
        vbox.addWidget(self.mode, 1, 1)
        vbox.addWidget(time, 2, 0)
        vbox.addWidget(self.time, 2, 1)
        vbox.addWidget(frames, 3, 0)
        vbox.addWidget(self.frames, 3, 1)
        vbox.addWidget(dosepf, 4, 0)
        vbox.addWidget(self.dosepf, 4, 1)
        vbox.addWidget(px, 5, 0)
        vbox.addWidget(self.px, 5, 1)
        vbox.addWidget(gain, 6, 0)
        vbox.addWidget(self.gain, 6, 1)
        vbox.addWidget(defects, 7, 0)
        vbox.addWidget(self.defects, 7, 1)

        groupBox.setLayout(vbox)

        return groupBox


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wizard = App()
    wizard.show()
    sys.exit(app.exec_())
