
# version 30001

data_job

_rlnJobType                             7
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
discard_label rlnImageName 
discard_sigma          4 
do_discard         No 
  do_queue         No 
 do_random         No 
do_recenter        Yes 
do_regroup         No 
do_remove_duplicates         No 
do_select_values         No 
  do_split        Yes 
duplicate_threshold         30 
 fn_coords         "" 
   fn_data Schedules/preprocess/extract_refpick/particles.star 
    fn_mic         "" 
  fn_model         "" 
image_angpix         -1 
min_dedicated         24 
 nr_groups          1 
  nr_split         -1 
other_args         "" 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
select_label rlnCtfFigureOfMerit 
select_maxval      9999. 
select_minval     -9999. 
split_size $$subset_size 
 