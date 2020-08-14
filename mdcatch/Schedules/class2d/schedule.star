
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
nr_cls1    20.000000    20.000000
nr_cls2    35.000000    35.000000
nr_cls3    50.000000    50.000000
  wait_sec    30.000000    30.000000
  delay1    30.000000    30.000000
  delay2    30.000000    30.000000
   zero     0.000000     0.000000
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
batch1_ready            0            0
batch2_ready            0            0
batch3_ready            0            0


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
extracted_batch1 Work/particles_batch1.star Work/particles_batch1.star
extracted_batch2 Work/particles_batch2.star Work/particles_batch2.star
extracted_batch3 Work/particles_batch3.star Work/particles_batch3.star


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
WAIT_delay1       wait  undefined   delay1  undefined
WAIT_delay2       wait  undefined   delay2  undefined
box_size=STAR_cryolobox_zero float=read_star box_size cryolobox       zero 
batch1_ready=EXISTS_extracted_batch1 bool=file_exists batch1_ready extracted_batch1  undefined
batch2_ready=EXISTS_extracted_batch2 bool=file_exists batch2_ready extracted_batch2  undefined
batch3_ready=EXISTS_extracted_batch3 bool=file_exists batch3_ready extracted_batch3  undefined
mask_diam=STAR_cryolodiam_zero float=read_star  mask_diam cryolodiam       zero


# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
class2d_batch1 class2d_batch1 continue     0
class2d_batch2 class2d_batch2 continue     0
class2d_batch3 class2d_batch3 continue     0
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
WAIT_wait_sec batch1_ready=EXISTS_extracted_batch1 0 undefined  undefined
batch1_ready=EXISTS_extracted_batch1 WAIT_wait_sec 1 mask_diam=STAR_cryolodiam_zero batch1_ready
mask_diam=STAR_cryolodiam_zero box_size=STAR_cryolobox_zero 0  undefined  undefined
box_size=STAR_cryolobox_zero class2d_batch1            0  undefined  undefined
class2d_batch1 batch2_ready=EXISTS_extracted_batch2 0 undefined undefined
batch2_ready=EXISTS_extracted_batch2 WAIT_delay1 1 class2d_batch2 batch2_ready
WAIT_delay1 batch2_ready=EXISTS_extracted_batch2 0 undefined undefined
class2d_batch2 batch3_ready=EXISTS_extracted_batch3 0 undefined undefined
batch3_ready=EXISTS_extracted_batch2 WAIT_delay2 1 class2d_batch3 batch3_ready
WAIT_delay2 batch3_ready=EXISTS_extracted_batch3 0 undefined undefined
class2d_batch3 sort_cls2d            0  undefined  undefined
sort_cls2d cryolo_train            0  undefined  undefined 
cryolo_train COPY_cryolo_model_src_TO_cryolo_model_dst            0  undefined  undefined 
