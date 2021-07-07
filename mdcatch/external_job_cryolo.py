#!/usr/bin/env python3
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
""" Based on https://github.com/DiamondLightSource/python-relion-yolo-it by
Sjors H.W. Scheres, Takanori Nakane, Colin M. Palmer, Donovan Webb"""

import argparse
import json
import os
import shutil
import time
from glob import glob
import subprocess
import math
from emtable import Table  # requires pip install emtable


RELION_JOB_FAILURE_FILENAME = "RELION_JOB_EXIT_FAILURE"
RELION_JOB_SUCCESS_FILENAME = "RELION_JOB_EXIT_SUCCESS"
DONE_MICS = "done_mics.txt"
CONDA_ENV = ". /home/gsharov/rc/conda.rc && conda activate cryolo-1.7.7"
CRYOLO_PREDICT = "cryolo_predict.py"
CRYOLO_GEN_MODEL = "/home/gsharov/soft/cryolo/gmodel_phosnet_202005_N63_c17.h5"
CRYOLO_GEN_JANNI_MODEL = "/home/gsharov/soft/cryolo/gmodel_phosnet_202005_nn_N63_c17.h5"
CRYOLO_JANNI_MODEL = "/home/gsharov/soft/cryolo/gmodel_janni_20190703.h5"
DEBUG = 0


