
# version 30001

data_job

_rlnJobType                             4
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
    angpix         -1 
angpix_ref         -1 
do_amyloid         No 
do_ctf_autopick        Yes 
do_ignore_first_ctfpeak_autopick         No 
do_invert_refs        Yes 
    do_log         No 
do_pick_helical_segments         No 
  do_queue         No 
do_read_fom_maps         No 
  do_ref3d $$has_3drefs 
do_write_fom_maps         No 
fn_input_autopick Schedules/preprocess/ctffind/micrographs_ctf.star 
fn_ref3d_autopick $$3drefs_name 
fn_refs_autopick $$2drefs_name 
   gpu_ids          0 
helical_nr_asu          1 
helical_rise         -1 
helical_tube_kappa_max        0.1 
helical_tube_length_min         -1 
helical_tube_outer_diameter        200 
  highpass         -1 
log_adjust_thr          0 
log_diam_max        180 
log_diam_min        150 
log_invert         No 
log_maxres         20 
log_upper_thr        999 
   lowpass         20 
maxstddevnoise_autopick $$refpick_stddev_noise 
min_dedicated         24 
minavgnoise_autopick $$refpick_avg_noise 
mindist_autopick $$refpick_mind 
    nr_mpi          1 
other_args         "" 
particle_diameter         -1 
psi_sampling_autopick          5 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
ref3d_sampling "30 degrees" 
ref3d_symmetry $$3dref_sym 
    shrink          0 
threshold_autopick $$refpick_thr 
   use_gpu        Yes 
 
