
# version 30001

data_job

_rlnJobType                             1
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
   bfactor        150 
bin_factor $$motioncorr_bin 
do_dose_weighting        Yes 
do_own_motioncor        Yes 
  do_queue         No 
dose_per_frame $$dose_rate 
first_frame_sum          1 
 fn_defect         $$defect_file 
fn_gain_ref  $$gainref 
fn_motioncor2_exe /public/EM/MOTIONCOR2/MotionCor2 
 gain_flip "No flipping (0)" 
  gain_rot "No rotation (0)" 
   gpu_ids        0:1 
group_for_ps          4 
group_frames          1 
input_star_mics Schedules/preprocess/importmovies/movies.star 
last_frame_sum         -1 
min_dedicated         24 
    nr_mpi          1 
nr_threads         12 
other_args "--do_at_most $$do_at_most" 
other_motioncor2_args         "" 
   patch_x          5 
   patch_y          5 
pre_exposure          0 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
 save_noDW         No 
   save_ps        Yes 
 
