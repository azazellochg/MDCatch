
# version 30001

data_job

_rlnJobTypeLabel             relion.external
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0


# version 30001
data_joboptions_values
loop_
_rlnJobOptionVariable #1
_rlnJobOptionValue #2
do_queue         No
fn_exe ./external_job_cryolo.py
in_3dref             ""
in_coords            ""
in_mask              ""
in_mic Schemes/proc-cryolo/select_mics/micrographs.star
in_mov               ""
in_part              ""
min_dedicated        24
nr_threads            1
other_args           ""
param10_label        ""
param10_value        ""
param1_label        gpu
param1_value        0,1
param2_label   box_size
param2_value          0
param3_label      model
param3_value    $$cryolo_model
param4_label         ""
param4_value         ""
param5_label         ""
param5_value         ""
param6_label         ""
param6_value         ""
param7_label         ""
param7_value         ""
param8_label         ""
param8_value         ""
param9_label         ""
param9_value         ""
qsub       qsub
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh
queuename    openmpi

