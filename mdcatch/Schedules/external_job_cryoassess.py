#!/usr/bin/env python3

""" Based on https://github.com/DiamondLightSource/python-relion-yolo-it by
Sjors H.W. Scheres, Takanori Nakane, Colin M. Palmer, Donovan Webb"""

import argparse
import os
import re
from glob import glob
import time
import subprocess
from emtable import Table


RELION_JOB_FAILURE_FILENAME = "RELION_JOB_EXIT_FAILURE"
RELION_JOB_SUCCESS_FILENAME = "RELION_JOB_EXIT_SUCCESS"
CONDA_ENV = ". /home/gsharov/rc/conda.rc && conda activate cryoassess-0.1.0"
CRYOASSESS_2D = "2dassess"
CRYOASSESS_2D_MODEL = "/home/gsharov/soft/cryoassess-models/2dassess_062119.h5"
DEBUG = 0


def run_job(project_dir, args):
    start = time.time()
    in_parts = args.in_parts
    job_dir = args.out_dir
    batch = args.batch_size
    gpu = args.gpu

    getPath = lambda *arglist: os.path.join(project_dir, *arglist)

    # Reading the model star file from relion
    modelstar = in_parts.replace("_data.star", "_model.star")
    refstable = Table(fileName=getPath(modelstar), tableName='model_classes')
    refstack = refstable[0].rlnReferenceImage.split("@")[-1]
    nrCls = int(refstable[-1].rlnReferenceImage.split("@")[0])

    if DEBUG:
        print("Found input class averages stack: %s" % refstack)

    # Launching cryoassess
    args_dict = {
        '-i': getPath(refstack),
        '-o': getPath(job_dir, 'output'),
        '-b': batch,
        '-m': CRYOASSESS_2D_MODEL,
    }
    cmd = "%s && CUDA_VISIBLE_DEVICES=%s %s " % (CONDA_ENV, gpu, CRYOASSESS_2D)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Parse output to get good classes IDs
    goodTemplate = getPath(job_dir, "output/Good/particle_*.jpg")
    regex = re.compile('particle_(\d*)\.jpg')
    goodcls = []
    files = glob(goodTemplate)
    if files:
        for i in files:
            s = regex.search(i)
            goodcls.append(int(s.group(1)))

    if DEBUG:
        print("Parsing output files: %s\nGood classes: %s" % (goodTemplate, goodcls))

    if len(goodcls) == 0:
        print("No good classes found. Job stopped.")
        end = time.time()
        diff = end - start
        print("Job duration = %dh %dmin %dsec \n" % (diff // 3600, diff // 60 % 60, diff % 60))
        open(RELION_JOB_FAILURE_FILENAME, "w").close()
        exit(1)

    # Create output star file for Relion to use
    optics = Table(fileName=getPath(in_parts), tableName='optics')
    ptcls = Table(fileName=getPath(in_parts), tableName='particles')
    cols = ptcls.getColumnNames()
    out_ptcls = Table(columns=cols)

    for row in ptcls:
        if row.rlnClassNumber in goodcls:
            out_ptcls.addRow(*row)

    if DEBUG:
        print("Input particles: %d\nOutput particles: %d" %
              (len(ptcls), len(out_ptcls)))

    out_star = getPath(job_dir, "particles_for_training.star")
    with open(out_star, "w") as f:
        optics.writeStar(f, tableName="optics")
        out_ptcls.writeStar(f, tableName="particles")

    # Create backup_selection.star for results visualization
    sel = Table(columns=['rlnSelected'])
    for i in range(1, nrCls+1):
        sel.addRow(1 if i in goodcls else 0)
    with open(getPath("backup_selection.star"), "w") as f:
        sel.writeStar(f, tableName="")

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff // 3600, diff // 60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job for calling cryoassess within Relion 3.1.0. Run it in the main Relion project directory, e.g.:
    external_job_cryoassess.py --o External/cryoassess_bestclasses2d --in_parts Class2D/job004/run_it025_data.star
"""
    parser = argparse.ArgumentParser(usage=help)
    parser.add_argument("--in_parts", help="Input data STAR file from Class2D job")
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--batch_size", help="Batch size used in prediction. Default is 32. If "
                        "memory error/warning appears, try lower this number to "
                        "16, 8, or even lower", default=32)
    parser.add_argument("--gpu", help='GPU to use', default='0')
    parser.add_argument("--pipeline_control", help="Not used here. Required by relion")
    parser.add_argument("--j", dest="threads", help="Not used here. Required by relion")

    args = parser.parse_args()

    if args.in_parts is None or args.out_dir is None:
        print("Error: --in_parts and --o are required params!")
        exit(1)

    if not args.in_parts.endswith("_data.star"):
        print("Error: --in_parts must point to a data STAR file")
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
