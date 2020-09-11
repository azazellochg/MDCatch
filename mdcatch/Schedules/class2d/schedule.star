
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
count_parts    0.000000    0.000000
batch_min  5000.000000 5000.000000
batch_max 20000.000000 20000.000000
 mask_diam   0.000000   0.000000
nr_cls1    20.000000    20.000000
nr_cls2    50.000000    50.000000
  wait_sec    60.000000   60.000000
   zero     0.000000     0.000000
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3
batch_exists            0            0
batch_ready            0            0
batch_complete         0            0
size_provided          0            0


# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
partdiam Work/picker_params.star,picker,rlnParticleDiameter Work/picker_params.star,picker,rlnParticleDiameter
extracted_batch Work/particles_batch.star Work/particles_batch.star


# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
WAIT_wait_sec       wait  undefined   wait_sec  undefined
batch_exists=EXISTS_extracted_batch bool=file_exists batch_exists extracted_batch  undefined
batch_ready=count_parts_GT_batch_min bool=gt batch_ready count_parts batch_min
batch_complete=count_parts_GE_batch_max bool=ge batch_complete count_parts batch_max
count_parts=COUNT_IMGS_extracted_batch_undefined float=count_images count_parts extracted_batch undefined
size_provided=mask_diam_GT_zero bool=gt size_provided mask_diam zero
mask_diam=STAR_partdiam_zero float=read_star  mask_diam partdiam       zero
EXIT exit undefined undefined undefined


# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
class2d_first class2d_first overwrite     0
class2d_last class2d_last new     0
sort_cls2d sort_cls2d continue 0


# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec batch_exists=EXISTS_extracted_batch 0 undefined  undefined
batch_exists=EXISTS_extracted_batch WAIT_wait_sec 1 count_parts=COUNT_IMGS_extracted_batch_undefined batch_exists
count_parts=COUNT_IMGS_extracted_batch_undefined batch_ready=count_parts_GT_batch_min 0 undefined undefined
batch_ready=count_parts_GT_batch_min WAIT_wait_sec 1 size_provided=mask_diam_GT_zero batch_ready
size_provided=mask_diam_GT_zero mask_diam=STAR_partdiam_zero 1 batch_complete=count_parts_GE_batch_max size_provided
mask_diam=STAR_partdiam_zero batch_complete=count_parts_GE_batch_max 0 undefined  undefined
batch_complete=count_parts_GE_batch_max class2d_first 1 class2d_last batch_complete
class2d_first WAIT_wait_sec 0  undefined  undefined
class2d_last sort_cls2d 0  undefined  undefined
sort_cls2d EXIT 0 undefined undefined
