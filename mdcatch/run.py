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

from . import __version__
from .config import *
from .utils.misc import getUsername
from .parser import Parser
from .schedule import setupRelion, setupScipion


class App(QWizard):
    """ Main class that runs the GUI. """
    model = Parser()

    def __init__(self, parent=None):
        super(App, self).__init__(parent, flags=Qt.WindowFlags())
        self.title = 'MDCatch v%s - metadata parser' % __version__
        self.width = 640
        self.height = 320
        self.initUI()

    def initUI(self):
        """ Initialize QWizard with two pages. """
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
        """ Dialog message with a warning or an error. """
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
    """ Page 1 with user input params. """
    def __init__(self, parent=None):
        super(Page1, self).__init__(parent)
        self.setSubTitle("Input parameters")
        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(self.group1(), 0, 0)
        self.mainLayout.addLayout(self.group2(), 0, 1)
        self.setLayout(self.mainLayout)

    def group1(self):
        """ Label widgets at row 0, col 0. """
        vbox = QVBoxLayout()
        label_soft = QLabel('Software')
        label_path = QLabel('Path')
        label_pipeline = QLabel('Run pipeline in')
        label_picker = QLabel('Particle picker')
        label_model = QLabel('Trained model for picking')
        label_mode = QLabel('Data processing type')
        self.label_diam = QLabel('Particle size (A)')
        self.label_sym = QLabel('Symmetry')
        self.label_filament_width = QLabel('Filament width (A)')
        self.label_filament_width.setVisible(False)

        vbox.addWidget(label_soft, alignment=Qt.Alignment())
        vbox.addWidget(label_path, alignment=Qt.Alignment())
        vbox.addWidget(label_pipeline, alignment=Qt.Alignment())
        vbox.addWidget(label_picker, alignment=Qt.Alignment())
        vbox.addWidget(label_model, alignment=Qt.Alignment())
        vbox.addWidget(label_mode, alignment=Qt.Alignment())
        vbox.addWidget(self.label_diam, alignment=Qt.Alignment())
        vbox.addWidget(self.label_sym, alignment=Qt.Alignment())
        vbox.addWidget(self.label_filament_width, alignment=Qt.Alignment())

        return vbox

    def group2(self):
        """ Actual input widgets at row 0, col 1. """
        grid = QVBoxLayout()

        # software type
        hbox_soft = QHBoxLayout()
        hbox_soft.setAlignment(Qt.AlignLeft)
        btgroup_soft = QButtonGroup()

        button_epu = self.addRadioButton("EPU", default=DEF_SOFTWARE == "EPU")
        button_sem = self.addRadioButton("SerialEM", default=DEF_SOFTWARE == "SerialEM")

        btgroup_soft.addButton(button_epu)
        btgroup_soft.addButton(button_sem)
        btgroup_soft.buttonClicked.connect(lambda: self.updSoftware(btgroup_soft))
        hbox_soft.addWidget(button_epu, alignment=Qt.Alignment())
        hbox_soft.addWidget(button_sem, alignment=Qt.Alignment())
        grid.addLayout(hbox_soft)

        # path box
        hbox_path = QHBoxLayout()
        self.rawPath = QLineEdit()
        self.rawPath.setMinimumWidth(300)
        self.rawPath.setReadOnly(True)
        self.rawPath.setText(METADATA_PATH)
        self.rawPath.setToolTip(help_message)

        button_browse = QPushButton('Browse')
        button_browse.setToolTip(help_message)
        button_browse.clicked.connect(lambda: self.browseFolderSlot(self.rawPath))

        hbox_path.addWidget(self.rawPath, alignment=Qt.Alignment())
        hbox_path.addWidget(button_browse, alignment=Qt.Alignment())
        grid.addLayout(hbox_path)

        # pipeline
        hbox_pipeline = QHBoxLayout()
        hbox_pipeline.setAlignment(Qt.AlignLeft)
        btgroup_pipeline = QButtonGroup()

        button_relion = self.addRadioButton("Relion", default=DEF_PIPELINE == "Relion")
        button_scipion = self.addRadioButton("Scipion", default=DEF_PIPELINE == "Scipion")

        btgroup_pipeline.addButton(button_relion)
        btgroup_pipeline.addButton(button_scipion)
        btgroup_pipeline.buttonClicked.connect(lambda: self.updPipeline(btgroup_pipeline))
        hbox_pipeline.addWidget(button_relion, alignment=Qt.Alignment())
        hbox_pipeline.addWidget(button_scipion, alignment=Qt.Alignment())
        grid.addLayout(hbox_pipeline)

        # particle picker
        hbox_picker = QHBoxLayout()
        hbox_picker.setAlignment(Qt.AlignLeft)
        btgroup_picker = QButtonGroup()

        self.button_cryolo = self.addRadioButton("Cryolo", default=DEF_PICKER == "Cryolo")
        self.button_topaz = self.addRadioButton("Topaz", default=DEF_PICKER == "Topaz")
        self.button_log = self.addRadioButton("Log", default=DEF_PICKER == "Log")
        btgroup_picker.addButton(self.button_cryolo)
        btgroup_picker.addButton(self.button_topaz)
        btgroup_picker.addButton(self.button_log)
        btgroup_picker.buttonClicked.connect(lambda: self.updPicker(btgroup_picker))
        hbox_picker.addWidget(self.button_cryolo, alignment=Qt.Alignment())
        hbox_picker.addWidget(self.button_topaz, alignment=Qt.Alignment())
        hbox_picker.addWidget(self.button_log, alignment=Qt.Alignment())
        grid.addLayout(hbox_picker)

        # picker model box
        hbox_model = QHBoxLayout()
        self.modelPath = QLineEdit()
        self.modelPath.setMinimumWidth(300)
        self.modelPath.setReadOnly(True)
        self.modelPath.setToolTip(help_message2)

        button_browse = QPushButton('Browse')
        button_browse.setToolTip(help_message2)
        button_browse.clicked.connect(lambda: self.browseFileSlot(self.modelPath))

        hbox_model.addWidget(self.modelPath, alignment=Qt.Alignment())
        hbox_model.addWidget(button_browse, alignment=Qt.Alignment())
        grid.addLayout(hbox_model)

        # mode
        hbox_mode = QHBoxLayout()
        hbox_mode.setAlignment(Qt.AlignLeft)
        btgroup_mode = QButtonGroup()

        self.button_spa = self.addRadioButton("SPA", default=True)
        self.button_helical = self.addRadioButton("Helical", default=False)

        btgroup_mode.addButton(self.button_spa)
        btgroup_mode.addButton(self.button_helical)
        btgroup_mode.buttonClicked.connect(lambda: self.updMode(btgroup_mode))
        hbox_mode.addWidget(self.button_spa, alignment=Qt.Alignment())
        hbox_mode.addWidget(self.button_helical, alignment=Qt.Alignment())
        grid.addLayout(hbox_mode)

        # size box
        hbox_diam = QHBoxLayout()
        self.spbox_diam = QSpinBox()
        self.spbox_diam.setRange(10, 9999)
        self.spbox_diam.setValue(DEF_PARTICLE_SIZE)
        self.spbox_diam.setFixedSize(60, 25)
        hbox_diam.addWidget(self.spbox_diam)
        hbox_diam.setAlignment(Qt.AlignLeft)
        grid.addLayout(hbox_diam)

        # symmetry box
        hbox_sym = QHBoxLayout()
        self.symm = QLineEdit()
        self.symm.setMinimumWidth(60)
        self.symm.setMaximumWidth(60)
        self.symm.setText(DEF_SYMMETRY)
        hbox_sym.addWidget(self.symm, alignment=Qt.AlignLeft)
        grid.addLayout(hbox_sym)

        return grid

    def updSoftware(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.software = bt.text()

    def updPipeline(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.pipeline = bt.text()

    def updPicker(self, btgroup):
        bt = btgroup.checkedButton()
        App.model.picker = bt.text()

    def updMode(self, btgroup):
        bt = btgroup.checkedButton()
        btValue = bt.text()
        App.model.mode = btValue

        self.label_diam.setVisible(btValue == 'SPA')
        self.label_sym.setVisible(btValue == 'SPA')
        self.symm.setVisible(btValue == 'SPA')
        self.label_filament_width.setVisible(btValue == 'Helical')

    def browseFolderSlot(self, var):
        """ Called when "Browse" is pressed. """
        folder = METADATA_PATH if var.text() is None else var.text()
        path = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                folder,
                                                options=QFileDialog.ShowDirsOnly)
        if path:
            self.refreshPath(path)

    def browseFileSlot(self, var):
        """ Called when "Browse" is pressed. """
        file = "" if var.text() is None else var.text()
        path = QFileDialog.getOpenFileName(self, "Select model file",
                                           file,
                                           filter="Pretrained picking model (*.h5 *.sav)")
        if path:
            self.refreshModel(path[0])

    def refreshPath(self, path):
        """ Update line widget with selected path. """
        App.model.mdPath = path
        self.rawPath.setText(App.model.mdPath)

    def refreshModel(self, path):
        """ Update line widget with selected path. """
        App.model.pickerModel = path
        self.modelPath.setText(App.model.pickerModel)

    def validatePage(self):
        """ Executed when Next is pressed.
        Returns True or False. """
        App.model.size = self.spbox_diam.value()

        if App.model.mode == 'SPA':
            App.model.symmetry = self.symm.text()
        else:  # helical
            if App.model.picker != 'Cryolo':
                App.showDialog("ERROR", "Only crYOLO picker is supported for helical mode")
                return False
            if App.model.pickerModel is None:
                App.showDialog("ERROR", "Helical picking requires a pre-trained crYOLO model")
                return False

        if App.model.mdPath is None:
            App.model.mdPath = METADATA_PATH

        username, uid = getUsername()
        App.model.user = (username, uid)

        if DEBUG:
            print("\n\nInput params: ")
            for k, v in sorted(App.model.__dict__.items()):
                print(k, v)

        prog = App.model.software
        fnList = App.model.guessFn(prog)

        if fnList is None:
            App.showDialog("ERROR", "No matching files found!\n\n" + help_message)
            return False
        else:
            print("\nFile found: %s\n" % fnList)
            App.model.fn = fnList
            return True

    def reset(self):
        """ Executed when "Back" is pressed. """
        App.model.acqDict.clear()
        App.model.__init__()
        # keep the old path until updated
        App.model.mdPath = self.rawPath.text()
        App.model.pickerModel = self.modelPath.text()

    def addRadioButton(self, choice, default=False):
        """ Util func to add QRadioButton widget. """
        rb = QRadioButton(choice)
        if default:
            rb.setChecked(True)

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        rb.setSizePolicy(sizePolicy)
        return rb


class Page2(QWizardPage):
    """ Page 2 with parsed results. """
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.group1(), 0, 0)
        self.mainLayout.addWidget(self.group2(), 0, 1)
        self.setLayout(self.mainLayout)

    def initializePage(self):
        # executed before showing page 2
        acqDict = App.model.acqDict
        prog = App.model.software
        fnList = App.model.fn

        App.model.parseMetadata(fnList)

        self.addPtclSizeWidgets(acqDict)
        App.model.calcDose()
        App.model.guessDataDir()

        msg = f"Found the following metadata from {prog} session: {App.model.mdPath.split('/')[-1]}"
        if 'Warning' in acqDict:
            msg += "\n%s" % acqDict['Warning']
        self.setSubTitle(msg)

        scopeID = acqDict['MicroscopeID']
        time = round(float(acqDict['ExposureTime']), 3)
        dosepf = round(float(acqDict['DosePerFrame']), 3)
        px = round(float(acqDict['PixelSpacing']), 4)

        self.scope_name.setText(SCOPE_DICT[scopeID][0])
        self.kv.setText(acqDict['Voltage'])
        self.cs.setText(acqDict['Cs'])
        self.px.setText(str(px))

        vpp = acqDict['PhasePlateUsed']
        if vpp in ['true', 'True', True]:
            self.vpp.setChecked(True)
        else:
            self.vpp.setChecked(False)

        self.camera_name.setText(acqDict['Detector'])
        self.mode.setText("%s, bin %s" % (acqDict['Mode'], acqDict['Binning']))
        self.time.setText(str(time))
        self.frames.setText(acqDict['NumSubFrames'])
        self.dosepf.setText(str(dosepf))
        self.gain.setText(os.path.basename(acqDict['GainReference']))
        self.defects.setText(os.path.basename(acqDict['DefectFile']))

    def group1(self):
        """ Widgets at row 0, col 0. """
        groupBox = QGroupBox("Microscope")
        name = QLabel("Name")
        kv = QLabel("Voltage (kV)")
        cs = QLabel("Cs (mm)")
        vpp = QLabel("Phase plate")
        px = QLabel("Pixel size (A)")

        self.scope_name = QLabel()
        self.kv = QLabel()
        self.cs = QLabel()
        self.vpp = QCheckBox()
        self.px = self.addLine(50, 5, Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([name, kv, cs, px, vpp]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.scope_name, self.kv,
                                 self.cs, self.px, self.vpp]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)
        return groupBox

    def group2(self):
        """ Widgets at row 0, col 1. """
        groupBox = QGroupBox("Detector")
        name = QLabel("Name")
        mode = QLabel("Mode")
        time = QLabel("Exposure time (s)")
        frames = QLabel("Frames")
        dosepf = QLabel("Fluence per frame (e/A²)")
        gain = QLabel("Gain reference")
        defects = QLabel("Defects file")

        self.camera_name = QLabel()
        self.mode = QLabel()
        self.time = QLabel()
        self.frames = QLabel()
        self.gain = QLabel()
        self.defects = QLabel()
        self.dosepf = self.addLine(50, 5, Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([name, mode, time, frames,
                                 dosepf, gain, defects]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.camera_name, self.mode,
                                 self.time, self.frames,
                                 self.dosepf, self.gain,
                                 self.defects]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)
        return groupBox

    def group3(self):
        """ Widgets at row 1, col 0. """
        groupBox = QGroupBox("Recommended options")

        tube = QLabel("Tube diameter (A)")
        tube.setVisible(App.model.mode == 'Helical')
        box = QLabel("Box size (px)")
        mask = QLabel("Mask size (px)")
        box2 = QLabel("Downscale to (px)")

        self.tube = self.addLine(50, 4, Qt.AlignRight)
        self.tube.setVisible(App.model.mode == 'Helical')
        self.box = self.addLine(50, 4, Qt.AlignRight)
        self.mask = self.addLine(50, 4, Qt.AlignRight)
        self.box_bin = self.addLine(50, 4, Qt.AlignRight)

        vbox = QGridLayout()
        for num, i in enumerate([tube, box, mask, box2]):
            vbox.addWidget(i, num, 0)

        for num, i in enumerate([self.tube, self.box, self.mask, self.box_bin]):
            vbox.addWidget(i, num, 1)

        groupBox.setLayout(vbox)

        return groupBox

    def addPtclSizeWidgets(self, acqDict):
        """ Add particle size widgets. """
        size = App.model.size
        acqDict['PtclSize'] = size
        App.model.calcBox()
        self.mainLayout.addWidget(self.group3(), 1, 0)

        self.box.setText(acqDict['BoxSize'])
        self.mask.setText(acqDict['MaskSize'])
        self.box_bin.setText(acqDict['BoxSizeSmall'])

        if App.model.mode == 'Helical':
            self.tube.setText(acqDict['TubeDiam'])

    def onFinish(self):
        """ Finish is pressed, we need to update all editable vars. """
        App.model.acqDict.update({
            'User': App.model.user,
            'DosePerFrame': self.dosepf.text(),
            'PixelSpacing': self.px.text(),
            'PhasePlateUsed': self.vpp.isChecked(),
            'BoxSize': self.box.text(),
            'MaskSize': self.mask.text(),
            'BoxSizeSmall': self.box_bin.text(),
            'Picker': App.model.picker,
            'Symmetry': App.model.symmetry
        })

        if App.model.mode == 'Helical':
            App.model.acqDict.update({
                'TubeDiam': self.tube.text()
            })

        print("\nFinal parameters:\n")
        for k, v in sorted(App.model.acqDict.items()):
            print(k, v)
        print('\n')

        if App.model.pipeline == 'Relion':
            setupRelion(App.model.acqDict)
        else:
            setupScipion(App.model.acqDict)

    def addLine(self, size, length, align):
        """ Util func to add LineEdit widget. """
        line = QLineEdit()
        line.setMinimumWidth(size)
        line.setMaximumWidth(size)
        line.setMaxLength(length)
        line.setAlignment(align)
        return line


def main():
    """ Create GUI app. """
    args = sys.argv
    help = "Usage: mdcatch"
    if len(args) > 1:
        if args[1] in ['-h', '--help']:
            print(help)
        else:
            print("Unrecognized arguments.\n%s" % help)
    else:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        wizard = App()
        wizard.show()
        sys.exit(app.exec_())
