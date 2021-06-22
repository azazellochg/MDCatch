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

# set to 1 for more diagnostic output
DEBUG = 0

# some default vars
DEF_PIPELINE = "Relion"  # default pipeline: Relion or Scipion
DEF_SOFTWARE = "EPU"  # default software: EPU or SerialEM
DEF_PICKER = "Cryolo"  # default particle picker: Cryolo or Topaz or Log
DEF_PREFIX = "lmb_"  # found metadata folder name should start with this prefix
DEF_PARTICLE_SIZES = (150, 180)  # default min/max size in Angstroms
DEF_SYMMETRY = "C1"

# path to folder with EPU sessions or folder with SerialEM mdoc files
# in SerialEM case movies and mdocs are expected in the same folder
METADATA_PATH = "/mnt/MetaData/Krios1/EPU"

# path where Relion projects are created
PROJECT_PATH = "/cephfs"

# Folder with Relion 4 template schemes
SCHEMES_PATH = "/home/gsharov/soft/MDCatch-dev/mdcatch/Schemes"

# Scipion 3 pre-processing template
JSON_TEMPLATE = "/home/gsharov/soft/MDCatch-dev/mdcatch/template.json"

# main dictionary
# instrumentID: [name, Cs, TFS camera, Gatan camera]
SCOPE_DICT = {
    '3299': ['Krios1', 2.7, 'Falcon3', 'K3'],
    '3413': ['Krios2', 2.7, 'Falcon4', 'K2'],
    '3593': ['Krios3', 2.7, 'Falcon3', 'K3'],
    '9952833': ['Glacios', 2.7, 'Falcon3', None]
}

###############################################################################
# EPU params

# EPU-produced movie file patterns per each camera
EPU_MOVIES_DICT = {
    'Falcon3': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*_Fractions.mrc",
    'Falcon4': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*_EER.eer",
    'K2': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*.mrc",
    'K3': "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*_fractions.tiff"
}
# EPU-produced gain reference file patterns per each camera
GAIN_DICT = {
    'K2': "FoilHole_*_Data_*-gain-ref.MRC",
    'K3': "FoilHole_*_Data_*_gain.tiff",
    # Falcon 4 EER gain is not copied by EPU, so we need to provide a full path
    'Falcon4': "/home/gsharov/20210128_135200_EER_GainReference.gain"
}

# Which EPU session files to parse for metadata (default is xml)
# change the pattern below if you want to parse movie sums mrc instead
PATTERN_EPU = "Images-Disc*/GridSquare_*/Data/FoilHole_*_Data_*.xml"

# path to MTF files for Relion, %s is replaced by e.g. 300
# examples: Name-count, Name-linear or Name,
# camera names should match SCOPE_DICT
MTF_DICT = {
    'Falcon4-count': '/home/gsharov/soft/MTFs/mtf_falcon4EC_%skV.star',
    'Falcon3-count': '/home/gsharov/soft/MTFs/mtf_falcon3EC_%skV.star',
    'Falcon3-linear': '/home/gsharov/soft/MTFs/mtf_falcon2_%skV.star',
    'K2': '/home/gsharov/soft/MTFs/mtf_k2_%skV.star',
    'K3': '/home/gsharov/soft/MTFs/mtf_K3_%skv_nocds.star'
}

# path to raw movies folder depending on camera name
# example: /mnt/Data/Krios3/K3/
# scope and camera names should match SCOPE_DICT
MOVIE_PATH_DICT = {
    'EF-CCD': '/mnt/Data/%s/%s/',
    'BM-Falcon': '/mnt/Data/%s/%s/'
}

###############################################################################
# SerialEM params

# SerialEM-produced movies pattern
PATTERN_SEM_MOVIES = "*.tif"
# change the pattern below if you want to parse movie tif instead
PATTERN_SEM = "*.tif.mdoc"

# Which SerialEM mdoc variables to parse
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
    'GainReference'
]

# help message for path selection
help_message = """Select the following folder:\n\n
   For EPU: the EPU session folder on /mnt/MetaData/
   with Images-Disc folder inside.\n
   OR\n
   For SerialEM: the folder on /mnt/Data/ that
   contains tif movies and mdoc files.\n"""
