
# version 30001

data_job

_rlnJobType                             2
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
       box        512 
   ctf_win         -1 
      dast        100 
     dfmax      50000 
     dfmin       5000 
    dfstep        500 
    do_EPA         No 
do_ignore_ctffind_params        Yes 
do_phaseshift   $$is_VPP 
  do_queue         No 
fn_ctffind_exe /usr/local/bin/ctffind 
fn_gctf_exe /public/EM/Gctf/bin/Gctf 
   gpu_ids         "" 
input_star_mics Schedules/preprocess-cryolo/motioncorr/corrected_micrographs.star
min_dedicated         24 
    nr_mpi         5
other_args         "" 
other_gctf_args         "" 
 phase_max        180 
 phase_min          0 
phase_step         10 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
    resmax          5 
    resmin         30 
slow_search         No 
use_ctffind4        Yes 
  use_gctf         No 
use_given_ps        Yes 
  use_noDW        No 
 
