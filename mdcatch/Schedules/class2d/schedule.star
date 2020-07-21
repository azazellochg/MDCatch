
# version 30001

data_schedule_general

_rlnScheduleName                       Schedules/class2d/
_rlnScheduleCurrentNodeName            WAIT_wait_sec
 

# version 30001

data_schedule_floats

loop_ 
_rlnScheduleFloatVariableName #1 
_rlnScheduleFloatVariableValue #2 
_rlnScheduleFloatVariableResetValue #3 
  box_size   256.000000   256.000000 
 mask_diam   200.000000   200.000000 
nr_classes_first    25.000000    25.000000 
  wait_sec    30.000000    30.000000 
      zero     0.000000     0.000000 
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
first_batch_ready            0            0 
has_done_cryolo            0            0 
 

# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
cryolo_model_dst Work/fine_tuned_model.h5 Work/fine_tuned_model.h5 
cryolo_model_src Schedules/class2d/cryolo_train/fine_tuned_model.h5 Schedules/class2d/cryolo_train/fine_tuned_model.h5 
cryolobox Work/cryolo_params.star,cryolo,rlnOriginalImageSize Work/cryolo_params.star,cryolo,rlnOriginalImageSize 
cryolodiam Work/cryolo_params.star,cryolo,rlnParticleDiameter Work/cryolo_params.star,cryolo,rlnParticleDiameter 
cryolostar Work/cryolo_params.star Work/cryolo_params.star 
extracted_star Work/particles.star Work/particles.star 
 

# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
COPY_cryolo_model_src_TO_cryolo_model_dst  copy_file  undefined cryolo_model_src cryolo_model_dst 
WAIT_wait_sec       wait  undefined   wait_sec  undefined 
box_size=STAR_cryolobox_zero float=read_star box_size cryolobox       zero 
first_batch_ready=EXISTS_extracted_star bool=file_exists first_batch_ready extracted_star  undefined 
has_done_cryolo=EXISTS_cryolostar bool=file_exists has_done_cryolo cryolostar  undefined 
mask_diam=STAR_cryolodiam_zero float=read_star  mask_diam cryolodiam       zero 
 

# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
class2d_first class2d_first   continue            0 
cryolo_train cryolo_train   continue            0 
sort_cls2d sort_cls2d   continue            0 
 

# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec has_done_cryolo=EXISTS_cryolostar            0  undefined  undefined 
has_done_cryolo=EXISTS_cryolostar WAIT_wait_sec            1 first_batch_ready=EXISTS_extracted_star has_done_cryolo 
first_batch_ready=EXISTS_extracted_star WAIT_wait_sec            1 mask_diam=STAR_cryolodiam_zero first_batch_ready 
mask_diam=STAR_cryolodiam_zero box_size=STAR_cryolobox_zero            0  undefined  undefined 
box_size=STAR_cryolobox_zero class2d_first            0  undefined  undefined 
class2d_first sort_cls2d            0  undefined  undefined 
sort_cls2d cryolo_train            0  undefined  undefined 
cryolo_train COPY_cryolo_model_src_TO_cryolo_model_dst            0  undefined  undefined 
 
