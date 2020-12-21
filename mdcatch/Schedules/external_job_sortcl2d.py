#!/usr/bin/env python3

""" Based on https://github.com/diamondlightsource/python-relion-yolo-it by
Sjors H.W. Scheres, Takanori Nakane, Colin M. Palmer, Donovan Webb"""

import os
import time
import argparse
from emtable import Table  # requires pip install emtable


RELION_JOB_FAILURE_FILENAME = "RELION_JOB_EXIT_FAILURE"
RELION_JOB_SUCCESS_FILENAME = "RELION_JOB_EXIT_SUCCESS"
DEBUG = 0


def run_job(project_dir, args):
    start = time.time()
    in_parts = args.in_parts
    job_dir = args.out_dir

    getPath = lambda *arglist: os.path.join(project_dir, *arglist)

    # Reading the model star file from relion
    model = in_parts.replace("_data.star", "_model.star")
    clstable = Table(fileName=getPath(model), tableName='model_classes')
    nrCls = int(clstable[-1].rlnReferenceImage.split("@")[0])

    # Find classes with >= 5% particles, accuracy < 10deg, < 10A
    good_cls = []
    for row in clstable:
        if (row.rlnClassDistribution >= 0.05 and
                row.rlnAccuracyRotations < 10 and
                row.rlnAccuracyTranslationsAngst < 10):
            good_cls.append(int(row.rlnReferenceImage.split("@")[0]))
    if DEBUG:
        print("Classes selected: ", good_cls)

    if len(good_cls) == 0:
        open(RELION_JOB_FAILURE_FILENAME, "w").close()
        exit(1)

    optics = Table(fileName=getPath(in_parts), tableName='optics')
    ptcls = Table(fileName=getPath(in_parts), tableName='particles')
    cols = ptcls.getColumnNames()
    out_ptcls = Table(columns=cols)
    
    for row in ptcls:
        if row.rlnClassNumber in good_cls:
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
        sel.addRow(1 if i in good_cls else 0)
    with open(getPath("backup_selection.star"), "w") as f:
        sel.writeStar(f, tableName="")

    end = time.time()
    diff = end - start
    print("Job duration = %dh %dmin %dsec \n" % (diff//3600, diff//60 % 60, diff % 60))


def main():
    """Change to the job working directory, then call run_job()"""
    help = """
External job to parse *_data.star from Class2D job and save particles with rlnClassDistribution >=0.05:
    external_job_sortcl2d.py --o External/best_cl2d --in_parts Class2D/job004/run_it020_data.star
"""
    parser = argparse.ArgumentParser(usage=help)
    parser.add_argument("--in_parts", help="Input *_data.star STAR file from Class2D job")
    parser.add_argument("--o", dest="out_dir", help="Output directory name")
    parser.add_argument("--j", dest="threads", help="Not used here. Required by relion")
    parser.add_argument("--pipeline_control", help="Not used here. Required by relion")

    args = parser.parse_args()

    if args.in_parts is None or args.out_dir is None:
        print("Error: --in_parts and --o are required params!")
        exit(1)

    if not args.in_parts.endswith("_data.star"):
        print("Error: --in_parts must point to a *_data.star file")
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

