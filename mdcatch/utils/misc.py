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
from datetime import datetime

from ..config import SCOPE_DICT


def getUsername():
    """ Return username and uid. """
    return os.getlogin(), os.getuid()


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
    bin = 2.0 if (paramDict['Mode'] == 'Super-resolution' and paramDict['Binning'] == '1') else 1.0
    gain = '' if paramDict['GainReference'] == 'None' else paramDict['GainReference']
    defect = '' if paramDict['DefectFile'] == 'None' else paramDict['DefectFile']
    # group frames if fluence < 0.8 e/A^2/frame
    group_frames = 1
    dpf = float(paramDict['DosePerFrame'])
    if dpf < 0.8:
        group_frames += 1
        if group_frames * dpf < 0.8:
            group_frames += 1

    return bin, gain, defect, group_frames
