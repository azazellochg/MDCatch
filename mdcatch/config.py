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

# daemon mode vars
DEF_USER = ("gsharov", 26096)  # default name: (username, uid)
DEF_PIPELINE = "Relion"  # default pipeline: Relion or Scipion
DEF_SOFTWARE = "EPU"  # default software: EPU or SerialEM
DEF_PREFIX = "lmb_"  # found metadata folder name should start with this prefix

# path to EPU session or folder with SerialEM mdoc files
#METADATA_PATH = "/home/gsharov/soft/MDCatch/mdcatch/Metadata-examples"
#METADATA_PATH = "/mnt/MetaData/"
METADATA_PATH = "/home/azazello/soft/MDCatch/mdcatch/Metadata-examples/EPU/K3/VPP"

# path where Relion projects are created
PROJECT_PATH = "/cephfs"

# Folder with Relion 3.1 schedules
SCHEDULE_PATH = "/home/gsharov/soft/MDCatch/mdcatch/Schedules"

# Scipion pre-processing template and output file
JSON_TEMPLATE = "/home/gsharov/soft/MDCatch/mdcatch/template.json"
JSON_PATH = "workflow.json"

# main dictionary
# instrumentID: [name, Cs, TFS camera, Gatan camera]
SCOPE_DICT = {'3299': ['Krios1', 2.7, 'Falcon', 'K2'],
              '3413': ['Krios2', 2.7, 'Falcon', 'K2'],
              '3593': ['Krios3', 2.7, 'Falcon', 'K3'],
              '9952833': ['Glacios', 2.7, 'Falcon', None]
              }

###############################################################################
# EPU 2.4+ patterns
EPU_MOVIES_DICT = {'Falcon': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*_Fractions.mrc",
                   'K2': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*.mrc",
                   'K3': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*_fractions.tiff"
                   }
GAIN_DICT = {'K2': "FoilHole_*_Data_*-gain-ref.MRC",
             'K3': "FoilHole_*_Data_*_gain.tiff"
             }

# change the pattern below if you want to parse movie sums mrc instead
PATTERN_EPU = "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*.xml"

###############################################################################
# SerialEM patterns
PATTERN_MDOC = ".{1,}\.tif\.mdoc$"
REGEX_MDOC_VAR = "(?P<var>[a-zA-Z0-9]+?) = (?P<value>(.*))"

# path to MTF files for Relion (300 kV only)
# examples: Name-count, Name-linear or Name,
# camera names should match SCOPE_DICT
MTF_DICT = {
    'Falcon-count': '/home/gsharov/soft/MTFs/mtf_falcon3EC_300kV.star',
    'Falcon-linear': '/home/gsharov/soft/MTFs/mtf_falcon2_300kV.star',
    'K2': '/home/gsharov/soft/MTFs/mtf_k2_300kV.star',
    'K3': '/home/gsharov/soft/MTFs/mtf_K3_300kv_nocds.star'
}

# path to raw movies folder depending on camera name
# example: /mnt/Data/Krios3/K3/
# scope and camera names should match SCOPE_DICT
MOVIE_PATH_DICT = {
    'EF-CCD': '/mnt/Data/%s/%s/',
    'BM-Falcon': '/mnt/Data/%s/%s/'
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
    # 'DateTime',
    'DefectFile',
    'GainReference',
    # optional vars below can be added to mdoc using "AddToNextFrameStackMdoc key value"
    'OpticalGroup',
    'PhasePlateInserted',
    'BeamTiltCompensation',
    'Beamtilt'
]

# help message for path selection
help_message = """Select the following folder:\n\n
   For EPU: the EPU session folder on /mnt/MetaData/
   with Images-DiscX folder inside.\n
   OR\n
   For SerialEM: the folder on /mnt/Data/ that
   contains tif movies and mdoc files.\n"""
