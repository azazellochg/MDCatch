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
import shutil
import subprocess
import json

from .utils.misc import precalculateVars, getPrjName
from .config import DEBUG, JSON_TEMPLATE, SCHEDULE_PATH, PATTERN_SEM_MOVIES


def setupRelion(paramDict):
    """ Prepare and launch Relion 3.1 schedules. """
    bin, gain, defect, group_frames = precalculateVars(paramDict)
    mapDict = {'Cs': paramDict['Cs'],
               'dose_rate': paramDict['DosePerFrame'],
               'angpix': paramDict['PixelSpacing'],
               'voltage': paramDict['Voltage'],
               'motioncorr_bin': bin,
               'group_frames': group_frames,
               'is_VPP': paramDict['PhasePlateUsed'],
               'optics_group': paramDict['OpticalGroup'],
               'size_min': paramDict['PtclSizes'][0],
               'size_max': paramDict['PtclSizes'][1],
               }

    pickerSchedule = {'crYOLO': 'preprocess-cryolo',
                      'Topaz': 'preprocess-topaz',
                      'LogPicker': 'preprocess-logpicker'}
    preprocess_schd = pickerSchedule[paramDict['Picker']]

    if paramDict['PtclSizes'][0] != 0:
        mapDict.update({
            'box_size': paramDict['BoxSize'],
            'mask_diam_px': paramDict['MaskSize'],
            'mask_diam': int(paramDict['MaskSize']) * bin * float(paramDict['PixelSpacing']),
            'box_size_bin': paramDict['BoxSizeSmall'],
        })

    prjName = getPrjName(paramDict)
    prjPath = os.path.join(paramDict['PrjPath'], prjName)
    os.mkdir(prjPath)

    # Create links
    movieDir = os.path.join(prjPath, "Movies")
    if os.path.islink(movieDir):
        os.remove(movieDir)
    if os.path.exists(movieDir):
        raise FileExistsError('Destination %s already exists and is not a link' %
                              movieDir)

    if paramDict['Software'] == 'EPU':
        # EPU: Movies -> EPU session folder
        origPath1, origPath2 = paramDict['MoviePath'].split('/Images-Disc')
        mapDict['movies_wildcard'] = 'Movies/Images-Disc%s' % origPath2
    else:
        # SerialEM: Movies -> Raw path folder
        origPath1 = paramDict['MoviePath'].split(PATTERN_SEM_MOVIES)[0]
        mapDict['movies_wildcard'] = 'Movies/%s' % PATTERN_SEM_MOVIES

    if DEBUG:
        print("Params passed to Relion: ", mapDict)

    os.symlink(origPath1, movieDir)
    os.chdir(prjPath)
    # Create .gui_projectdir file, so that other users can open GUI
    with open('.gui_projectdir', 'w'):
        pass

    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            shutil.copyfile(i, os.path.basename(i))

    mapDict['gainref'] = os.path.basename(gain) or '""'
    mapDict['mtf_file'] = os.path.basename(paramDict['MTF'])
    mapDict['defect_file'] = os.path.basename(defect) or '""'

    try:
        subprocess.check_output(["which", "relion_scheduler"],
                                stderr=subprocess.DEVNULL)
        if not os.path.exists('Schedules'):
            shutil.copytree(SCHEDULE_PATH, os.getcwd() + '/Schedules')
    except subprocess.CalledProcessError:
        print("ERROR: relion command not found in PATH or Schedules not found!")
        exit(1)

    # setup ACL for uid
    uid = paramDict['User'][1]
    if uid:  # not zero
        cmdList = ["setfacl -R -m u:%s:rwX %s" % (uid, prjPath)]
        cmdList.append("setfacl -R -d -m u:%s:rwX %s" % (uid, prjPath))
        cmdList.append("setfacl -R -m m::rwx %s" % prjPath)
        cmdList.append("setfacl -R -d -m m::rwx %s" % prjPath)
        try:
            for cmd in cmdList:
                subprocess.check_output(cmd.split())
        except subprocess.CalledProcessError:
            print("Warning: setfacl command failed, ignoring..")

    # Set up scheduler vars
    cmdList = list()
    for key in mapDict:
        cmd = 'relion_scheduler --schedule %s --set_var %s --value %s' % (
            preprocess_schd, key, str(mapDict[key]))
        cmdList.append(cmd)

    cmdList.append('relion_scheduler --schedule class2d --set_var mask_diam --value %s' % mapDict.get('mask_diam', 0))

    for cmd in cmdList:
        print(cmd)
        proc = subprocess.check_output(cmd.split())

    # Run scheduler with Popen - without waiting for return
    cmd1 = 'relion_scheduler --schedule %s --run --pipeline_control Schedules/%s/ &' % (
        preprocess_schd, preprocess_schd)
    cmd2 = 'relion_scheduler --schedule class2d --run --pipeline_control Schedules/class2d/ &'

    with open("schedules_preprocess.log", "w") as fnLog1:
        print(cmd1)
        proc = subprocess.Popen(cmd1.split(), universal_newlines=True,
                                stdout=fnLog1, stderr=subprocess.STDOUT)
    with open("schedules_class2d.log", "w") as fnLog2:
        print(cmd2)
        proc = subprocess.Popen(cmd2.split(), universal_newlines=True,
                                stdout=fnLog2, stderr=subprocess.STDOUT)


