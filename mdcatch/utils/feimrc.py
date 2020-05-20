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

""" This script parses MRC 2014 FEI1 file header. """

import numpy as np
from struct import unpack

from mdcatch.utils.dtypes import mrc_tags, fei_tags

file = '/home/azazello/test/parser/Falcon3-sum.mrc'

with open(file, 'rb') as fin:
    fin.seek(0)
    header = fin.read(1024)
    map = header[208:212]
    machst = header[212:214]
    exttyp = header[104:108]

    if map != b'MAP ' or machst != b'DD':  # 0x44 0x44 is little endian
        raise Exception("Not a MRC file or not little endian byte order!")
    if exttyp != b'FEI1':
        print("No FEI1 extended header found!")
        exit(0)

    fin.seek(1024)
    md_size = unpack('<L', fin.read(4))[0]
    fin.seek(1024)
    ext_header = fin.read(md_size)

# parse main header
header_arr = np.frombuffer(header[:52], dtype=mrc_tags)
keys = header_arr.dtype.names
header_dict = [dict(zip(keys, value)) for value in header_arr][0]

header_dict["apix_x"] = header_dict["CELLA"]["X"] / header_dict["NX"]
header_dict["apix_y"] = header_dict["CELLA"]["Y"] / header_dict["NY"]

for k, v in sorted(header_dict.items()):
    print("%s = %s" % (k, v))

# parse extended header
ext_header_arr = np.frombuffer(ext_header, dtype=fei_tags)
keys = ext_header_arr.dtype.names
ext_header_dict = [dict(zip(keys, value)) for value in ext_header_arr][0]

for k, v in sorted(ext_header_dict.items()):
    print("%s = %s" % (k, str(v).lstrip("b'").rstrip("'")))
