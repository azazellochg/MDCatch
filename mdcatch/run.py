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
                             QCheckBox, QApplication, QWizardPage,
                             QButtonGroup)
from PyQt5.QtCore import Qt
import sys

from .parser import Parser
from .schedule import *



class App(QWizard):
    model = Parser()

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = 'MDCatch v0.9.5 - metadata parser'
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
        self.mainLayout.addLayout(self.group3(), 1, 1)
        self.setLayout(self.mainLayout)

    def group1(self):
        vbox = QVBoxLayout()
        label1 = QLabel('Software')
        label2 = QLabel('Path')
        label3 = QLabel('Particle diameter (A)')
        label4 = QLabel('Launch pipeline in')
        label5 = QLabel('LMB username')

        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(label3)
        vbox.addWidget(label4)
        vbox.addWidget(label5)

        return vbox

    def group2(self):
        grid = QVBoxLayout()

        # software type
        hbox1 = QHBoxLayout()
        hbox1.setAlignment(Qt.AlignLeft)
        btgroup1 = QButtonGroup()

        b1 = self.addRadioButton("EPU", default=True)
        b2 = self.addRadioButton("SerialEM")

        btgroup1.addButton(b1)
        btgroup1.addButton(b2)
        btgroup1.buttonClicked.connect(lambda: self.updSoftware(btgroup1))
        hbox1.addWidget(b1)
        hbox1.addWidget(b2)
        grid.addLayout(hbox1)

        # path box
        hbox2 = QHBoxLayout()
        self.rawPath = QLineEdit()
        self.rawPath.setReadOnly(True)
        self.rawPath.setText(METADATA_PATH)

        b3 = QPushButton('Browse')
        b3.clicked.connect(lambda: self.browseSlot(self.rawPath))
        b4 = QPushButton('?')
        b4.setFixedSize(20, 25)
        b4.clicked.connect(self.helpSlot)

        hbox2.addWidget(self.rawPath)
        hbox2.addWidget(b3)
        hbox2.addWidget(b4)
        grid.addLayout(hbox2)

        # size box
        hbox3 = QHBoxLayout()
        labelSizeMin = QLabel('from')
        hbox3.addWidget(labelSizeMin)

        self.size_short = QSpinBox()
        self.size_short.setRange(10, 9999)
        self.size_short.setValue(part_size_short)
        self.size_short.setFixedSize(60, 25)
        hbox3.addWidget(self.size_short)

        labelSizeMax = QLabel('to')
        hbox3.addWidget(labelSizeMax)

        self.size_long = QSpinBox()
        self.size_long.setRange(10, 9999)
        self.size_long.setValue(part_size_long)
        self.size_long.setFixedSize(60, 25)
        hbox3.addWidget(self.size_long)
        hbox3.setAlignment(Qt.AlignLeft)
        grid.addLayout(hbox3)

        # pipeline
        hbox4 = QHBoxLayout()
        hbox4.setAlignment(Qt.AlignLeft)
        btgroup2 = QButtonGroup()

        b5 = self.addRadioButton("Relion", default=True)
        b6 = self.addRadioButton("Scipion")

        btgroup2.addButton(b5)
        btgroup2.addButton(b6)
        btgroup2.buttonClicked.connect(lambda: self.updPipeline(btgroup2))
        hbox4.addWidget(b5)
        hbox4.addWidget(b6)
        grid.addLayout(hbox4)

        # username
        hbox5 = QHBoxLayout()
        hbox5.setAlignment(Qt.AlignLeft)
        self.username = QLineEdit()
        self.username.setFixedSize(200, 25)

        self.b7 = QPushButton('Check!')
        self.b7.setFixedSize(70, 25)
        self.b7.clicked.connect(lambda: self.checkLogin(self.username.text()))

        hbox5.addWidget(self.username)
        hbox5.addWidget(self.b7)
        grid.addLayout(hbox5)

        return grid

    def group3(self):
        vbox = QVBoxLayout()
        self.label6 = QLabel('')
        self.label6.setVisible(False)

        vbox.addWidget(self.label6)

        return vbox

    def updSoftware(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.setSoftware(bt.text())

    def updPipeline(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.setPipeline(bt.text())

    def browseSlot(self, var):
        # called when a user press Browse
        folder = METADATA_PATH if var.text() is None else var.text()
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                folder,
                                                QFileDialog.ShowDirsOnly)
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

    def checkLogin(self, login):
        # match username with NIS database
        cmd = "/usr/bin/ypmatch %s passwd" % login
        try:
            res = subprocess.check_output(cmd.split())
        except subprocess.CalledProcessError:
            App.showDialog("ERROR", "Username %s not found!" % login)
            return False
        except FileNotFoundError:
            App.showDialog("ERROR", "Command %s not found!" % cmd.split()[0])
            return False

        res = str(res)
        uid, gid = res.split(':')[2], res.split(':')[3]
        self.label6.setVisible(True)
        self.label6.setStyleSheet('color: green')
        self.label6.setText('Check OK: UID=%s, GID=%s' % (uid, gid))
        App.model.setUser(login, uid, gid)
        return True

    def validatePage(self):
        # Next is pressed, returns True or False
        App.model.setSizes(self.size_short.text(), self.size_long.text())
        if App.model.getMdPath() is None:
            App.model.setMdPath(METADATA_PATH)

        # prevent Check button bypass
        usrchk = self.checkLogin(self.username.text())
        if not usrchk:
            return False

        if DEBUG:
            print("\n\nInput params: ",
                  [App.model.getSoftware(),
                   App.model.getMdPath(),
                   App.model.getUser(),
                   App.model.getSizes(),
                   App.model.getPipeline()])

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
        self.mainLayout.addWidget(self.group3(), 1, 0)
        self.mainLayout.addWidget(self.group4(), 1, 1)
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

        acqDict['PtclSizeShort'], acqDict['PtclSizeLong'] = App.model.getSizes()
        App.model.calcDose()
        App.model.calcBox()
        App.model.guessDataDir(fnList)

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
        self.px = self.addLine(50, 20, 5, Qt.AlignRight)

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
        self.dosepf = self.addLine(50, 20, 4, Qt.AlignRight)

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
        groupBox = QGroupBox("Recommended options")

        box = QLabel("Box size (px)")
        mask = QLabel("Mask size (px)")
        box2 = QLabel("Downscale to (px)")

        self.box = self.addLine(50, 20, 4, Qt.AlignRight)
        self.mask = self.addLine(50, 20, 4, Qt.AlignRight)
        self.box2 = self.addLine(50, 20, 4, Qt.AlignRight)

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

    def onFinish(self):
        # Finish pressed, we need to update all editable vars
        App.model.acqDict['User'] = App.model.getUser()
        App.model.acqDict['DosePerFrame'] = self.dosepf.text()
        App.model.acqDict['PixelSpacing'] = self.px.text()
        App.model.acqDict['PhasePlateUsed'] = self.vpp.isChecked()
        App.model.acqDict['NoCl2D'] = self.runCtf.isChecked()
        App.model.acqDict['BoxSize'] = self.box.text()
        App.model.acqDict['MaskSize'] = self.mask.text()
        App.model.acqDict['BoxSizeSmall'] = self.box2.text()

        if DEBUG:
            print("\nFinal parameters:\n")
            for k, v in sorted(App.model.acqDict.items()):
                print(k, v)
            print('\n')

        if App.model.getPipeline() == 'Relion':
            setupRelion(App.model.acqDict)
        else:
            setupScipion(App.model.acqDict)

    def addLine(self, sizex, sizey, length, align):
        line = QLineEdit()
        line.setFixedSize(sizex, sizey)
        line.setMaxLength(length)
        line.setAlignment(align)

        return line


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wizard = App()
    wizard.show()
    sys.exit(app.exec_())