def setupScipion(paramDict):
    """ Prepare and schedule Scipion 3 workflow.
    The default template will run import movies, relion motioncor,
    ctffind4, cryolo picking, extraction and summary monitor protocols.
    """
    prjName = getPrjName(paramDict)
    prjPath = os.path.join(paramDict['PrjPath'], prjName)
    os.mkdir(prjPath)
    os.chdir(prjPath)
    with open(JSON_TEMPLATE, 'r') as f:
        protocolsList = json.load(f)
    protNames = dict()

    for i, protDict in enumerate(protocolsList):
        protClassName = protDict['object.className']
        protNames[protClassName] = i

    bin, gain, defect, group_frames = precalculateVars(paramDict)
    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            shutil.copyfile(i, os.path.basename(i))

    # import movies
    importProt = protocolsList[protNames["ProtImportMovies"]]

    if paramDict['Software'] == 'EPU':
        # get EPU session folder
        origPath1, origPath2 = paramDict['MoviePath'].split('Images-Disc')
        importProt["filesPath"] = origPath1
        importProt["filesPattern"] = "Images-Disc%s" % origPath2
    else:
        # SerialEM
        importProt["filesPath"] = "%s/" % "/".join(paramDict['MoviePath'].split('/')[:-1])
        importProt["filesPattern"] = paramDict['MoviePath'].split('/')[-1]

    importProt["voltage"] = float(paramDict['Voltage'])
    importProt["sphericalAberration"] = float(paramDict['Cs'])
    importProt["samplingRate"] = float(paramDict['PixelSpacing'])
    importProt["dosePerFrame"] = float(paramDict['DosePerFrame'])
    importProt["gainFile"] = os.path.join(os.getcwd(), os.path.basename(gain)) if gain else ""

    # motioncorr
    movieProt = protocolsList[protNames["ProtRelionMotioncor"]]
    movieProt["binFactor"] = bin
    movieProt["groupFrames"] = group_frames
    movieProt["defectFile"] = os.path.join(os.getcwd(), os.path.basename(defect)) if defect else ""

    # ctffind
    ctfProt = protocolsList[protNames["CistemProtCTFFind"]]
    ctfProt["findPhaseShift"] = paramDict['PhasePlateUsed']

    jsonFn = "%s.json" % prjName
    with open(jsonFn, "w") as f:
        jsonStr = json.dumps(protocolsList, indent=4, separators=(',', ': '))
        f.write(jsonStr)

    try:
        subprocess.check_output(["which", "scipion3"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: scipion3 command not found in PATH!")
        exit(1)

    cmd = 'scipion3 python -m pyworkflow.project.scripts.create %s %s' % (
        prjName, os.path.abspath(jsonFn))
    proc = subprocess.run(cmd.split(), check=True)

    cmd2 = 'scipion3 python -m pyworkflow.project.scripts.schedule %s' % prjName
    proc2 = subprocess.Popen(cmd2.split(), universal_newlines=True)
