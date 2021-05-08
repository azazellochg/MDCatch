#!/usr/bin/env python3

from mdcatch.schedule import setupRelion, setupScipion

paramDict = {
       #"AppliedDefocus": -1.5,
       #"BeamShiftX": -0.11633544415235519,
       #"BeamShiftY": -0.019380046054720879,
       "BeamSize": 1.0499999999999998,
       #"BeamTiltX": 0.00850762240588665,
       #"BeamTiltY": 0.0088164648041129112,
       "Cs": 2.7,
       "DefectFile": "None",
       "Detector": "K2",
       "Dose": 34.123202510617006,
       "DoseOnCamera": 0.5184268233337922,
       "DosePerFrame": 1.277,
       "EPUversion": "2.7.0.5806",
       "ExposureTime": 8,
       "GainReference": "/work/gsharov/Movies/gain.mrc",
       "GunLens": 6,
       "ImageShiftX": 0,
       "ImageShiftY": 0,
       "MTF": "/home/gsharov/soft/MTFs/mtf_k2_300kV.star",
       "Magnification": 75000,
       "MicroscopeID": "3299",
       "Mode": "Counting",
       "MoviePath": "/work/gsharov/Movies/Images-Disc1/GridSquare_15465465/Data/*tiff",
       "NumSubFrames": 24,
       "OpticalGroup": "opticsGroup1",
       "PhasePlateUsed": False,
       "PixelSpacing": 0.885,
       "PrjPath": "/cephfs",
       "PtclSizes": (150, 180),
       "BoxSize": 200,
       "BoxSizeSmall": 64,
       "MaskSize": 180,
       "Software": "EPU",
       "SpotSize": 10,
       "User": ('gsharov', 26096),
       "Voltage": 200,
}

setupRelion(paramDict)
#setupScipion(paramDict)

