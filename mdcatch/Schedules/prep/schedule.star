
# version 30001

data_schedule_general

_rlnScheduleName                       Schedules/prep/
_rlnScheduleCurrentNodeName            WAIT
 

# version 30001

data_schedule_floats

loop_ 
_rlnScheduleFloatVariableName #1 
_rlnScheduleFloatVariableValue #2 
_rlnScheduleFloatVariableResetValue #3 
do_at_most    5.000000    5.000000 
maxtime_hr    8.000000    8.000000
  wait_sec   0.000000   0.000000 
 

# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5 
EXIT_maxtime exit_maxtime  undefined    maxtime_hr  undefined 
WAIT       wait  undefined   wait_sec  undefined 
 

# version 30001

data_schedule_jobs

loop_ 
_rlnScheduleJobNameOriginal #1 
_rlnScheduleJobName #2 
_rlnScheduleJobMode #3 
_rlnScheduleJobHasStarted #4 
importmovies importmovies   continue            0 
motioncorr motioncorr   continue            0 
   ctffind    ctffind   continue            0 


# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
      WAIT EXIT_maxtime            0  undefined  undefined 
EXIT_maxtime importmovies            0  undefined  undefined 
importmovies motioncorr            0  undefined  undefined 
motioncorr    ctffind            0  undefined  undefined 
   ctffind WAIT            0  undefined  undefined 
  
