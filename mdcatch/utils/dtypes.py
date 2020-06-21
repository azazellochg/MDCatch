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

import numpy as np

# See https://www.awaresystems.be/imaging/tiff/tifftags/baseline.html
# BigTIFF dtypes:
# 1: BYTE 1-byte uint
# 2: ASCII 8-byte
# 3: SHORT 2-byte uint
# 5: RATIONAL 2x 4-byte uint
# 16: LONG8 8-byte uint

bigtiff_tags = {
    # tag: (name, dtype)
    256: ("ImageWidth", 3),  # nx
    257: ("ImageLength", 3),  # ny
    258: ("BitsPerSample", 3),  # data type
    259: ("Compression", 3),
    262: ("PhotometricInterpretation", 3),  # The color space of the image data.
    270: ("ImageDescription", 2),
    273: ("StripOffsets", 16),
    277: ("SamplesPerPixel", 3),
    278: ("RowsPerStrip", 3),
    279: ("StripByteCounts", 16),
    282: ("XResolution", 5),  # The number of pixels per ResolutionUnit in the ImageWidth direction.
    283: ("YResolution", 5),  # The number of pixels per ResolutionUnit in the ImageLength direction.
    284: ("PlanarConfiguration", 3),
    296: ("ResolutionUnit", 3),  # The unit of measurement for XResolution and YResolution.
    306: ("DateTime", 2),  # YYYY:MM:DD HH:MM:SS
    339: ("SampleFormat", 3),
    340: ("SMinSampleValue", 1),  # min
    341: ("SMaxSampleValue", 1),  # max
}

# See https://www.ccpem.ac.uk/mrc_format/mrc2014.php
# The code below is taken from mrcfile/dtypes.py and modified,
# is distributed under a 3-Clause BSD licence
# Copyright (c) 2016, Science and Technology Facilities Council
mrc_tags = np.dtype([
    ('NX', 'i4'),
    ('NY', 'i4'),
    ('NZ', 'i4'),
    ('MODE', 'i4'),
    ('NXSTART', 'i4'),
    ('NYSTART', 'i4'),
    ('NZSTART', 'i4'),
    ('MX', 'i4'),
    ('MY', 'i4'),
    ('MZ', 'i4'),
    ('CELLA', [  # cell dimensions in Angstroms
        ('X', 'f4'),
        ('Y', 'f4'),
        ('Z', 'f4')
    ])
])

# See EPU user manual for FEI1 MRC header details
# For Timestamp definition see:
# https://docs.microsoft.com/en-us/cpp/atl-mfc-shared/reference/coledatetime-class?redirectedfrom=MSDN&view=vs-2019
fei_tags = np.dtype([
    ('Metadata size', 'i4'),  # bytes
    ('Metadata version', 'i4'),
    ('Bitmask 1', 'u4'),
    ('Timestamp', 'f8'),  # days from December 30, 1899, at midnight
    ('Microscope type', 'S16'),
    ('D-Number', 'S16'),
    ('Application', 'S16'),
    ('Application version', 'S16'),
    ('HT', 'f8'),  # Volt
    ('Dose', 'f8'),  # electrons/m^2
    ('Alpha tilt', 'f8'),  # deg.
    ('Beta tilt', 'f8'),  # deg.
    ('X-Stage', 'f8'),  # m
    ('Y-Stage', 'f8'),  # m
    ('Z-Stage', 'f8'),  # m
    ('Tilt axis angle', 'f8'),  # deg.
    ('Dual axis rotation', 'f8'),  # deg.
    ('Pixel size X', 'f8'),  # m
    ('Pixel size Y', 'f8'),  # m
    ('Unused space', 'S48'),
    ('Defocus', 'f8'),  # m
    ('STEM Defocus', 'f8'),  # m
    ('Applied defocus', 'f8'),  # m
    ('Instrument mode', 'i4'),
    ('Projection mode', 'i4'),
    ('Objective lens mode', 'S16'),
    ('High magnification mode', 'S16'),
    ('Probe mode', 'i4'),
    ('EFTEM On', '?'),
    ('Magnification', 'f8'),
    ('Bitmask 2', 'u4'),
    ('Camera length', 'f8'),  # m
    ('Spot index', 'i4'),
    ('Illuminated area', 'f8'),  # m
    ('Intensity', 'f8'),
    ('Convergence angle', 'f8'),  # degr.
    ('Illumination mode', 'S16'),
    ('Wide convergence angle range', '?'),
    ('Slit inserted', '?'),
    ('Slit width', 'f8'),  # eV
    ('Acceleration voltage offset', 'f8'),  # Volt
    ('Drift tube voltage', 'f8'),  # Volt
    ('Energy shift', 'f8'),  # eV
    ('Shift offset X', 'f8'),  # a.u.
    ('Shift offset Y', 'f8'),  # a.u.
    ('Shift X', 'f8'),  # a.u.
    ('Shift Y', 'f8'),  # a.u.
    ('Integration time', 'f8'),  # s
    ('Binning Width', 'i4'),
    ('Binning Height', 'i4'),
    ('Camera name', 'S16'),
    ('Readout area left', 'i4'),
    ('Readout area top', 'i4'),
    ('Readout area right', 'i4'),
    ('Readout area bottom', 'i4'),
    ('Ceta noise reduction', '?'),
    ('Ceta frames summed', 'i4'),
    ('Direct detector electron counting', '?'),
    ('Direct detector align frames', '?'),
    ('Camera param reserved 0', 'i4'),
    ('Camera param reserved 1', 'i4'),
    ('Camera param reserved 2', 'i4'),
    ('Camera param reserved 3', 'i4'),
    ('Bitmask 3', 'u4'),
    ('Camera param reserved 4', 'i4'),
    ('Camera param reserved 5', 'i4'),
    ('Camera param reserved 6', 'i4'),
    ('Camera param reserved 7', 'i4'),
    ('Camera param reserved 8', 'i4'),
    ('Camera param reserved 9', 'i4'),
    ('Phase Plate', '?'),
    ('STEM Detector name', 'S16'),
    ('Gain', 'f8'),
    ('Offset', 'f8'),
    ('STEM param reserved 0', 'i4'),
    ('STEM param reserved 1', 'i4'),
    ('STEM param reserved 2', 'i4'),
    ('STEM param reserved 3', 'i4'),
    ('STEM param reserved 4', 'i4'),
    ('Dwell time', 'f8'),  # s
    ('Frame time', 'f8'),  # s
    ('Scan size left', 'i4'),
    ('Scan size top', 'i4'),
    ('Scan size right', 'i4'),
    ('Scan size bottom', 'i4'),
    ('Full scan FOV X', 'f8'),  # m
    ('Full scan FOV Y', 'f8'),  # m
    ('Element', 'S16'),
    ('Energy interval lower', 'f8'),
    ('Energy interval higher', 'f8'),
    ('Method', 'i4'),
    ('Is dose fraction', '?'),
    ('Fraction number', 'i4'),
    ('Start frame', 'i4'),
    ('End frame', 'i4'),
    ('Input stack filename', 'S80'),
    ('Bitmask 4', 'u4'),
    ('Alpha tilt min', 'f8'),  # deg.
    ('Alpha tilt max', 'f8')  # deg.
])
