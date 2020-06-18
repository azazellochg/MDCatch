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
from datetime import datetime

from .config import *


def setupRelion(paramDict):
    """ Prepare and launch Relion 3.1 schedules. """
    bin, gain, defect = precalculateVars(paramDict)
    mapDict = {'Cs': paramDict['Cs'],
               'dose_rate': paramDict['DosePerFrame'],
               'LOG_mind': paramDict['PtclSizeShort'],
               'LOG_maxd': paramDict['PtclSizeLong'],
               'boxsize_logpick': paramDict['BoxSizeSmall'],
               'mask_diam': paramDict['MaskSize'],
               'angpix': paramDict['PixelSpacing'],
               'voltage': paramDict['Voltage'],
               'motioncorr_bin': bin,
               'box_size': paramDict['BoxSize'],
               'do_until_ctf': paramDict['NoCl2D'],
               'is_VPP': paramDict['PhasePlateUsed'],
               'optics_group': paramDict['OpticalGroup']}

    prjName = getPrjName(paramDict)
    prjPath = os.path.join(paramDict['PrjPath'], prjName)
    os.mkdir(prjPath)

    # Create links
    movieDir = os.path.join(prjPath, "Movies")
    if os.path.islink(movieDir):
        os.remove(movieDir)
    if os.path.exists(movieDir):
        raise Exception('Destination %s already exists and is not a link' %
                        movieDir)

    if paramDict['Software'] == 'EPU':
        # EPU: Movies -> EPU session folder
        origPath1, origPath2 = paramDict['MoviePath'].split('/Images-Disc')
        mapDict['movies_wildcard'] = 'Movies/Images-Disc%s' % origPath2
    else:
        # SerialEM: Movies -> Raw path folder
        origPath1 = paramDict['MoviePath'].split('*.tif')[0]
        mapDict['movies_wildcard'] = 'Movies/*.tif'

    os.symlink(origPath1, movieDir)
    os.chdir(prjPath)
    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            os.symlink(i, os.path.basename(i))

    mapDict['gainref'] = os.path.basename(gain) or '""'
    mapDict['mtf_file'] = os.path.basename(paramDict['MTF'])
    mapDict['defect_file'] = os.path.basename(defect) or '""'

    try:
        subprocess.check_output(["which", "relion_scheduler"],
                                stderr=subprocess.DEVNULL)
        if not os.path.exists('Schedules'):
            shutil.copytree(SCHEDULE_PATH, os.getcwd() + '/Schedules')
    except subprocess.CalledProcessError:
        print("ERROR: Relion 3.1 not found in PATH or Schedules not found!")
        exit(1)

    # Run scheduler
    cmdList = list()
    for key in mapDict:
        cmd = 'relion_scheduler --schedule %s --set_var %s --value %s' % (
            'preprocess', key, str(mapDict[key]))
        cmdList.append(cmd)

    # mask for cl2d is in Angstroms
    diam = float(mapDict['angpix']) * float(mapDict['mask_diam'])
    cmdList.append('relion_scheduler --schedule class2d --set_var mask_diam --value %f' %
                   diam)

    for cmd in cmdList:
        if DEBUG:
            print(cmd)
        proc = subprocess.run(cmd.split(), check=True)

    # now use Popen - without waiting for return
    cmdList = list()
    cmdList.append('relion_scheduler --schedule preprocess --run &')

    if mapDict['do_until_ctf'] is False:
        cmdList.append('relion_scheduler --schedule class2d --run &')

    for cmd in cmdList:
        if DEBUG:
            print(cmd)
        proc = subprocess.Popen(cmd.split(), universal_newlines=True)


def setupScipion(paramDict):
    """ Prepare and schedule Scipion 3 workflow. """
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

    bin, gain, defect = precalculateVars(paramDict)

    # import movies
    importProt = protocolsList[protNames["ProtImportMovies"]]
    importProt["filesPath"] = "%s/" % "/".join(paramDict['MoviePath'].split('/')[:-1])
    if paramDict['MoviePath'].endswith('mrc'):
        importProt["filesPattern"] = "FoilHole*.mrc"
    else:
        importProt["filesPattern"] = "*.tif"
    importProt["voltage"] = float(paramDict['Voltage'])
    importProt["sphericalAberration"] = float(paramDict['Cs'])
    importProt["samplingRate"] = float(paramDict['PixelSpacing'])
    importProt["dosePerFrame"] = float(paramDict['DosePerFrame'])
    importProt["gainFile"] = gain

    # assign optics
    opticsProt = protocolsList[protNames["ProtRelionAssignOpticsGroup"]]
    opticsProt["opticsGroupName"] = paramDict['OpticalGroup']
    opticsProt["mtfFile"] = paramDict['MTF']

    # motioncorr
    movieProt = protocolsList[protNames["ProtMotionCorr"]]
    movieProt["binFactor"] = bin
    movieProt["defectFile"] = defect

    # gctf
    ctfProt = protocolsList[protNames["ProtGctf"]]
    ctfProt["doPhShEst"] = paramDict['PhasePlateUsed']

    # relion Log picker
    pickProt = protocolsList[protNames["ProtRelionAutopickLoG"]]
    pickProt["minDiameter"] = paramDict["PtclSizeShort"]
    pickProt["maxDiameter"] = paramDict["PtclSizeLong"]
    pickProt["boxSize"] = paramDict['BoxSize']

    # relion extract ptcls
    extrProt = protocolsList[protNames["ProtRelionExtractParticles"]]
    extrProt["boxSize"] = paramDict['BoxSize']
    extrProt["rescaledSize"] = paramDict['BoxSizeSmall']
    extrProt["backDiameter"] = paramDict['MaskSize']

    if os.path.exists(JSON_PATH):
        os.remove(JSON_PATH)
    with open(JSON_PATH, "w") as f:
        jsonStr = json.dumps(protocolsList, indent=4, separators=(',', ': '))
        f.write(jsonStr)

    try:
        subprocess.check_output(["which", "scipion"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: Scipion 3.0 not found in PATH!")
        exit(1)

    cmd = 'scipion python -m pyworkflow.project.scripts.create %s %s' % (
        prjName, os.path.abspath(JSON_PATH))
    proc = subprocess.run(cmd.split(), check=True)

    cmd2 = 'scipion python -m pyworkflow.project.scripts.schedule %s' % prjName
    proc2 = subprocess.Popen(cmd2.split(), universal_newlines=True)


def getPrjName(paramDict):
    """ Util func to get project name. """
    # project name = username_scope_date_time
    username, uid, gid = paramDict['User']
    scope = SCOPE_DICT[paramDict['MicroscopeID']][0]
    dt = datetime.now()
    dt = dt.strftime('%d-%m-%Y_%H%M')
    prjName = username + '_' + scope + '_' + dt

    return prjName


def precalculateVars(paramDict):
    """ Get binning, gain and defect files. """
    # set motioncor bin to 2 if using super-res data
    bin = 2.0 if paramDict['Mode'] == 'Super-resolution' else 1.0
    gain = '' if paramDict['GainReference'] == 'None' else paramDict['GainReference']
    defect = '' if paramDict['DefectFile'] == 'None' else paramDict['DefectFile']

    return bin, gain, defect
