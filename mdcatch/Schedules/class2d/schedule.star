
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
batch_size  5000.000000  5000.000000 
    ibatch     1.000000     1.000000 
 mask_diam   200.000000   200.000000 
mybatch_size     0.000000     0.000000 
nr_batches     0.000000     0.000000 
nr_classes   100.000000   100.000000 
       one     1.000000     1.000000 
prev_mybatch_size     0.000000     0.000000 
  wait_sec   180.000000   180.000000 
 

# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
has_done_batches            0            0 
is_big_enough            0            0 
is_bigger_mybatch            0            0 
is_done_first            0            0 
  is_first            0            0 
 

# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
batch_files Batches/logpick/particles_split*.star Batches/logpick/particles_split*.star 
   batches  undefined  undefined 
   mybatch  undefined  undefined 
 particles  particles  particles 
 

# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
WAIT_wait_sec       wait  undefined   wait_sec  undefined 
batches=GLOB_batch_files string=glob    batches batch_files  undefined 
has_done_batches=ibatch_GT_nr_batches    bool=gt has_done_batches     ibatch nr_batches 
ibatch=SET_one  float=set     ibatch        one  undefined 
ibatch=ibatch_PLUS_one float=plus     ibatch     ibatch        one 
is_big_enough=mybatch_size_GE_batch_size    bool=ge is_big_enough mybatch_size batch_size 
is_bigger_mybatch=mybatch_size_GT_prev_mybatch_size    bool=gt is_bigger_mybatch mybatch_size prev_mybatch_size 
is_done_first=mybatch_size_GE_batch_size    bool=ge is_done_first mybatch_size batch_size 
is_first=ibatch_EQ_one    bool=eq   is_first     ibatch        one 
mybatch=NTH_WORD_batches_ibatch string=nth_word    mybatch    batches     ibatch 
mybatch_size=COUNT_IMGS_mybatch_undefined float=count_images mybatch_size    mybatch  particles 
nr_batches=COUNT_WORDS_batches float=count_words nr_batches    batches  undefined 
prev_mybatch_size=SET_mybatch_size  float=set prev_mybatch_size mybatch_size  undefined 
 

# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
class2d_firstbatch class2d_firstbatch  overwrite            0 
class2d_rest class2d_rest        new            0 
 

# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec batches=GLOB_batch_files            0  undefined  undefined 
batches=GLOB_batch_files nr_batches=COUNT_WORDS_batches            0  undefined  undefined 
nr_batches=COUNT_WORDS_batches has_done_batches=ibatch_GT_nr_batches            0  undefined  undefined 
has_done_batches=ibatch_GT_nr_batches mybatch=NTH_WORD_batches_ibatch            1 WAIT_wait_sec has_done_batches 
mybatch=NTH_WORD_batches_ibatch mybatch_size=COUNT_IMGS_mybatch_undefined            0  undefined  undefined 
mybatch_size=COUNT_IMGS_mybatch_undefined is_first=ibatch_EQ_one            0  undefined  undefined 
is_first=ibatch_EQ_one is_big_enough=mybatch_size_GE_batch_size            1 is_bigger_mybatch=mybatch_size_GT_prev_mybatch_size   is_first 
is_big_enough=mybatch_size_GE_batch_size WAIT_wait_sec            1 class2d_rest is_big_enough 
class2d_rest ibatch=ibatch_PLUS_one            0  undefined  undefined 
ibatch=ibatch_PLUS_one WAIT_wait_sec            0  undefined  undefined 
is_bigger_mybatch=mybatch_size_GT_prev_mybatch_size WAIT_wait_sec            1 class2d_firstbatch is_bigger_mybatch 
class2d_firstbatch prev_mybatch_size=SET_mybatch_size            0  undefined  undefined 
prev_mybatch_size=SET_mybatch_size is_done_first=mybatch_size_GE_batch_size            0  undefined  undefined 
is_done_first=mybatch_size_GE_batch_size WAIT_wait_sec            1 ibatch=ibatch_PLUS_one is_done_first 
 
