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
                             QRadioButton, QPushButton, QWizard,
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
        self.height = 180
        self.initUI()

    def initUI(self):
        self.page1 = Page1()
        self.addPage(self.page1)
        self.addPage(Page2(self))
        self.button(QWizard.NextButton).clicked.connect(self.page1.runApp)
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

    def runApp(self):
        # Next pressed
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

        matchDict = {"EPU": 'xml',
                     "SerialEM": 'mdoc'}

        prog = App.model.getSoftware()
        fnList = App.model.guessFn(matchDict[prog])
        if fnList is None:
            App.showDialog("ERROR", error_message % matchDict[prog])

        if DEBUG:
            print("\nFiles found: %s\n" % fnList)

        if fnList is not None:
            if prog == 'EPU':
                App.model.parseImgXml(fnList)
            else:  # SerialEM
                App.model.parseImgMdoc(fnList)

            App.model.acqDict['PtclSize'] = App.model.getSize()
            App.model.calcDose()
            App.model.guessDataDir(fnList)
            for k, v in App.model.acqDict.items():
                print(k, v)

    def reset(self):
        # Back pressed
        App.model.acqDict.clear()


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.mainLayout = QGridLayout()
        self.renderPage2()
        self.setLayout(self.mainLayout)

    def renderPage2(self):
        self.label1 = QLabel()
        self.label1.setText("test")
        self.mainLayout.addWidget(self.label1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wizard = App()
    wizard.show()
    sys.exit(app.exec_())
