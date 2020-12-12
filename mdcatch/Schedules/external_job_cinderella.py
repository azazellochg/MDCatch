#!/usr/bin/env python3

""" Based on https://github.com/DiamondLightSource/python-relion-yolo-it by
Sjors H.W. Scheres, Takanori Nakane, Colin M. Palmer, Donovan Webb"""

import argparse
import os
import time
import subprocess
from emtable import Table


RELION_JOB_FAILURE_FILENAME = "RELION_JOB_EXIT_FAILURE"
RELION_JOB_SUCCESS_FILENAME = "RELION_JOB_EXIT_SUCCESS"
CONDA_ENV = ". /home/gsharov/rc/conda.rc && conda activate cinderella-0.7.0"
CINDERELLA_PREDICT = "sp_cinderella_predict.py"
CINDERELLA_GEN_MODEL = "/home/gsharov/soft/cryolo/relion_lmb_cl2d_model_based_on_cinderella.h5"
DEBUG = 0


def run_job(project_dir, args):
    start = time.time()
    in_parts = args.in_parts
    job_dir = args.out_dir
    thresh = args.threshold
    model = args.model
    gpus = args.gpu

    getPath = lambda *arglist: os.path.join(project_dir, *arglist)

    if model == "None":
        model = CINDERELLA_GEN_MODEL
    else:
        model = getPath(model)

    # Reading the model star file from relion
    modelstar = in_parts.replace("_data.star", "_model.star")
    refstable = Table(fileName=getPath(modelstar), tableName='model_classes')
    refstack = refstable[0].rlnReferenceImage.split("@")[-1]
    nrCls = int(refstable[-1].rlnReferenceImage.split("@")[0])

    if DEBUG:
        print("Found input class averages stack: %s" % refstack)

    # Launching cinderella
    args_dict = {
        '-i': getPath(refstack),
        '-o': 'output',
        '-w': model,
        '--gpu': gpus,
        '-t': thresh,
    }
    cmd = "%s && %s " % (CONDA_ENV, CINDERELLA_PREDICT)
    cmd += " ".join(['%s %s' % (k, v) for k, v in args_dict.items()])

    print("Running command:\n{}".format(cmd))
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()

    if proc.returncode:
        raise Exception("Command failed with return code %d" % proc.returncode)

    # Parse output to get good classes IDs
    outfn = os.path.basename(refstack.replace(".mrcs", "_index_confidence.txt"))
    outpath = getPath(job_dir, "output", outfn)
    goodcls = []
    with open(outpath, "r") as f:
        for line in f:
            if float(line.split()[1]) > thresh:
                goodcls.append(int(line.split()[0]) + 1)
            else:
                break

    if DEBUG:
        print("Parsing output file: %s\nGood classes: %s" % (outpath, goodcls))

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
    for i in range(1, nrCls + 1):
        sel.addRow(1 if i in goodcls else 0)
    with open(getPath("backup_selection.star"), "w") as f:
        sel.writeStar(f, tableName="")

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff//3600, diff//60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job for calling cinderella within Relion 3.1.0. Run it in the main Relion project directory, e.g.:
    external_job_cinderella.py --o External/cinderella_bestclasses2d --in_parts Class2D/job004/run_it025_data.star --threshold 0.7
"""
    parser = argparse.ArgumentParser(usage=help)
    parser.add_argument("--in_parts", help="Input data STAR file from Class2D job")
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--threshold", help="Confidence threshold (default = 0.7)", type=float, default=0.7)
    parser.add_argument("--model", help="Cinderella prediction model (if not specified general is used)", default="None")
    parser.add_argument("--gpu", help='GPUs to use (e.g. "0 1 2 3")', default="0")
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
