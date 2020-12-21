
# version 30001

data_job

_rlnJobType                            99
_rlnJobIsContinue                       0


# version 30001

data_joboptions_values

loop_
_rlnJobOptionVariable #1
_rlnJobOptionValue #2
  do_queue         No
    fn_exe         Schedules/external_job_cryoassess.py
  in_3dref         ""
 in_coords         ""
   in_mask         ""
    in_mic         ""
    in_mov         ""
   in_part         Schedules/class2d/class2d_last/run_it020_data.star
min_dedicated          1
nr_threads          1
other_args         ""
param10_label         ""
param10_value         ""
param1_label         gpu
param1_value         1
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
