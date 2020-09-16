
# version 30001

data_job

_rlnJobType                             0
_rlnJobIsContinue                       0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
        Cs       $$Cs 
        Q0        0.1 
    angpix   $$angpix 
beamtilt_x          0 
beamtilt_y          0 
  do_other         No 
  do_queue         No 
    do_raw        Yes 
fn_in_other    ref.mrc 
 fn_in_raw $$movies_wildcard 
    fn_mtf $$mtf_file 
is_multiframe        Yes 
        kV  $$voltage 
min_dedicated         24 
 node_type "Particle coordinates (*.box, *_pick.star)" 
optics_group_name $$optics_group 
optics_group_particles         "" 
other_args "--do_at_most $$do_at_most" 
      qsub       qsub 
qsubscript /public/EM/RELION/relion/bin/relion_qsub.csh 
 queuename    openmpi 
 
