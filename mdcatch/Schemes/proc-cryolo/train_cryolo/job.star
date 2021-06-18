
# version 30001

data_job

_rlnJobTypeLabel             relion.external
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_
_rlnJobOptionVariable #1
_rlnJobOptionValue #2
do_queue         No
fn_exe ./external_job_cryolo_train.py
in_3dref             ""
in_coords            ""
in_mask              ""
in_mic               ""
in_mov               ""
in_part Schemes/proc-cryolo/select_ini/particles.star
min_dedicated        24
nr_threads            1
other_args           ""
param10_label        ""
param10_value        ""
param1_label        gpu
param1_value          0
param2_label         ""
param2_value         ""
param3_label         ""
param3_value         ""
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
