
# version 30001

data_pipeline_general

_rlnPipeLineJobCounter                       0
 

# version 30001

data_pipeline_processes

loop_ 
_rlnPipeLineProcessName #1 
_rlnPipeLineProcessAlias #2 
_rlnPipeLineProcessType #3 
_rlnPipeLineProcessStatus #4 
Schedules/class2d/class2d_firstbatch/       None            8            1 
Schedules/class2d/class2d_rest/       None            8            1 
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
 $$mybatch            3 
Schedules/class2d/class2d_firstbatch/run_it025_data.star            3 
Schedules/class2d/class2d_firstbatch/run_it025_model.star            8 
Schedules/class2d/class2d_rest/run_it025_data.star            3 
Schedules/class2d/class2d_rest/run_it025_model.star            8 
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
 $$mybatch Schedules/class2d/class2d_firstbatch/ 
 $$mybatch Schedules/class2d/class2d_rest/ 
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/class2d/class2d_firstbatch/ Schedules/class2d/class2d_firstbatch/run_it025_data.star 
Schedules/class2d/class2d_firstbatch/ Schedules/class2d/class2d_firstbatch/run_it025_model.star 
Schedules/class2d/class2d_rest/ Schedules/class2d/class2d_rest/run_it025_data.star 
Schedules/class2d/class2d_rest/ Schedules/class2d/class2d_rest/run_it025_model.star 
 