def run_job(project_dir, args):
    start = time.time()
    in_mics = args.in_mics
    job_dir = args.out_dir
    thresh = args.threshold
    box_size = args.box_size
    distance = 0
    model = args.model
    filament = args.filament
    if filament:
        fil_width = args.filament_width
        box_dist = args.box_distance
        min_boxes = args.minimum_number_boxes
    denoise = args.denoise
    gpus = args.gpu
    threads = args.threads

    getPath = lambda *arglist: os.path.join(project_dir, *arglist)

    if model == "None":
        model = CRYOLO_GEN_MODEL if not denoise else CRYOLO_GEN_JANNI_MODEL
    else:
        model = getPath(model)

    # Making a cryolo config file
    json_dict = {"model": {
        "architecture": "PhosaurusNet",
        "input_size": 1024,
        "max_box_per_image": 600,
        "filter": [
            0.1,
            "filtered_tmp/"
        ]
    }}

    if box_size:  # is not 0
        json_dict["model"]["anchors"] = [int(box_size), int(box_size)]
        if not filament:
            distance = int(box_size / 2)  # use half the box_size
    if denoise:
        json_dict["model"]["filter"] = [
            CRYOLO_JANNI_MODEL,
            24,
            3,
            "filtered_tmp/"
        ]

    if DEBUG:
        print("Using following config.json: ", json_dict)

    with open("config_cryolo.json", "w") as json_file:
        json.dump(json_dict, json_file, indent=4)

    # Reading the micrographs star file from relion
    mictable = Table(fileName=getPath(in_mics), tableName='micrographs')

    # Arranging files for cryolo: making symlinks for mics
    done_mics = []
    mic_dirs = []
    if os.path.exists(DONE_MICS):
        with open(DONE_MICS, "r") as f:
            done_mics.extend(f.read().splitlines())
    if DEBUG:
        print("Current done_mics: ", done_mics)

    mic_fns = mictable.getColumnValues("rlnMicrographName")
    mic_ext = os.path.splitext(mic_fns[0])[1]
    if "job" in mic_fns[0].split("/")[1]:  # remove JobType/jobXXX
        input_job = "/".join(mic_fns[0].split("/")[:2])
        keys = ["/".join(i.split("/")[2:]) for i in mic_fns]
    else:
        input_job = ""
        keys = mic_fns
    values = [os.path.splitext(i)[0] + "_autopick.star" for i in keys]
    mic_dict = {k: v for k, v in zip(keys, values) if k not in done_mics}

    for mic in mic_dict:
        if DEBUG:
            print("Processing mic: ", mic)
        mic_dir = os.path.dirname(mic)
        # create folder for micrograph links for cryolo job
        if not os.path.isdir(mic_dir):
            os.makedirs(mic_dir)
        if mic_dir not in mic_dirs:
            mic_dirs.append(mic_dir)
            if DEBUG:
                print("Added folder %s to the mic_dirs" % mic_dir)
        inputfn = getPath(input_job, mic)
        outfn = getPath(job_dir, mic)
        os.symlink(inputfn, outfn)
        if DEBUG:
            print("Link %s --> %s" % (inputfn, outfn))

    if len(mic_dict.keys()) == 0:
        print("All mics picked! Nothing to do.")
        open(RELION_JOB_SUCCESS_FILENAME, "w").close()
        exit(0)

    # Launching cryolo
    args_dict = {
        '--conf': "config_cryolo.json",
        '--output': 'output',
        '--weights': model,
        '--gpu': gpus.replace(',', ' '),
        '--threshold': thresh,
        '--distance': distance,
        '--cleanup': "",
        '--num_cpu': -1 if threads == 1 else threads
    }

    if filament:
        args_dict.update({
            '--filament': "",
            '--filament_width': fil_width,
            '--box_distance': box_dist,
            '--minimum_number_boxes': min_boxes
        })

    cmd = "%s && %s " % (CONDA_ENV, CRYOLO_PREDICT)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])
    cmd += " --input "
    for i in mic_dirs:
        if len(glob("%s/*%s" % (i, mic_ext))):  # skip folders with no mics
            cmd += "%s/ " % i

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Moving output star files for Relion to use
    table_coords = Table(columns=['rlnMicrographName', 'rlnMicrographCoordinates'])
    with open(DONE_MICS, "a+") as f, open("autopick.star", "w") as mics_star:
        for mic in mic_dict:
            f.write("%s\n" % mic)
            mic_base = os.path.basename(mic)
            os.remove(mic)  # clean up symlink
            coord_cryolo = os.path.splitext(mic_base)[0] + ".star"
            coord_cryolo = getPath(job_dir, "output", "STAR", coord_cryolo)
            coord_relion = mic_dict[mic]
            if os.path.exists(coord_cryolo):
                os.rename(coord_cryolo, getPath(job_dir, coord_relion))
                table_coords.addRow(os.path.join(input_job, mic), os.path.join(job_dir, coord_relion))
                if DEBUG:
                    print("Moved %s to %s" % (coord_cryolo, getPath(job_dir, coord_relion)))
        table_coords.writeStar(mics_star, tableName='coordinate_files')

    # Required output job_pipeline.star file
    pipeline_fn = getPath(job_dir, "job_pipeline.star")
    table_gen = Table(columns=['rlnPipeLineJobCounter'])
    table_gen.addRow(2)
    table_proc = Table(columns=['rlnPipeLineProcessName', 'rlnPipeLineProcessAlias',
                                'rlnPipeLineProcessTypeLabel', 'rlnPipeLineProcessStatusLabel'])
    table_proc.addRow(job_dir, 'None', 'External', 'Running')
    table_nodes = Table(columns=['rlnPipeLineNodeName', 'rlnPipeLineNodeTypeLabel'])
    table_nodes.addRow(in_mics, "relion.MicrographStar")
    table_nodes.addRow(os.path.join(job_dir, "autopick.star"), "relion.CoordinateStar")
    table_input = Table(columns=['rlnPipeLineEdgeFromNode', 'rlnPipeLineEdgeProcess'])
    table_input.addRow(in_mics, job_dir)
    table_output = Table(columns=['rlnPipeLineEdgeProcess', 'rlnPipeLineEdgeToNode'])
    table_output.addRow(job_dir, os.path.join(job_dir, "autopick.star"))

    with open(pipeline_fn, "w") as f:
        table_gen.writeStar(f, tableName="pipeline_general", singleRow=True)
        table_proc.writeStar(f, tableName="pipeline_processes")
        table_nodes.writeStar(f, tableName="pipeline_nodes")
        table_input.writeStar(f, tableName="pipeline_input_edges")
        table_output.writeStar(f, tableName="pipeline_output_edges")

    outputFn = getPath(job_dir, "output_for_relion.star")
    if not os.path.exists(outputFn):
        # get estimated box size
        summaryfn = getPath(job_dir, "output/DISTR",
                            'size_distribution_summary*.txt')
        with open(glob(summaryfn)[0]) as f:
            for line in f:
                if line.startswith("MEAN,"):
                    estim_sizepx = int(line.split(",")[-1])
                    break
        print("\ncrYOLO estimated box size %d px" % estim_sizepx)

        # calculate diameter, original (boxSize) and downsampled (boxSizeSmall) box
        optics = Table(fileName=getPath(in_mics), tableName='optics')
        angpix = float(optics[0].rlnMicrographPixelSize)
        # use + 20% for diameter
        diam = math.ceil(estim_sizepx * angpix * 1.2)
        # use +30% for box size, make it even
        boxSize = 1.3 * estim_sizepx
        boxSize = math.ceil(boxSize / 2.) * 2

        # from relion_it.py script
        # Authors: Sjors H.W. Scheres, Takanori Nakane & Colin M. Palmer
        boxSizeSmall = None
        for box in (48, 64, 96, 128, 160, 192, 256, 288, 300, 320,
                    360, 384, 400, 420, 450, 480, 512, 640, 768,
                    896, 1024):
            # Don't go larger than the original box
            if box > boxSize:
                boxSizeSmall = boxSize
                break
            # If Nyquist freq. is better than 8.5 A, use this
            # downscaled box, otherwise continue to next size up
            small_box_angpix = angpix * boxSize / box
            if small_box_angpix < 4.25:
                boxSizeSmall = box
                break

        print("\nSuggested parameters:\n\tDiameter (A): %d\n\tBox size (px): %d\n"
              "\tBox size binned (px): %d" % (diam, boxSize, boxSizeSmall))

        # output all params into a star file
        tableCryolo = Table(columns=['rlnParticleDiameter',
                                     'rlnOriginalImageSize',
                                     'rlnImageSize'])
        tableCryolo.addRow(diam, boxSize, boxSizeSmall)
        with open(outputFn, "w") as f:
            tableCryolo.writeStar(f, tableName='picker')

        # create .gui_manualpickjob.star for easy display
        starString = """
# version 30001
data_job
_rlnJobType                             3
_rlnJobIsContinue                       0
# version 30001
data_joboptions_values
loop_
_rlnJobOptionVariable #1
_rlnJobOptionValue #2
    angpix         %f
 black_val          0
blue_value          0
color_label rlnParticleSelectZScore
  diameter         %d
  do_color         No
  do_queue         No
do_startend        No
  fn_color         ""
     fn_in         ""
  highpass         -1
   lowpass         20
  micscale        0.2
min_dedicated       1
other_args         ""
      qsub       qsub
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh
 queuename    openmpi
 red_value          2
sigma_contrast      3
 white_val          0
"""
        with open(getPath(".gui_manualpickjob.star"), "w") as f:
            f.write(starString % (angpix, diam))

    # remove output dir
    if os.path.isdir("output"):
        shutil.rmtree("output")

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff//3600, diff//60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job for calling cryolo within Relion 4.0. Run it in the Relion project directory, e.g.:
    external_job_cryolo.py --o External/cryolo_picking --in_mics CtfFind/job004/micrographs_ctf.star
