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

# Config variables
DEBUG = 1

# path to EPU session or folder with SerialEM mdoc files
METADATA_PATH = "/mnt/Krios1/Metadata"

# path where Relion projects are created
PROJECT_PATH = "/work/gsharov/tmp"

# Folder with Relion 3.1 schedules
SCHEDULE_PATH = "/home/gsharov/soft/Schedules"

# Scipion pre-processing template and output file
JSON_TEMPLATE = "template.json"
JSON_PATH = "workflow.json"

EPU_MOVIES_PATH = "Images-Disc*/GridSquare_*/Data/FoilHole_*.mrc"
PATTERN_XML = "FoilHole_[0-9]{6,8}_Data_[0-9]{6,8}_[0-9]{6,8}_[0-9]{8}_[0-9]{4,6}.xml$"
PATTERN_MDOC = ".{1,}\.tif\.mdoc$"
REGEX_MDOC_VAR = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

# default particle size for Relion LoG picker
part_size_short = 150
part_size_long = 180

# instrumentID: (Cs, scope name)
CS_DICT = {'3299': (2.7, 'Krios1'),
           '3413': (2.7, 'Krios2'),
           '3593': (2.7, 'Krios3')}

# path to MTF files for Relion (300 kV only)
MTF_DICT = {
    'Falcon3-count': '/home/gsharov/soft/MTFs/mtf_falcon3EC_300kV.star',
    'Falcon3-linear': '/home/gsharov/soft/MTFs/mtf_falcon2_300kV.star',
    'K2': '/home/gsharov/soft/MTFs/mtf_k2_300kV.star',
    'K3': '/home/gsharov/soft/MTFs/mtf_K3_300kv_nocds.star'
}

# path to raw movies folder depending on camera type
MOVIE_PATH_DICT = {
    'EF-CCD': '/mnt/%s/Data/K2/',
    'BM-Falcon': '/mnt/%s/Data/Falcon3/'
}

# SerialEM mdoc vars to parse
SERIALEM_PARAMS = [
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

    # vars below are added to mdoc using "AddToNextFrameStackMdoc key value"
    'OpticalGroup',
    'PhasePlateInserted',  # later renamed to PhasePlateUsed in parser.py
    'BeamTiltCompensation',
    'Beamtilt'
]

help_message = """Select the following folder:\n\n
   1) EPU: the EPU session folder on /mnt/Krios1/Metadata
   with Images-DiscX folder inside.\n
   2) SerialEM: the folder on /mnt/Krios1/Data/K2/ that
   contains tif and mdoc files.\n"""

error_message = """NO %s FILES WERE FOUND!\n\n
Please make sure that you selected correct folder:\n
   1) EPU: the EPU session folder on /mnt/Krios1/Metadata
   with Images-DiscX folder inside.\n
   2) SerialEM: the folder on /mnt/Krios1/Data/K2/ that
   contains tif and mdoc files.\n"""
