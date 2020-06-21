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
METADATA_PATH = "/home/azazello/soft/MDCatch/mdcatch/Metadata-examples"

# path where Relion projects are created
PROJECT_PATH = "/work/gsharov/tmp"

# Folder with Relion 3.1 schedules
SCHEDULE_PATH = "/home/azazello/soft/MDCatch/mdcatch/Schedules"

# Scipion pre-processing template and output file
JSON_TEMPLATE = "/home/azazello/soft/MDCatch/mdcatch/template.json"
JSON_PATH = "workflow.json"

# EPU 2.6.1 patterns
EPU_MOVIES_PATH = "Images-Disc*/GridSquare_*/Data/FoilHole_*.mrc"
PATTERN_EPU = "FoilHole_[0-9]{6,8}_Data_[0-9]{6,8}_[0-9]{6,8}_[0-9]{8}_[0-9]{4,6}.(xml|mrc)$"
GAIN_DICT = {'K2': "FoilHole_[0-9]{6,8}_Data_[0-9]{6,8}_[0-9]{6,8}_[0-9]{8}_[0-9]{4,6}-gain-ref.MRC$",
             'K3': "FoilHole_[0-9]{6,8}_Data_[0-9]{6,8}_[0-9]{6,8}_[0-9]{8}_[0-9]{4,6}_gain.tiff$"
             }

# SerialEM patterns
PATTERN_MDOC = ".{1,}\.tif\.mdoc$"
REGEX_MDOC_VAR = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

# default particle size for Relion LoG picker
part_size_short = 150
part_size_long = 180

# instrumentID: [name, Cs, TFS camera, Gatan camera]
SCOPE_DICT = {'3299': ['Krios1', 2.7, 'Falcon3', 'K2'],
              '3413': ['Krios2', 2.7, 'Falcon3', 'K2'],
              '3593': ['Krios3', 2.7, 'Falcon3', 'K3'],
              '9952833': ['Glacios', 2.7, 'Falcon3', None]
              }

# path to MTF files for Relion (300 kV only)
# examples: Name-count, Name-linear or Name,
# where Name should match the camera name in SCOPE_DICT
MTF_DICT = {
    'Falcon3-count': '/home/gsharov/soft/MTFs/mtf_falcon3EC_300kV.star',
    'Falcon3-linear': '/home/gsharov/soft/MTFs/mtf_falcon2_300kV.star',
    'K2': '/home/gsharov/soft/MTFs/mtf_k2_300kV.star',
    'K3': '/home/gsharov/soft/MTFs/mtf_K3_300kv_nocds.star'
}

# path to raw movies folder depending on camera name
# example: /mnt/Krios1/Data/Falcon3/
MOVIE_PATH_DICT = {
    'EF-CCD': '/mnt/%s/Data/%s/',
    'BM-Falcon': '/mnt/%s/Data/%s/'
}

# SerialEM mdoc vars to parse
SERIALEM_PARAMS = [
    'T',  # Microscope ID
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

    # optional vars below can be added to mdoc using "AddToNextFrameStackMdoc key value"
    'OpticalGroup',
    'PhasePlateInserted',
    'BeamTiltCompensation',
    'Beamtilt'
]

# error message for path selection
help_message = """Select the following folder:\n\n
   1) EPU: the EPU session folder on /mnt/Krios1/Metadata
   with Images-DiscX folder inside.\n
   OR\n
   2) SerialEM: the folder on /mnt/Krios1/Data/K2/ that
   contains tif movies and mdoc files.\n"""
