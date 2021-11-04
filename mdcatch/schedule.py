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

import os
import shutil
import subprocess
import json

from .utils.misc import precalculateVars, getPrjName
from .config import JSON_TEMPLATE, SCHEMES_PATH, PATTERN_SEM_MOVIES, BATCH_SIZE


def setupRelion(paramDict):
    """ Prepare and launch Relion 4.0 schemes. """
    try:
        subprocess.check_output(["which", "relion_schemer"],
                                stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: Relion not found in PATH!")
        exit(1)

    bin, gain, defect, group_frames = precalculateVars(paramDict)
    mask_diam = int(int(paramDict['MaskSize']) * bin * float(paramDict['PixelSpacing']))
    mapDict = {
        'prep__do_at_most': BATCH_SIZE,
        'prep__ctffind__do_phaseshift': paramDict['PhasePlateUsed'],
        'prep__importmovies__Cs': paramDict['Cs'],
        'prep__importmovies__angpix': paramDict['PixelSpacing'],
        'prep__importmovies__kV': paramDict['Voltage'],
        'prep__importmovies__optics_group_name': '"%s"' % paramDict['OpticalGroup'],
        'prep__motioncorr__bin_factor': bin,
        'prep__motioncorr__dose_per_frame': paramDict['DosePerFrame'],
        'prep__motioncorr__group_frames': group_frames
    }

    picker = paramDict['Picker'].lower()
    if picker == 'cryolo':
        mapDict.update({
            'proc-cryolo__cryolo_model': paramDict['PickerModel'],
            'proc-cryolo__do_3d': True,
            'proc-cryolo__class2d__particle_diameter': mask_diam,
            'proc-cryolo__extract__bg_diameter': paramDict['MaskSize'],
            'proc-cryolo__extract__extract_size': paramDict['BoxSize'],
            'proc-cryolo__extract__rescale': paramDict['BoxSizeSmall'],
            'proc-cryolo__inimodel3d__particle_diameter': mask_diam,
            'proc-cryolo__inimodel3d__sym_name': '"%s"' % paramDict['Symmetry'],
            'proc-cryolo__autopick__param2_value': paramDict['BoxSize'],
            'proc-cryolo__refine3d__particle_diameter': mask_diam,
            'proc-cryolo__refine3d__sym_name': '"%s"' % paramDict['Symmetry'],
        })
        if 'TubeDiam' in paramDict:
            box_dist = int(int(paramDict['BoxSize']) * 0.1)  # 10% of the box
            mapDict.update({
                'proc-cryolo__do_3d': True,
                'proc-cryolo__autopick__param4_label': 'filament',
                'proc-cryolo__autopick__param5_label': 'bd',
                'proc-cryolo__autopick__param5_value': box_dist,
                'proc-cryolo__autopick__param6_label': 'mn',
                'proc-cryolo__autopick__param6_value': 1,
                'proc-cryolo__extract__do_cut_into_segments': False,
                'proc-cryolo__extract__do_extract_helical_tubes': False,
                'proc-cryolo__extract__do_extract_helix': True,
                'proc-cryolo__extract__helical_bimodal_angular_priors': True,
                'proc-cryolo__extract__helical_tube_outer_diameter': paramDict['TubeDiam'],
                'proc-cryolo__class2d__do_bimodal_psi': True,
                'proc-cryolo__class2d__do_helix': True,
                'proc-cryolo__class2d__helical_tube_outer_diameter': paramDict['TubeDiam'],
                'proc-cryolo__class2d__do_restrict_xoff': False,
                'proc-cryolo__class2d__range_psi': 6,
                'proc-cryolo__class2d__psi_sampling': 1,
                'proc-cryolo__class2d__other_args': '"--dont_check_norm"'
            })
    else:  # logpicker or topaz
        mapDict.update({
            'proc-topaz__do_log': 1 if picker == 'log' else 0,
            'proc-topaz__do_topaz': 1 if picker == 'topaz' else 0,
            'proc-topaz__topaz_model': paramDict['PickerModel'] or "",
            'proc-topaz__do_3d': True,
            'proc-topaz__class2d__particle_diameter': mask_diam,
            'proc-topaz__extract__bg_diameter': paramDict['MaskSize'],
            'proc-topaz__extract__extract_size': paramDict['BoxSize'],
            'proc-topaz__extract__rescale': paramDict['BoxSizeSmall'],
            'proc-topaz__inimodel3d__particle_diameter': mask_diam,
            'proc-topaz__inimodel3d__sym_name': '"%s"' % paramDict['Symmetry'],
            'proc-topaz__autopick__use_gpu': True if picker == 'topaz' else False,
            'proc-topaz__autopick__log_diam_min': int(paramDict['PtclSize'] * 0.8333),  # particle circularity
            'proc-topaz__autopick__log_diam_max': paramDict['PtclSize'],
            'proc-topaz__autopick__topaz_particle_diameter': paramDict['PtclSize'],
            'proc-topaz__refine3d__particle_diameter': mask_diam,
            'proc-topaz__refine3d__sym_name': '"%s"' % paramDict['Symmetry'],
        })

    if paramDict['Mode'] == "EER":
        eer_group = 1 // float(paramDict['DosePerFrame'])  # group to achieve 1 e/A^2/frame
        mapDict.update({
            'prep__motioncorr__bin_factor': 1,
            'prep__motioncorr__group_frames': 1,
            'prep__motioncorr__dose_per_frame': 1.0,
            'prep__motioncorr__eer_grouping': eer_group
        })

    prjName = getPrjName(paramDict)
    prjPath = os.path.join(paramDict['PrjPath'], prjName)
    os.mkdir(prjPath)

    # Create links
    movieDir = os.path.join(prjPath, "Movies")
    if os.path.islink(movieDir):
        os.remove(movieDir)
    if os.path.exists(movieDir):
        raise FileExistsError('Destination %s already exists and is not a link' %
                              movieDir)

    if paramDict['Software'] == 'EPU':
        # EPU: Movies -> EPU session folder
        origPath1, origPath2 = paramDict['MoviePath'].split('/Images-Disc')
        mapDict['prep__importmovies__fn_in_raw'] = '"Movies/Images-Disc%s"' % origPath2
    else:
        # SerialEM: Movies -> Raw path folder
        origPath1 = paramDict['MoviePath'].split(PATTERN_SEM_MOVIES)[0]
        mapDict['prep__importmovies__fn_in_raw'] = '"Movies/%s"' % PATTERN_SEM_MOVIES

    os.symlink(origPath1, movieDir)
    os.chdir(prjPath)
    # Create .gui_projectdir file, so that users can open GUI
    open('.gui_projectdir', 'w').close()
    # Create .gui_manualpickjob.star for easy picking results display
    starString = """

# version 30001

data_job

_rlnJobTypeLabel             ManualPick
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
    angpix         %s 
 black_val          0 
blue_value          0 
color_label rlnAutopickFigureOfMerit 
  diameter        %s 
  do_color         No 
do_fom_threshold         No 
  do_queue         No 
do_startend         No 
  fn_color         "" 
     fn_in         "" 
  highpass         -1 
   lowpass         20 
  micscale        0.2 
min_dedicated         24 
minimum_pick_fom          0 
other_args         "" 
      qsub       qsub 
qsubscript /home/gsharov/rc/relion-slurm.sh 
 queuename    openmpi 
 red_value          2 
sigma_contrast          3 
 white_val          0     
"""
    with open(".gui_manualpickjob.star", "w") as f:
        f.write(starString % (float(paramDict['PixelSpacing']) * bin,
                              paramDict['PtclSize']))

    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            shutil.copyfile(i, os.path.basename(i))

    if os.path.exists(gain):
        mapDict['prep__motioncorr__fn_gain_ref'] = '"%s"' % os.path.basename(gain)
    else:
        mapDict['prep__motioncorr__fn_gain_ref'] = ''

    if os.path.exists(paramDict['MTF']):
        mapDict['prep__importmovies__fn_mtf'] = '"%s"' % os.path.basename(paramDict['MTF'])
    else:
        mapDict['prep__importmovies__fn_mtf'] = ''

    if os.path.exists(defect):
        mapDict['prep__motioncorr__fn_defect'] = '"%s"' % os.path.basename(defect)
    else:
        mapDict['prep__motioncorr__fn_defect'] = ''

    if not os.path.exists('Schemes'):
        shutil.copytree(SCHEMES_PATH, os.getcwd() + '/Schemes')

    for fn in ['external_job_cryolo.py', 'external_job_cryolo_train.py']:
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), fn),
                    os.getcwd())

    # Save relion params in .py file
    with open("relion_it_options.py", 'w') as file:
        file.write("{\n")
        for k, v in mapDict.items():
            if v != '':
                if isinstance(v, str):
                    v = v.replace('"', '')
                file.write("'%s' : '%s',\n" % (k, v))
        file.write("}\n")

    # Save acquisition params
    with open("%s_session_params" % paramDict['Software'], "w") as fn:
        fn.write("Movies dir: %s\n\n" % origPath1)
        for k, v in sorted(paramDict.items()):
            fn.write("%s = %s\n" % (k, v))

    # Set up schemer vars
    cmdList = list()
    for key in mapDict:
        if mapDict[key] != '':
            opts = key.split("__")
            if key.count("__") == 2:  # job option
                jobstar = 'Schemes/' + opts[0] + '/' + opts[1] + '/job.star'
                cmd = 'relion_pipeliner --editJob %s --editOption %s --editValue %s' % (
                    jobstar, opts[2], mapDict[key])
            else:  # scheme option
                cmd = 'relion_schemer --scheme %s --set_var %s --value %s --original_value %s' % (
                    opts[0], opts[1], mapDict[key], mapDict[key])

            cmdList.append(cmd)

    for cmd in sorted(cmdList):
        print(cmd)
        os.system(cmd)

    # Run schemer
    sch_name = 'cryolo' if picker == 'cryolo' else 'topaz'
    cmdList = ['relion_schemer --scheme prep --reset &',
               'relion_schemer --scheme prep --run --pipeline_control Schemes/prep/ >> Schemes/prep/run.out 2>> Schemes/prep/run.err &',
               f'relion_schemer --scheme proc-{sch_name} --reset &',
               f'relion_schemer --scheme proc-{sch_name} --run --pipeline_control Schemes/proc-{sch_name}/ >> Schemes/proc-{sch_name}/run.out 2>> Schemes/proc-{sch_name}/run.err &']

    for cmd in cmdList:
        print(cmd)
        os.system(cmd)


