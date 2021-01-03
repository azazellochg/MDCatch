#!/usr/bin/env python3

""" Based on https://github.com/DiamondLightSource/python-relion-yolo-it by
Sjors H.W. Scheres, Takanori Nakane, Colin M. Palmer, Donovan Webb"""

import argparse
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
CONDA_ENV = ". /home/gsharov/rc/conda.rc && conda activate topaz-0.2.4"
TOPAZ_PREPROCESS = "topaz preprocess"
TOPAZ_EXTRACT = "topaz extract"
TOPAZ_CONVERT = "topaz convert"
TOPAZ_SPLIT = "topaz split"
DEBUG = 0


def run_job(project_dir, args):
    start = time.time()
    in_mics = args.in_mics
    job_dir = args.out_dir
    thresh = args.threshold
    diam = args.diam
    model = args.model
    gpu = args.gpu
    threads = args.threads
    workers = args.workers

    getPath = lambda *arglist: os.path.join(project_dir, *arglist)

    if model != "None":
        model = getPath(model)

    # Reading the micrographs star file from relion
    optics = Table(fileName=getPath(in_mics), tableName='optics')
    angpix = float(optics[0].rlnMicrographPixelSize)
    mictable = Table(fileName=getPath(in_mics), tableName='micrographs')

    # calculate downscale factor to get to 4-8 A/px
    for scale in range(2, 20):
        angpix_bin = angpix * scale
        if diam < 300 and (4.0 <= angpix_bin <= 6.0 or angpix > 6.0):
            break
        elif diam >= 300 and (6.0 <= angpix_bin <= 8.0 or angpix > 8.0):
            break

    print("Using downscale factor %d to get %0.2f A/pix for %d A particle" % (
        scale, angpix_bin, diam))

    # Arranging files for topaz: making symlinks for mics
    done_mics = []
    mic_dirs = []
    if os.path.exists(DONE_MICS):
        with open(DONE_MICS, "r") as f:
            done_mics.extend(f.read().splitlines())
    if DEBUG:
        print("Current done_mics: ", done_mics)

    mic_fns = mictable.getColumnValues("rlnMicrographName")
    mic_ext = os.path.splitext(mic_fns[0])[1]
    input_job = "/".join(mic_fns[0].split("/")[:2])
    keys = ["/".join(i.split("/")[2:]) for i in mic_fns]  # remove JobType/jobXXX
    values = [os.path.splitext(i)[0] + "_topaz.star" for i in keys]  # _topaz.star
    mic_dict = {k: v for k, v in zip(keys, values) if k not in done_mics}

    for mic in mic_dict:
        if DEBUG:
            print("Processing mic: ", mic)
        mic_dir = os.path.dirname(mic)
        # create folder for micrograph links for topaz job
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

    # Launching topaz preprocess
    args_dict = {
        '--scale': scale,
        '--destdir': 'preprocessed',
        '--num-workers': workers,
        '--num-threads': threads
    }
    cmd = "%s && %s " % (CONDA_ENV, TOPAZ_PREPROCESS)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])
    for i in mic_dirs:
        if len(glob("%s/*%s" % (i, mic_ext))):  # skip folders with no mics
            cmd += " %s/*%s" % (i, mic_ext)

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Launching topaz extract
    args_dict = {
        '--radius': int(diam / angpix_bin // 2),
        '--up-scale': scale,
        '--threshold': thresh,
        '--output': 'output/coords.txt',
        '--num-workers': workers,
        '--num-threads': threads,
        '--device': gpu
    }

    if model != "None":
        args_dict.update({'--model': model})

    cmd = "%s && %s " % (CONDA_ENV, TOPAZ_EXTRACT)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])
    cmd += " preprocessed/*.mrc"
    os.makedirs("output", exist_ok=True)

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # clean preprocessed dir
    shutil.rmtree("preprocessed")

    # Launching topaz convert
    cmd = "%s && %s " % (CONDA_ENV, TOPAZ_CONVERT)
    cmd += " -o output/coords.star output/coords.txt"
    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Launching topaz split
    cmd = "%s && %s " % (CONDA_ENV, TOPAZ_SPLIT)
    cmd += " --output output output/coords.star"
    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Move output star files for Relion to use
    with open(DONE_MICS, "a+") as f:
        for mic in mic_dict:
            f.write("%s\n" % mic)
            mic_base = os.path.basename(mic)
            os.remove(mic)  # clean up
            coord_topaz = "output/" + os.path.splitext(mic_base)[0] + ".star"
            coord_relion = mic_dict[mic]
            if os.path.exists(coord_topaz):
                os.rename(coord_topaz, getPath(job_dir, coord_relion))
                if DEBUG:
                    print("Moved %s to %s" % (coord_topaz, getPath(job_dir, coord_relion)))

    # clean output dir
    shutil.rmtree("output")

    # Required output mics star file
    with open("coords_suffix_topaz.star", "w") as mics_star:
        mics_star.write(in_mics)

    # Required output nodes star file
    nodes = Table(columns=['rlnPipeLineNodeName', 'rlnPipeLineNodeType'])
    nodes.addRow(os.path.join(job_dir, "coords_suffix_topaz.star"), "2")
    with open("RELION_OUTPUT_NODES.star", "w") as nodes_star:
        nodes.writeStar(nodes_star, tableName="output_nodes")

    outputFn = getPath(job_dir, "output_for_relion.star")
    if not os.path.exists(outputFn):
        # calculate diameter, original (boxSize) and downsampled (boxSizeSmall) box
        optics = Table(fileName=getPath(in_mics), tableName='optics')
        angpix = float(optics[0].rlnMicrographPixelSize)
        # use +10% for box size, make it even
        boxSize = math.ceil(diam * 1.1 / angpix / 2.) * 2

        # from relion_it.py script
        # Authors: Sjors H.W. Scheres, Takanori Nakane & Colin M. Palmer
        boxSizeSmall = None
        for box in (32, 48, 64, 96, 128, 160, 192, 256, 288, 300, 320,
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

        print("\nEstimated parameters:\n\tDiameter (A): %d\n\tBox size (px): %d\n"
              "\tBox size binned (px): %d" % (diam, boxSize, boxSizeSmall))

        # output all params into a star file
        tableTopaz = Table(columns=['rlnParticleDiameter',
                                    'rlnOriginalImageSize',
                                    'rlnImageSize'])
        tableTopaz.addRow(diam, boxSize, boxSizeSmall)
        with open(outputFn, "w") as f:
            tableTopaz.writeStar(f, tableName='picker')

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
    angpix         -1
 black_val          0
blue_value          0
color_label rlnParticleSelectZScore
  ctfscale          1
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
            f.write(starString % diam)

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff//3600, diff//60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job for calling topaz within Relion 3.1.0. Run it in the main Relion project directory, e.g.:
    external_job_topaz.py --o External/topaz_picking --in_mics CtfFind/job004/micrographs_ctf.star --diam 120 --threshold 0 --gpu 0
"""
    parser = argparse.ArgumentParser(usage=help)
    parser.add_argument("--in_mics", help="Input micrographs STAR file")
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--j", dest="threads", help="Number of CPU threads (default = 1)", type=int, default=1)
    parser.add_argument("--workers", dest="workers", help="Number of worker processes (default = 1)", type=int, default=1)
    parser.add_argument("--diam", help="Particle diameter in A (default = 120)", type=int, default=120)
    parser.add_argument("--threshold", help="Threshold for picking (default = -6)", type=float, default=-6)
    parser.add_argument("--model", help="Topaz training model (if not specified default is used)", default="None")
    parser.add_argument("--gpu", help='GPU to use (default = 0)', default="0")
    parser.add_argument("--pipeline_control", help="Not used here. Required by relion")

    args = parser.parse_args()

    if args.in_mics is None or args.out_dir is None:
        print("Error: --in_mics and --o are required params!")
        exit(1)

    if not args.in_mics.endswith(".star"):
        print("Error: --in_mics must point to a micrographs star file")
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
