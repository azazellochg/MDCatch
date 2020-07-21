
# version 30001

data_schedule_general

_rlnScheduleName                       Schedules/class2d_2nd/
_rlnScheduleCurrentNodeName            WAIT_wait_sec
 

# version 30001

data_schedule_floats

loop_ 
_rlnScheduleFloatVariableName #1 
_rlnScheduleFloatVariableValue #2 
_rlnScheduleFloatVariableResetValue #3 
  box_size   256.000000   256.000000 
box_size_bin    64.000000    64.000000 
cryolo_thresh     0.300000     0.300000 
 mask_diam   200.000000   200.000000 
nr_classes   100.000000   100.000000 
  wait_sec    30.000000    30.000000 
      zero     0.000000     0.000000 
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
mics_exist            0            0 
model_exists            0            0 
 

# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
cryolo_model Work/fine_tuned_model.h5 Work/fine_tuned_model.h5 
cryolo_model_src Schedules/class2d_2nd/cryolo_train/fine_tuned_model.h5 Schedules/class2d_2nd/cryolo_train/fine_tuned_model.h5 
 cryolobox Work/cryolo_params.star,cryolo,rlnOriginalImageSize Work/cryolo_params.star,cryolo,rlnOriginalImageSize 
cryoloboxbinned Work/cryolo_params.star,cryolo,rlnImageSize Work/cryolo_params.star,cryolo,rlnImageSize 
cryolodiam Work/cryolo_params.star,cryolo,rlnParticleDiameter Work/cryolo_params.star,cryolo,rlnParticleDiameter 
cryolostar Work/cryolo_params.star Work/cryolo_params.star 
mics_to_pick Work/micrographs_ctf.star Work/micrographs_ctf.star 
 

# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
COPY_cryolo_model_src_TO_cryolo_model  copy_file  undefined cryolo_model_src cryolo_model 
WAIT_wait_sec       wait  undefined   wait_sec  undefined 
box_size=STAR_cryolobox_zero float=read_star   box_size  cryolobox       zero 
box_size_bin=STAR_cryoloboxbinned_zero float=read_star box_size_bin cryoloboxbinned       zero 
mask_diam=STAR_cryolodiam_zero float=read_star  mask_diam cryolodiam       zero 
mics_exist=EXISTS_mics_to_pick bool=file_exists mics_exist mics_to_pick  undefined 
model_exists=EXISTS_cryolo_model bool=file_exists model_exists cryolo_model  undefined 
 

# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
   class2d    class2d   continue            0 
cryolopicker cryolopicker   continue            0 
   extract    extract   continue            0 
sort_cls2d sort_cls2d   continue            0 
cryolo_train cryolo_train   continue            0 
 

# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec model_exists=EXISTS_cryolo_model            0  undefined  undefined 
model_exists=EXISTS_cryolo_model WAIT_wait_sec            1 mics_exist=EXISTS_mics_to_pick model_exists 
mics_exist=EXISTS_mics_to_pick cryolopicker            0  undefined  undefined 
cryolopicker mask_diam=STAR_cryolodiam_zero            0  undefined  undefined 
mask_diam=STAR_cryolodiam_zero box_size_bin=STAR_cryoloboxbinned_zero            0  undefined  undefined 
box_size_bin=STAR_cryoloboxbinned_zero    extract            0  undefined  undefined 
   extract    class2d            0  undefined  undefined 
   class2d sort_cls2d            0  undefined  undefined 
sort_cls2d cryolo_train            0  undefined  undefined 
cryolo_train COPY_cryolo_model_src_TO_cryolo_model            0  undefined  undefined 
 