"""
    parser = argparse.ArgumentParser(usage=help)
    parser.add_argument("--in_mics", help="Input micrographs STAR file")
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--j", dest="threads", help="Number of CPU threads (default = all)", type=int, default=1)
    parser.add_argument("--box_size", help="Box size (default = 0 means it's estimated)", type=int, default=0)
    parser.add_argument("--threshold", help="Threshold for picking (default = 0.3)", type=float, default=0.3)
    parser.add_argument("--model", help="Cryolo training model (if not specified general model is used)", default="None")
    parser.add_argument("--filament", help='Enable filament mode', default=False, action='store_true')
    parser.add_argument("--fw", dest="filament_width", help='[FILAMENT MODE] Filament width (in pixel)', type=int, default=None)
    parser.add_argument("--bd", dest="box_distance", help='[FILAMENT MODE] Distance in pixel between two boxes', type=int, default=None)
    parser.add_argument("--mn", dest="minimum_number_boxes", help='[FILAMENT MODE] Minimum number of boxes per filament', type=int, default=None)
    parser.add_argument("--denoise", help="Denoise with JANNI instead of lowpass filtering", default=False, action='store_true')
    parser.add_argument("--gpu", help='GPUs to use (e.g. "0,1,2,3", default = "0")', default="0")
    parser.add_argument("--pipeline_control", help="Not used here. Required by Relion")

    args = parser.parse_args()

    if args.in_mics is None or args.out_dir is None:
        print("Error: --in_mics and --o are required params!")
        exit(1)

    if not args.in_mics.endswith(".star"):
        print("Error: --in_mics must point to a micrographs star file!")
        exit(1)

    if args.filament:
        if None in [args.filament_width, args.box_distance, args.minimum_number_boxes]:
            print("Error: --fw, --bd, --mn are required in filament mode!")
            exit(1)

    project_dir = os.getcwd()
    os.makedirs(args.out_dir, exist_ok=True)
    os.chdir(args.out_dir)
    if os.path.isfile(RELION_JOB_FAILURE_FILENAME):
        os.remove(RELION_JOB_FAILURE_FILENAME)
    if os.path.isfile(RELION_JOB_SUCCESS_FILENAME):
        os.remove(RELION_JOB_SUCCESS_FILENAME)
    try:
        run_job(project_dir, args)
    except:
        open(RELION_JOB_FAILURE_FILENAME, "w").close()
        raise
    else:
        open(RELION_JOB_SUCCESS_FILENAME, "w").close()


if __name__ == "__main__":
    main()
