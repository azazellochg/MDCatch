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
from .config import JSON_TEMPLATE, SCHEDULE_PATH, PATTERN_SEM_MOVIES


def setupRelion(paramDict):
    """ Prepare and launch Relion 4.0 schedules. """
    try:
        subprocess.check_output(["which", "relion_scheduler"],
                                stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: Relion not found in PATH!")
        exit(1)

    bin, gain, defect, group_frames = precalculateVars(paramDict)
    mask_diam = int(paramDict['MaskSize']) * bin * float(paramDict['PixelSpacing'])
    mapDict = {
        'prep__do_at_most': 5,
        'prep__ctffind__do_phaseshift': paramDict['PhasePlateUsed'],
        'prep__importmovies__Cs': paramDict['Cs'],
        'prep__importmovies__angpix': paramDict['PixelSpacing'],
        'prep__importmovies__kV': paramDict['Voltage'],
        'prep__importmovies__optics_group_name': '"%s"' % paramDict['OpticalGroup'],
        'prep__motioncorr__bin_factor': bin,
        'prep__motioncorr__dose_per_frame': paramDict['DosePerFrame'],
        'prep__motioncorr__group_frames': group_frames,
        'proc__class2d_ini__particle_diameter': mask_diam,
        'proc__class2d_rest__particle_diameter': mask_diam,
        'proc__extract_ini__bg_diameter': paramDict['MaskSize'],
        'proc__extract_ini__extract_size': paramDict['BoxSize'],
        'proc__extract_ini__rescale': paramDict['BoxSizeSmall'],
        'proc__extract_rest__bg_diameter': paramDict['MaskSize'],
        'proc__extract_rest__extract_size': paramDict['BoxSize'],
        'proc__extract_rest__rescale': paramDict['BoxSizeSmall'],
        'proc__inimodel3d__particle_diameter': mask_diam,
        'proc__inimodel3d__sym_name': '"%s"' % paramDict['Symmetry'],
        'proc__inipicker__topaz_particle_diameter': paramDict['PtclSizes'][1],
        'proc__refine3d__particle_diameter': mask_diam,
        'proc__refine3d__sym_name': '"%s"' % paramDict['Symmetry'],
        'proc__restpicker__topaz_particle_diameter': paramDict['PtclSizes'][1],
        'proc__train_topaz__topaz_particle_diameter': paramDict['PtclSizes'][1],
    }

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
                              paramDict['PtclSizes'][1]))

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

    if not os.path.exists('Schedules'):
        shutil.copytree(SCHEDULE_PATH, os.getcwd() + '/Schedules')

    # Save relion params in .py file
    with open("relion_it_options.py", 'w') as file:
        file.write("{\n")
        for k, v in mapDict.items():
            if v != '':
                file.write("'%s' : %s, \n" % (k, v))
        file.write("}\n")

    # Save acquisition params
    with open("%s_session_params" % paramDict['Software'], "w") as fn:
        fn.write("Movies dir: %s\n\n" % origPath1)
        for k, v in sorted(paramDict.items()):
            fn.write("%s = %s\n" % (k, v))

    # Set up scheduler vars
    cmdList = list()
    for key in mapDict:
        if mapDict[key] != '':
            opts = key.split("__")
            if key.count("__") == 2:  # job option
                jobstar = 'Schedules/' + opts[0] + '/' + opts[1] + '/job.star'
                cmd = 'relion_pipeliner --editJob %s --editOption %s --editValue %s' % (
                    jobstar, opts[2], mapDict[key])
            else:  # schedule option
                cmd = 'relion_scheduler --schedule %s --set_var %s --value %s --original_value %s' % (
                    opts[0], opts[1], mapDict[key], mapDict[key])

            cmdList.append(cmd)

    for cmd in sorted(cmdList):
        print(cmd)
        os.system(cmd)

    # Run scheduler
    cmdList = ['relion_scheduler --schedule prep --reset &',
               'relion_scheduler --schedule prep --run --pipeline_control Schedules/prep/ >> Schedules/prep/run.out 2>> Schedules/prep/run.err &',
               'relion_scheduler --schedule proc --reset &',
               'relion_scheduler --schedule proc --run --pipeline_control Schedules/proc/ >> Schedules/proc/run.out 2>> Schedules/proc/run.err &']

    for cmd in cmdList:
        print(cmd)
        os.system(cmd)


def setupScipion(paramDict):
    """ Prepare and schedule Scipion 3 workflow.
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
    prjPath = os.path.join(out.decode().replace('"', '').replace('\n', ''), "projects", prjName)
    os.chdir(prjPath)

    with open(JSON_TEMPLATE, 'r') as f:
        protocolsList = json.load(f)
    protNames = dict()

    for i, protDict in enumerate(protocolsList):
        protClassName = protDict['object.className']
        protNames[protClassName] = i

    bin, gain, defect, group_frames = precalculateVars(paramDict)
    for i in [gain, defect, paramDict['MTF']]:
        if os.path.exists(i):
            shutil.copyfile(i, os.path.basename(i))

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
    importProt["gainFile"] = os.path.join(os.getcwd(), os.path.basename(gain)) if gain else ""

    # motioncorr
    movieProt = protocolsList[protNames["ProtRelionMotioncor"]]
    movieProt["binFactor"] = bin
    movieProt["groupFrames"] = group_frames
    movieProt["defectFile"] = os.path.join(os.getcwd(), os.path.basename(defect)) if defect else ""

    # ctffind
    ctfProt = protocolsList[protNames["CistemProtCTFFind"]]
    ctfProt["findPhaseShift"] = paramDict['PhasePlateUsed']

    jsonFn = "%s.json" % prjName
    with open(jsonFn, "w") as f:
        jsonStr = json.dumps(protocolsList, indent=4, separators=(',', ': '))
        f.write(jsonStr)

    try:
        subprocess.check_output(["which", "scipion3"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("ERROR: scipion3 command not found in PATH!")
        exit(1)

    cmd = 'scipion3 python -m pyworkflow.project.scripts.create %s %s' % (
        prjName, os.path.abspath(jsonFn))
    proc = subprocess.run(cmd.split(), check=True)

    cmd2 = 'scipion3 python -m pyworkflow.project.scripts.schedule %s' % prjName
    proc2 = subprocess.Popen(cmd2.split(), universal_newlines=True)
