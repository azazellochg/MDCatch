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

#default_path = "/home/azazello/soft/MDCatch/examples"
#default_path = "/home/gsharov/soft/MDCatch/examples"
default_path = "/net/em-support3/"
schedule_dir = "/beegfs3/otfp/Gregory/test1_krios1/Schedules"
template_json = "template.json"
output_json = "workflow.json"

epu_movies_path = "Images-Disc*/GridSquare_*/Data/FoilHole_*.mrc"
reg_xml = "FoilHole_[0-9]{6,8}_Data_[0-9]{6,8}_[0-9]{6,8}_[0-9]{8}_[0-9]{4,6}.xml$"
reg_mdoc = ".{1,}\.tif\.mdoc$"
mdocPattern = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

matchDict = {"EPU": 'xml',
             "SerialEM": 'mdoc'}

# default particle diameter
part_size_short = 150
part_size_long = 180

# scopeID: Cs aberration and scope name
cs_dict = {
    '3299': (2.7, 'Krios1'),
    '3413': (2.7, 'Krios2'),
    '3593': (2.7, 'Krios3')
}

# path to MTF files for Relion (300 kV only)
mtf_dict = {
    'Falcon3-count': '/teraraid4/otfp/MTFs/mtf_falcon3EC_300kV.star',
    'Falcon3-linear': '/teraraid4/otfp/MTFs/mtf_falcon2_300kV.star',
    'K2': '/teraraid4/otfp/MTFs/mtf_k2_300kV.star',
    'K3': '/teraraid4/otfp/MTFs/mtf_K3_300kv_nocds.star'
}

# path to raw movies folder on Krios etc
pathDict = {
    'EF-CCD': '/net/cista1/%sGatan/',
    'BM-Falcon': '/net/cista1/%sFalcon/'
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
   1) EPU: the EPU session folder on /net/em-support3/
   with Images-DiscX folder inside.\n
   2) SerialEM: the folder on /net/cista1/ that
   contains tif and mdoc files.\n"""

error_message = """NO %s FILES WERE FOUND!\n\n
Please make sure that you selected correct folder:\n
   1) EPU: the EPU session folder on /net/em-support3/
   with Images-DiscX folder inside.\n
   2) SerialEM: the folder on /net/cista1/ that
   contains tif and mdoc files.\n"""
