
# version 30001

data_job

_rlnJobType                             8
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
allow_coarser        No
ctf_intact_first_peak         No 
do_bimodal_psi        Yes 
do_combine_thru_disc         No 
do_ctf_correction        Yes 
do_fast_subsets         No 
  do_helix         No 
do_parallel_discio        Yes 
do_preread_images         No 
  do_queue         No 
do_restrict_xoff        Yes 
do_zero_mask        Yes 
dont_skip_align        Yes 
   fn_cont "" 
    fn_img Work/particles_batch.star
   gpu_ids        0:1 
helical_rise       4.75 
helical_tube_outer_diameter        200 
highres_limit         -1 
min_dedicated         24 
nr_classes $$nr_cls2
   nr_iter         20 
    nr_mpi          3
   nr_pool         30 
nr_threads          8 
offset_range          5 
offset_step          1 
other_args "--free_gpu_memory 2000"
particle_diameter $$mask_diam 
psi_sampling          6 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
 range_psi          6 
scratch_dir       /work 
 tau_fudge          2 
   use_gpu        Yes 
 