def setupScipion(paramDict):
    """ Prepare and scheme Scipion 3 workflow.
    The default template will run import movies, relion motioncor,
    ctffind4, cryolo picking, extraction and summary monitor protocols.
    """
    try:
        subprocess.check_output(["which", "scipion3"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: scipion3 command not found in PATH!")
        exit(1)

    prjName = getPrjName(paramDict)
    cmd = "scipion3 printenv | grep SCIPION_USER_DATA | cut -d'=' -f2"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    scipionDir = os.path.abspath(out.decode().replace('"', '').replace('\n', ''))
    prjPath = scipionDir + "/projects/" + prjName

    with open(JSON_TEMPLATE, 'r') as f:
        protocolsList = json.load(f)
    protNames = dict()

    for i, protDict in enumerate(protocolsList):
        protClassName = protDict['object.className']
        protNames[protClassName] = i

    bin, gain, defect, group_frames = precalculateVars(paramDict)

    # import movies
    importProt = protocolsList[protNames["ProtImportMovies"]]

    if paramDict['Software'] == 'EPU':
        # get EPU session folder
        origPath1, origPath2 = paramDict['MoviePath'].split('Images-Disc')
        importProt["filesPath"] = origPath1
        importProt["filesPattern"] = "Images-Disc%s" % origPath2
    else:
        # SerialEM
        importProt["filesPath"] = "%s/" % "/".join(paramDict['MoviePath'].split('/')[:-1])
        importProt["filesPattern"] = paramDict['MoviePath'].split('/')[-1]

    importProt["voltage"] = float(paramDict['Voltage'])
    importProt["sphericalAberration"] = float(paramDict['Cs'])
    importProt["samplingRate"] = float(paramDict['PixelSpacing'])
    importProt["dosePerFrame"] = float(paramDict['DosePerFrame'])
    importProt["gainFile"] = (prjPath + "/" + os.path.basename(gain)) if gain else ""

    # motioncorr
    movieProt = protocolsList[protNames["ProtRelionMotioncor"]]
    movieProt["binFactor"] = bin
    movieProt["groupFrames"] = group_frames
    movieProt["defectFile"] = (prjPath + "/" + os.path.basename(defect)) if defect else ""

    # ctffind
    ctfProt = protocolsList[protNames["CistemProtCTFFind"]]
    ctfProt["findPhaseShift"] = paramDict['PhasePlateUsed']
    ctfProt["streamingBatchSize"] = BATCH_SIZE

    # picking
    pickProt = protocolsList[protNames["SphireProtCRYOLOPicking"]]
    pickProt["boxSize"] = paramDict['BoxSize']
    pickProt["streamingBatchSize"] = BATCH_SIZE

    # extract
    extrProt = protocolsList[protNames["ProtRelionExtractParticles"]]
    extrProt["boxSize"] = paramDict['BoxSize']
    extrProt["rescaledSize"] = paramDict['BoxSizeSmall']
    extrProt["backDiameter"] = paramDict['MaskSize']
    extrProt["streamingBatchSize"] = BATCH_SIZE

    jsonFn = "%s.json" % prjName
    with open(jsonFn, "w") as f:
        jsonStr = json.dumps(protocolsList, indent=4, separators=(',', ': '))
        f.write(jsonStr)

    cmd = 'scipion3 python -m pyworkflow.project.scripts.create %s %s' % (
        prjName, os.path.abspath(jsonFn))
    proc = subprocess.run(cmd.split(), check=True)

    os.rename(jsonFn, os.path.join(prjPath, jsonFn))
    os.chdir(prjPath)
    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            shutil.copyfile(i, os.path.basename(i))

    # Save acquisition params
    with open("%s_session_params" % paramDict['Software'], "w") as fn:
        fn.write("Movies dir: %s\n\n" % importProt["filesPath"])
        for k, v in sorted(paramDict.items()):
            fn.write("%s = %s\n" % (k, v))

    cmd2 = 'scipion3 python -m pyworkflow.project.scripts.scheme %s' % prjName
    proc2 = subprocess.Popen(cmd2.split(), universal_newlines=True)
