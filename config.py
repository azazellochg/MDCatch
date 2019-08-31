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

# Config vars and dicts

DEBUG = 1

default_path = "/home/azazello/MEGA/application/acquisition_patterns"
#default_path = "/home/gsharov/MEGAsync/application/acquisition_patterns"
#default_path = "/net/em-support3/Krios1/Gregory"
schedule_dir = "Schedules"
template_json = "template.json"
output_json = "workflow.json"

epu_movies_path = "Images-Disc*/GridSquare_*/Data/FoilHole_*.mrc"
reg_xml = "FoilHole_[0-9]{7,8}_Data_[0-9]{7,8}_[0-9]{7,8}_[0-9]{8}_[0-9]{4,6}.xml"
reg_mdoc = ".{1,}\.tif\.mdoc"
mdocPattern = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

matchDict = {"EPU": 'xml',
             "SerialEM": 'mdoc'}

# default particle diameter (has to be a string)
part_size = '200'

# scopeID: Cs aberration and scope name
cs_dict = {
    '3299': (2.7, 'Krios1'),
    '3413': (2.7, 'Krios2'),
    '3593': (2.7, 'Krios3'),
    '316': (2.25, 'Polara1'),
    '304': (2.25, 'Polara2'),
    '2366': (2.0, 'F20')
}

# path to MTF files for Relion (300 kV only)
mtf_dict = {
    'Falcon3-count': '/beegfs3/otfp/MTFs/mtf_falcon3EC_300kV.star',
    'Falcon3-linear': '/beegfs3/otfp/MTFs/mtf_falcon2_300kV.star',
    'K2': '/beegfs3/otfp/MTFs/mtf_k2_300kV.star',
    'K3': '/beegfs3/otfp/MTFs/mtf_K3_300kv_nocds.star'
}

# path to raw movies folder on Krios etc
pathDict = {
    'EF-CCD': '/net/cista1/%sGatan/',
    'BM-Falcon': '/net/cista1/%sFalcon/',
    'Polara1': '/net/cista1/Polara1/',
}

# SerialEM mdoc params to parse
paramsList = [
    'T',  # Microscope ID
    #'TiltAngle',
    'Voltage',
    'Magnification',
    'ExposureDose',
    'PixelSpacing',
    'ExposureTime',
    'Binning',
    'TargetDefocus',
    'NumSubFrames',
    #'DateTime',
    'DefectFile',
    'GainReference',

    # params below are added to mdoc using "AddToNextFrameStackMdoc key value"
    'OpticalGroup',
    'PhasePlateInserted',  # later renamed to PhasePlateUsed in parser.py
    'BeamTiltCompensation',
    'Beamtilt'
]

help_message = """Select the following folder:\n\n
   1) For EPU session it will be the folder on 
/net/em-support3/ with Images-DiscX folder inside.\n
   2) For SerialEM session it will be the folder 
on /net/cista1/ that contains tif and mdoc files inside.\n"""

error_message = """NO %s FILES WERE FOUND!\n\n
Please make sure that you selected correct folder:\n
   1) For EPU session it will be the folder on 
/net/em-support3/ with Images-DiscX folder inside.\n
   2) For SerialEM session it will be the folder 
on /net/cista1/ that contains tif and mdoc files inside.\n"""
