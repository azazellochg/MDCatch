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
import time
from glob import glob
import subprocess
import math
from emtable import Table  # run "pip3 install --user emtable" for system python


CONDA_ENV = ". /home/gsharov/rc/conda.rc && conda activate cryolo-1.8"
CRYOLO_PREDICT = "cryolo_predict.py"
CRYOLO_GEN_MODEL = "/home/gsharov/soft/cryolo/gmodel_phosnet_202005_N63_c17.h5"
CRYOLO_GEN_JANNI_MODEL = "/home/gsharov/soft/cryolo/gmodel_phosnet_202005_nn_N63_c17.h5"
CRYOLO_JANNI_MODEL = "/home/gsharov/soft/cryolo/gmodel_janni_20190703.h5"
SCRATCH_DIR = os.getenv("RELION_SCRATCH_DIR", None)  # SSD scratch space for filtered mics, can be None
DEBUG = 0


def run_job(args):
    start = time.time()
    in_mics = args.in_mics
    job_dir = args.out_dir
    thresh = args.threshold
    box_size = args.box_size
    distance = 0
    model = args.model
    filament = args.filament
    if filament:
        box_dist = args.box_distance
        min_boxes = args.minimum_number_boxes
    denoise = args.denoise
    gpus = args.gpu
    threads = args.threads

    if SCRATCH_DIR is not None:
        filtered_dir = os.path.join(SCRATCH_DIR, "filtered_tmp")
    else:
        filtered_dir = "%s/filtered_tmp/" % job_dir

    if model == "None":
        model = CRYOLO_GEN_MODEL if not denoise else CRYOLO_GEN_JANNI_MODEL
    else:
        model = os.path.abspath(model)

    # Making a cryolo config file
    json_dict = {
        "model": {
            "architecture": "PhosaurusNet",
            "input_size": 1024,
            "max_box_per_image": 600,
            "filter": [
                0.1,
                filtered_dir
            ]
        },
        "other": {
            "log_path": "%s/logs/" % job_dir
        }
    }
    if box_size:  # is not 0
        json_dict["model"]["anchors"] = [int(box_size), int(box_size)]
        if not filament:
            distance = int(box_size / 2)  # use half the box_size
    if denoise:
        json_dict["model"]["filter"] = [
            CRYOLO_JANNI_MODEL,
            24,
            3,
            filtered_dir
        ]

    if DEBUG:
        print("Using following config: ", json_dict)

    with open(os.path.join(job_dir, "config_cryolo.json"), "w") as json_file:
        json.dump(json_dict, json_file, indent=4)

    # Reading the micrographs star file from Relion
    mictable = Table(fileName=in_mics, tableName='micrographs')
    mic_fns = mictable.getColumnValues("rlnMicrographName")

    # Launching cryolo
    args_dict = {
        '--conf': os.path.join(job_dir, "config_cryolo.json"),
        '--input': in_mics,
        '--output': os.path.join(job_dir, 'output'),
        '--weights': model,
        '--gpu': gpus.replace(',', ' '),
        '--threshold': thresh,
        '--distance': distance,
        '--cleanup': "",
        '--skip': "",
        '--write_empty': "",
        '--num_cpu': -1 if threads == 1 else threads
    }

    if filament:
        args_dict.update({
            '--filament': "",
            '--box_distance': box_dist,
            '--minimum_number_boxes': min_boxes,
            '--directional_method': 'PREDICTED'
        })
        args_dict.pop('--distance')

    cmd = "%s && %s " % (CONDA_ENV, CRYOLO_PREDICT)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Moving output star files for Relion to use
    table_coords = Table(columns=['rlnMicrographName', 'rlnMicrographCoordinates'])
    star_dir = "EMAN_HELIX_SEGMENTED" if filament else "STAR"
    ext = ".box" if filament else ".star"
    with open(os.path.join(job_dir, "autopick.star"), "w") as mics_star:
        for mic in mic_fns:
            mic_base = os.path.basename(mic)
            mic_dir = os.path.dirname(mic)
            if len(mic_dir.split("/")) > 1 and "job" in mic_dir.split("/")[1]:  # remove JobType/jobXXX
                mic_dir = "/".join(mic_dir.split("/")[2:])
            os.makedirs(os.path.join(job_dir, mic_dir), exist_ok=True)
            coord_cryolo = os.path.splitext(mic_base)[0] + ext
            coord_cryolo = os.path.join(job_dir, "output", star_dir, coord_cryolo)
            coord_relion = os.path.splitext(mic_base)[0] + "_autopick" + ext
            coord_relion = os.path.join(job_dir, mic_dir, coord_relion)
            if os.path.exists(coord_cryolo):
                os.rename(coord_cryolo, coord_relion)
                table_coords.addRow(mic, coord_relion)
                if DEBUG:
                    print("Moved %s to %s" % (coord_cryolo, coord_relion))
        table_coords.writeStar(mics_star, tableName='coordinate_files')

    # Required output to mini pipeline job_pipeline.star file
    pipeline_fn = os.path.join(job_dir, "job_pipeline.star")
    table_gen = Table(columns=['rlnPipeLineJobCounter'])
    table_gen.addRow(2)
    table_proc = Table(columns=['rlnPipeLineProcessName', 'rlnPipeLineProcessAlias',
                                'rlnPipeLineProcessTypeLabel', 'rlnPipeLineProcessStatusLabel'])
    table_proc.addRow(job_dir, 'None', 'relion.external', 'Running')
    table_nodes = Table(columns=['rlnPipeLineNodeName', 'rlnPipeLineNodeTypeLabel'])
    table_nodes.addRow(in_mics, "MicrographsData.star.relion")
    table_nodes.addRow(os.path.join(job_dir, "autopick.star"), "MicrographsCoords.star.relion.autopick")
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

    # Register output nodes in .Nodes/
    os.makedirs(os.path.join(".Nodes", "MicrographsCoords", job_dir), exist_ok=True)
    open(os.path.join(".Nodes", "MicrographsCoords", job_dir, "autopick.star"), "w").close()

    outputFn = os.path.join(job_dir, "output_for_relion.star")
    if not os.path.exists(outputFn):
        # get estimated box size
        summaryfn = os.path.join(job_dir, "output/DISTR", 'size_distribution_summary*.txt')
        with open(glob(summaryfn)[0]) as f:
            for line in f:
                if line.startswith("MEAN,"):
                    estim_sizepx = int(line.split(",")[-1])
                    break
        print("\ncrYOLO estimated box size %d px" % estim_sizepx)

        # calculate diameter, original (boxSize) and downsampled (boxSizeSmall) box
        optics = Table(fileName=in_mics, tableName='optics')
        angpix = float(optics[0].rlnMicrographPixelSize)

        if filament:
            # box size = 1.5x tube diam
            diam = 0.66 * box_size
        else:
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
                # If Nyquist freq. is better than 7.5 A, use this
                # downscaled box, otherwise continue to next size up
                small_box_angpix = angpix * boxSize / box
                if small_box_angpix < 3.75:
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

