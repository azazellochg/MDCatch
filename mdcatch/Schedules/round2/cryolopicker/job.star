
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
    fn_exe    /home/gsharov/soft/MDCatch/mdcatch/Schedules/external_job_cryolo.py 
  in_3dref         "" 
 in_coords         "" 
   in_mask         "" 
    in_mic         Work/micrographs_ctf.star
    in_mov         "" 
   in_part         "" 
min_dedicated          1 
nr_threads          1 
other_args         "" 
param10_label         "" 
param10_value         "" 
param1_label         gpu 
param1_value         0 
param2_label         threshold 
param2_value         $$cryolo_thresh 
param3_label         model 
param3_value         Work/fine_tuned_model.h5
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
 
