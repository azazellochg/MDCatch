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
from datetime import datetime

from ..config import (DEF_USER, SCOPE_DICT, DEF_PICKER,
                      TOPAZ_SIZE, LOGPICKER_SIZES)


def getUsername(mdPath):
    """ Return username and uid using NIS database. """
    mdFolder = os.path.basename(mdPath)
    try:
        username = mdFolder.split("_")[1]
    except IndexError:
        return DEF_USER

    cmd = "/usr/bin/ypmatch %s passwd" % username
    try:
        res = subprocess.check_output(cmd.split())
    except subprocess.CalledProcessError:
        print("Warning: username %s not found! Using defaults: " % username, DEF_USER)
        return DEF_USER
    except FileNotFoundError:
        print("Warning: command %s failed! Using defaults: " % cmd, DEF_USER)
        return DEF_USER
    else:
        uid = str(res).split(":")[2]
        return username, uid


def getPrjName(paramDict):
    """ Util func to get project name.
    Returns project name = username_scope_date_time
    """
    username, _ = paramDict['User']
    scope = SCOPE_DICT[paramDict['MicroscopeID']][0]
    dt = datetime.now()
    dt = dt.strftime('%d-%m-%Y_%H%M')
    prjName = username + '_' + scope + '_' + dt

    return prjName


def precalculateVars(paramDict):
    """ Returns binning, gain, defect files and frame grouping. """
    # set motioncor bin to 2 if using super-res data
    bin = 2.0 if paramDict['Mode'] == 'Super-resolution' else 1.0
    gain = '' if paramDict['GainReference'] == 'None' else paramDict['GainReference']
    defect = '' if paramDict['DefectFile'] == 'None' else paramDict['DefectFile']
    # group frames if dose rate < 0.8 e/A^2/frame
    group_frames = 1
    dpf = float(paramDict['DosePerFrame'])
    if dpf < 0.8:
        group_frames += 1
        if group_frames * dpf < 0.8:
            group_frames += 1

    return bin, gain, defect, group_frames


def setParticleSizes(model):
    """ Setup particle sizes when running in non-GUI mode. """
    if DEF_PICKER == 'Topaz':
        model.acqDict['PtclSizes'] = TOPAZ_SIZE, LOGPICKER_SIZES[1]
        model.calcBox(DEF_PICKER)
    elif DEF_PICKER == 'LogPicker':
        model.acqDict['PtclSizes'] = LOGPICKER_SIZES
        model.calcBox(DEF_PICKER)
    else:
        model.acqDict['PtclSizes'] = 0, LOGPICKER_SIZES[1]
