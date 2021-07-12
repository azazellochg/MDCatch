#!/usr/bin/env python3
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

""" This script parses mdoc files from SerialEM. """

import re

from ..config import DEBUG, SERIALEM_PARAMS, SCOPE_DICT


REGEX_MDOC_VAR = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"


def parseMdoc(fn):
    acqDict = dict()
    # we assume SerialEM is only used for Gatan detectors
    acqDict['Detector'] = 'EF-CCD'

    with open(fn, 'r') as fname:
        regex = re.compile(REGEX_MDOC_VAR)

        for line in fname:
            match = regex.match(line)
            if match and match.groupdict()['var'] in SERIALEM_PARAMS:
                key = match.groupdict()['var']
                acqDict[key] = match.groupdict()['value'].strip()

    # rename a few keys to match EPU
    # T = SerialEM: Acquired on Titan Krios D3593
    match = re.search("D[0-9]{3,10}", acqDict['T'])
    if match:
        value = match.group().replace('D', '')
        acqDict['MicroscopeID'] = value
        acqDict.pop('T')
        if value in SCOPE_DICT:
            acqDict['Cs'] = str(SCOPE_DICT[value][1])
    else:
        print("ERROR: Could not detect MicroscopeID (D####) from mdoc!\n"
              "Make sure you have e.g. the following line in the mdoc:\n"
              "T = SerialEM: Acquired on Titan Krios D3593")
        exit(1)

    if 'ExposureDose' in acqDict:
        acqDict['Dose'] = acqDict.pop('ExposureDose')
    if 'TargetDefocus' in acqDict:
        acqDict['AppliedDefocus'] = acqDict.pop('TargetDefocus')
    if 'Binning' in acqDict:
        if acqDict['Binning'] == '0.5':
            acqDict['Mode'] = 'Super-resolution'
            acqDict['Binning'] = 1
        else:
            acqDict['Mode'] = 'Counting'
    if 'PhasePlateInserted' in acqDict:
        acqDict['PhasePlateUsed'] = acqDict.pop('PhasePlateInserted')

    if DEBUG:
        for k, v in sorted(acqDict.items()):
            print("%s = %s" % (k, v))

    return acqDict