_rlnJobTypeLabel             relion.manualpick%s
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0

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
do_fom_threshold         No
  do_queue         No
do_startend        No
  fn_color         ""
     fn_in         ""
  highpass         -1
   lowpass         20
  micscale        0.2
min_dedicated       1
minimum_pick_fom          0
other_args         ""
      qsub       qsub
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh
 queuename    openmpi
 red_value          2
sigma_contrast      3
 white_val          0
"""
        label = ".helical" if filament else ""
        with open(".gui_manualpickjob.star", "w") as f:
            f.write(starString % (label, angpix, diam))

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff//3600, diff//60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job for calling crYOLO 1.8+ within Relion 4.0. Run it in the Relion project directory, e.g.:
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
        if None in [args.box_size, args.box_distance, args.minimum_number_boxes]:
            print("Error: --box_size, --bd, --mn are required in filament mode!")
            exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    RELION_JOB_FAILURE_FILENAME = os.path.join(args.out_dir, "RELION_JOB_EXIT_FAILURE")
    RELION_JOB_SUCCESS_FILENAME = os.path.join(args.out_dir, "RELION_JOB_EXIT_SUCCESS")

    if os.path.isfile(RELION_JOB_FAILURE_FILENAME):
        os.remove(RELION_JOB_FAILURE_FILENAME)
    if os.path.isfile(RELION_JOB_SUCCESS_FILENAME):
        os.remove(RELION_JOB_SUCCESS_FILENAME)
    try:
        run_job(args)
    except:
        open(RELION_JOB_FAILURE_FILENAME, "w").close()
        raise
    else:
        open(RELION_JOB_SUCCESS_FILENAME, "w").close()


if __name__ == "__main__":
    main()
