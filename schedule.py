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
import subprocess
import json
from datetime import datetime

from config import *


def precalculateVars(paramDict):
    # set motioncor bin to 2 if using super-res data
    bin = 2.0 if paramDict['Mode'] == 'Super-resolution' else 1.0
    vpp = True if paramDict['PhasePlateUsed'] in ['true', 'True'] else False
    gain = '' if paramDict['GainReference'] == 'None' else paramDict['GainReference']
    defect = '' if paramDict['DefectFile'] == 'None' else paramDict['DefectFile']

    return bin, vpp, gain, defect


def setupRelion(paramDict):
    fnDir = os.path.join(schedule_dir, 'preprocess')
    bin, vpp, gain, defect = precalculateVars(paramDict)
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
               'is_VPP': vpp,
               'gainref': gain,
               'movies_wildcard': '"%s"' % paramDict['MoviePath'],
               'mtf_file': paramDict['MTF'],
               'optics_group': paramDict['OpticalGroup']}

    cmdList = list()

    # Relion checks
    if not os.path.exists(fnDir):
        print("ERROR: Schedules folder not found, you can't launch Relion!")
        exit(1)

    try:
        subprocess.check_output(["which", "relion_scheduler"],
                                stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: Relion not found in PATH!")
        exit(1)

    # Run scheduler
    for key in mapDict:
        cmd = 'relion_scheduler --schedule %s --set_var %s --value %s' % (
            fnDir, key, str(mapDict[key]))
        cmdList.append(cmd)
    cmdList.append('relion_scheduler --schedule %s --run &' % fnDir)

    if DEBUG:
        for cmd in cmdList:
            print(cmd)

    cmd = '\n'.join([line for line in cmdList])
    proc = subprocess.check_output(cmd, shell=True)
    proc.wait()


def setupScipion(paramDict):
    bin, vpp, gain, defect = precalculateVars(paramDict)
    f = open(template_json, 'r')
    protocolsList = json.load(f)
    protNames = dict()

    for i, protDict in enumerate(protocolsList):
        protClassName = protDict['object.className']
        protNames[protClassName] = i
    f.close()

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
    importProt["opticsGroup"] = paramDict['OpticalGroup']
    importProt["mtf"] = paramDict['MTF']

    movieProt = protocolsList[protNames["ProtMotionCorr"]]
    movieProt["binFactor"] = bin
    movieProt["defectFile"] = defect

    ctfProt = protocolsList[protNames["ProtGctf"]]
    ctfProt["doPhShEst"] = vpp

    if os.path.exists(output_json):
        os.remove(output_json)
    f = open(output_json, "w")
    jsonStr = json.dumps(protocolsList, indent=4, separators=(',', ': '))
    f.write(jsonStr)
    f.close()

    try:
        subprocess.check_output(["which", "scipion"],
                                stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: Scipion not found in PATH!")
        exit(1)

    # projectName = scopeName_date
    scope = cs_dict[paramDict['MicroscopeID']][1]
    dt = datetime.now()
    dt = dt.strftime('%d-%m-%Y')
    prjName = scope + '_' + dt

    cmd = 'scipion run python pyworkflow/project/scripts/create.py %s workflow.json' % prjName
    cmd += '\nscipion project %s &' % prjName
    proc = subprocess.check_output(cmd, shell=True)
    proc.wait()
