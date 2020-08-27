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

import os
import sys
from PyQt5.QtWidgets import (QGridLayout, QLabel, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QRadioButton,
                             QPushButton, QWizard, QGroupBox,
                             QSizePolicy, QLineEdit, QFileDialog,
                             QCheckBox, QApplication, QWizardPage,
                             QButtonGroup, QSpinBox)
from PyQt5.QtCore import Qt

from .config import *
from .parser import Parser
from .schedule import setupRelion, setupScipion


class App(QWizard):
    model = Parser()

    def __init__(self, parent=None):
        super(App, self).__init__(parent, flags=Qt.WindowFlags())
        self.title = 'MDCatch v0.9.8 - metadata parser'
        self.width = 640
        self.height = 320
        self.initUI()

    def initUI(self):
        self.page1 = Page1()
        self.addPage(self.page1)
        self.page2 = Page2()
        self.addPage(self.page2)
        self.button(QWizard.BackButton).clicked.connect(self.page1.reset)
        self.button(QWizard.FinishButton).clicked.connect(self.page2.onFinish)
        self.setWindowTitle(self.title)
        # remove Help button from the window
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
        label3 = QLabel('Run pipeline in')
        label4 = QLabel('Particle picker')
        label5 = QLabel('Particle size (A)')
        label5.setToolTip(help_picker)

        vbox.addWidget(label1, alignment=Qt.Alignment())
        vbox.addWidget(label2, alignment=Qt.Alignment())
        vbox.addWidget(label3, alignment=Qt.Alignment())
        vbox.addWidget(label4, alignment=Qt.Alignment())
        vbox.addWidget(label5, alignment=Qt.Alignment())

        return vbox

    def group2(self):
        grid = QVBoxLayout()

        # software type
        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignLeft)
        btgroup1 = QButtonGroup()

        b1 = self.addRadioButton("EPU", default=DEF_SOFTWARE=="EPU")
        b2 = self.addRadioButton("SerialEM", default=DEF_SOFTWARE=="SerialEM")

        btgroup1.addButton(b1)
        btgroup1.addButton(b2)
        btgroup1.buttonClicked.connect(lambda: self.updSoftware(btgroup1))
        hbox1.addWidget(b1, alignment=Qt.Alignment())
        hbox1.addWidget(b2, alignment=Qt.Alignment())
        grid.addLayout(hbox1)

        # path box
        hbox2 = QHBoxLayout()
        self.rawPath = QLineEdit()
        self.rawPath.setMinimumWidth(300)
        self.rawPath.setReadOnly(True)
        self.rawPath.setText(METADATA_PATH)
        self.rawPath.setToolTip(help_message)

        b3 = QPushButton('Browse')
        b3.setToolTip(help_message)
        b3.clicked.connect(lambda: self.browseSlot(self.rawPath))

        hbox2.addWidget(self.rawPath, alignment=Qt.Alignment())
        hbox2.addWidget(b3, alignment=Qt.Alignment())
        grid.addLayout(hbox2)

        # pipeline
        hbox3 = QHBoxLayout()
        hbox3.setAlignment(Qt.AlignLeft)
        btgroup2 = QButtonGroup()

        b4 = self.addRadioButton("Relion", default=DEF_PIPELINE=="Relion")
        b5 = self.addRadioButton("Scipion", default=DEF_PIPELINE=="Scipion")

        btgroup2.addButton(b4)
        btgroup2.addButton(b5)
        btgroup2.buttonClicked.connect(lambda: self.updPipeline(btgroup2))
        hbox3.addWidget(b4, alignment=Qt.Alignment())
        hbox3.addWidget(b5, alignment=Qt.Alignment())
        grid.addLayout(hbox3)

        # particle picker
        hbox4 = QHBoxLayout()
        hbox4.setAlignment(Qt.AlignLeft)
        btgroup3 = QButtonGroup()

        self.b6 = self.addRadioButton("crYOLO", default=DEF_PICKER == "crYOLO")
        self.b7 = self.addRadioButton("Topaz", default=DEF_PICKER == "Topaz")
        self.b8 = self.addRadioButton("LogPicker", default=DEF_PICKER == "LogPicker")

        btgroup3.addButton(self.b6)
        btgroup3.addButton(self.b7)
        btgroup3.addButton(self.b8)
        btgroup3.buttonClicked.connect(lambda: self.updPicker(btgroup3))
        hbox4.addWidget(self.b6, alignment=Qt.Alignment())
        hbox4.addWidget(self.b7, alignment=Qt.Alignment())
        hbox4.addWidget(self.b8, alignment=Qt.Alignment())
        grid.addLayout(hbox4)

        # size box
        hbox5 = QHBoxLayout()
        self.labelSizeMin = QLabel('')
        self.labelSizeMin.setToolTip(help_picker)
        hbox5.addWidget(self.labelSizeMin)

        self.size_short = QSpinBox()
        self.size_short.setToolTip(help_picker)
        self.size_short.setRange(0, 9999)
        self.size_short.setValue(LOGPICKER_SIZES[0] if DEF_PICKER != "crYOLO" else 0)
        self.size_short.setFixedSize(60, 25)
        hbox5.addWidget(self.size_short)

        self.labelSizeMax = QLabel('max')
        self.labelSizeMax.setToolTip(help_picker)
        self.labelSizeMax.setVisible(self.b8.isChecked())
        hbox5.addWidget(self.labelSizeMax)

        self.size_long = QSpinBox()
        self.size_long.setToolTip(help_picker)
        self.size_long.setVisible(self.b8.isChecked())
        self.size_long.setRange(10, 9999)
        self.size_long.setValue(LOGPICKER_SIZES[1])
        self.size_long.setFixedSize(60, 25)
        hbox5.addWidget(self.size_long)
        hbox5.setAlignment(Qt.AlignLeft)
        grid.addLayout(hbox5)

        return grid

    def updSoftware(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.setSoftware(bt.text())

    def updPipeline(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.setPipeline(bt.text())

    def updPicker(self, btgroup):
        bt = btgroup.checkedButton()
        if self.b6.isChecked():  # crYOLO
            self.labelSizeMin.setText("")
            self.size_short.setValue(0)
            self.labelSizeMax.setVisible(False)
            self.size_long.setVisible(False)
        elif self.b7.isChecked():  # Topaz
            self.labelSizeMin.setText("")
            self.size_short.setValue(LOGPICKER_SIZES[0])
            self.labelSizeMax.setVisible(False)
            self.size_long.setVisible(False)
        elif self.b8.isChecked():  # LogPicker
            self.labelSizeMin.setText("min")
            self.size_short.setValue(LOGPICKER_SIZES[0])
            self.labelSizeMax.setVisible(True)
            self.size_long.setVisible(True)

        App.model.setPicker(bt.text())
        App.model.setSize(self.size_short.value(), self.size_long.value())

    def browseSlot(self, var):
        # called when "Browse" is pressed
        folder = METADATA_PATH if var.text() is None else var.text()
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                folder,
                                                options=QFileDialog.ShowDirsOnly)
        if path:
            self.refreshPath(path)

    def refreshPath(self, path):
        # update line widget with selected path
        App.model.setMdPath(path)
        self.rawPath.setText(App.model.getMdPath())

    def helpSlot(self):
        # called when "?" is pressed
        App.showDialog("Help", help_message, 'help')
        return

    def validatePage(self):
        # Next is pressed, returns True or False
        if App.model.getMdPath() is None:
            App.model.setMdPath(METADATA_PATH)

        if DEBUG:
            print("\n\nInput params: ",
                  [App.model.getSoftware(),
                   App.model.getMdPath(),
                   App.model.getUser(),
                   App.model.getPipeline(),
                   App.model.getPicker(),
                   App.model.getSize()])

        prog = App.model.getSoftware()
        fnList = App.model.guessFn(prog)

        if fnList is None:
            App.showDialog("ERROR", "No matching files found!\n\n" + help_message)
            return False
        else:
            print("\nFiles found: %s\n" % fnList) if DEBUG else ""
            App.model.setFn(fnList)
            return True

    def reset(self):
        # "Back" is pressed
        App.model.acqDict.clear()
        App.model.__init__()

    def addRadioButton(self, choice, default=False):
        rb = QRadioButton(choice)
        if default:
            rb.setChecked(True)

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        rb.setSizePolicy(sizePolicy)
        return rb


class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.group1(), 0, 0)
        self.mainLayout.addWidget(self.group2(), 0, 1)
        self.setLayout(self.mainLayout)

    def initializePage(self):
        # executed before showing page 2
        acqDict = App.model.acqDict
        prog = App.model.getSoftware()
        fnList = App.model.getFn()

        if prog == 'EPU':
            App.model.parseImgEpu(fnList)
        else:  # SerialEM
            App.model.parseImgMdoc(fnList)

        acqDict['Picker'] = App.model.getPicker()
        acqDict['PtclSizes'] = App.model.getSize()
        App.model.calcDose()
        App.model.guessDataDir()

        self.setSubTitle("Found the following metadata from %s session:" % prog)

        scopeID = acqDict['MicroscopeID']
        time = round(float(acqDict['ExposureTime']), 3)
        dosepf = round(float(acqDict['DosePerFrame']), 2)
        px = round(float(acqDict['PixelSpacing']), 4)

        self.name.setText(SCOPE_DICT[scopeID][0])
        self.kv.setText(acqDict['Voltage'])
        self.cs.setText(acqDict['Cs'])
        self.px.setText(str(px))

        vpp = acqDict['PhasePlateUsed']
        if vpp in ['true', 'True', True]:
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
        self.px = self.addLine(50, 5, Qt.AlignRight)

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
        self.dosepf = self.addLine(50, 5, Qt.AlignRight)

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

    def onFinish(self):
        # Finish pressed, we need to update all editable vars
        App.model.acqDict['User'] = App.model.getUser()
        App.model.acqDict['DosePerFrame'] = self.dosepf.text()
        App.model.acqDict['PixelSpacing'] = self.px.text()
        App.model.acqDict['PhasePlateUsed'] = self.vpp.isChecked()

        if DEBUG:
            print("\nFinal parameters:\n")
            for k, v in sorted(App.model.acqDict.items()):
                print(k, v)
            print('\n')

        if App.model.getPipeline() == 'Relion':
            setupRelion(App.model.acqDict)
        else:
            setupScipion(App.model.acqDict)

    def addLine(self, size, length, align):
        line = QLineEdit()
        line.setMinimumWidth(size)
        line.setMaximumWidth(size)
        line.setMaxLength(length)
        line.setAlignment(align)
        return line


def main():
    args = sys.argv
    help = "Usage: mdcatch [--watch]\nBy default starts a GUI, "\
           "use '--watch' for daemon mode. It will watch METADATA_PATH folder."
    if len(args) > 1:
        if args[1] in ['-h', '--help']:
            print(help)
        elif args[1] == '--watch':
            from .watcher import WatchDog
            watch = WatchDog()
            watch.start_daemon(METADATA_PATH)
        else:
            print("Unrecognized arguments.\n%s" % help)
    else:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        wizard = App()
        wizard.show()
        sys.exit(app.exec_())
