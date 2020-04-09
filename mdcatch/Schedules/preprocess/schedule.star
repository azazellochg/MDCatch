
# version 30001

data_schedule_general

_rlnScheduleName                       Schedules/preprocess/
_rlnScheduleCurrentNodeName            WAIT_wait_sec
 

# version 30001

data_schedule_floats

loop_ 
_rlnScheduleFloatVariableName #1 
_rlnScheduleFloatVariableValue #2 
_rlnScheduleFloatVariableResetValue #3 
        Cs     1.400000     1.400000 
  LOG_maxd   180.000000   180.000000 
  LOG_mind   150.000000   150.000000 
LOG_thresh     0.000000     0.000000 
    angpix     0.885000     0.885000 
  box_size   256.000000   256.000000 
boxsize_logpick    64.000000    64.000000 
boxsize_refpick   128.000000   128.000000 
do_at_most     5.000000     5.000000 
 dose_rate     1.277000     1.277000 
 mask_diam   200.000000   200.000000 
motioncorr_bin     1.000000     1.000000 
refpick_avg_noise   -999.00000   -999.00000 
refpick_mind   130.000000   130.000000 
refpick_stddev_noise     1.100000     1.100000 
refpick_thr     0.400000     0.400000 
subset_size  5000.000000  5000.000000 
   voltage   200.000000   200.000000 
  wait_sec   180.000000   180.000000 
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
do_until_ctf            0            0 
has_2drefs            0            0 
has_3drefs            0            0 
  has_refs            0            0 
    is_VPP            0            0 
 

# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
2drefs_name refs2d_forpicking.star refs2d_forpicking.star 
 3dref_sym         C1         C1 
3drefs_name ref3d_forpicking.mrc ref3d_forpicking.mrc 
   gainref Movies/gain.mrc Movies/gain.mrc 
   defect_file Movies/defects.txt "" 
movies_wildcard Movies/*.tiff Movies/*.tiff 
  mtf_file /lmb/home/scheres/mtf_k2_300kV.star /lmb/home/scheres/mtf_k2_300kV.star 
optics_group  mydataset  mydataset 
split_log_dst Batches/logpick/. Batches/logpick/. 
split_log_src Schedules/preprocess/split_logpick/particles_split*.star Schedules/preprocess/split_logpick/particles_split*.star 
split_ref_dst Batches/refpick/. Batches/refpick/. 
split_ref_src Schedules/preprocess/split_refpick/particles_split*.star Schedules/preprocess/split_refpick/particles_split*.star 
 

# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
COPY_split_log_src_TO_split_log_dst  copy_file  undefined split_log_src split_log_dst 
COPY_split_ref_src_TO_split_ref_dst  copy_file  undefined split_ref_src split_ref_dst 
WAIT_wait_sec       wait  undefined   wait_sec  undefined 
has_2drefs=EXISTS_2drefs_name bool=file_exists has_2drefs 2drefs_name  undefined 
has_3drefs=EXISTS_3drefs_name bool=file_exists has_3drefs 3drefs_name  undefined 
has_refs=has_2drefs_OR_has_3drefs    bool=or   has_refs has_2drefs has_3drefs 
 

# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
   ctffind    ctffind   continue            0 
extract_logpick extract_logpick   continue            0 
extract_refpick extract_refpick   continue            0 
importmovies importmovies   continue            0 
 logpicker  logpicker   continue            0 
motioncorr motioncorr   continue            0 
 refpicker  refpicker   continue            0 
split_logpick split_logpick   continue            0 
split_refpick split_refpick   continue            0 
 

# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec importmovies            0  undefined  undefined 
importmovies motioncorr            0  undefined  undefined 
motioncorr    ctffind            0  undefined  undefined 
   ctffind has_2drefs=EXISTS_2drefs_name            1 WAIT_wait_sec do_until_ctf 
has_2drefs=EXISTS_2drefs_name has_3drefs=EXISTS_3drefs_name            0  undefined  undefined 
has_3drefs=EXISTS_3drefs_name has_refs=has_2drefs_OR_has_3drefs            0  undefined  undefined 
has_refs=has_2drefs_OR_has_3drefs  logpicker            1  refpicker   has_refs 
 logpicker extract_logpick            0  undefined  undefined 
 refpicker extract_refpick            0  undefined  undefined 
extract_logpick split_logpick            0  undefined  undefined 
extract_refpick split_refpick            0  undefined  undefined 
split_logpick COPY_split_log_src_TO_split_log_dst            0  undefined  undefined 
split_refpick COPY_split_ref_src_TO_split_ref_dst            0  undefined  undefined 
COPY_split_log_src_TO_split_log_dst WAIT_wait_sec            0  undefined  undefined 
COPY_split_ref_src_TO_split_ref_dst WAIT_wait_sec            0  undefined  undefined 
 
