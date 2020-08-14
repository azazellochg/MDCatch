
# version 30001

data_pipeline_general

_rlnPipeLineJobCounter                       1
 

# version 30001

data_pipeline_processes

loop_ 
_rlnPipeLineProcessName #1 
_rlnPipeLineProcessAlias #2 
_rlnPipeLineProcessType #3 
_rlnPipeLineProcessStatus #4 
Schedules/class2d/class2d_batch1/       None            8            1
Schedules/class2d/class2d_batch2/       None            8            1
Schedules/class2d/class2d_batch3/       None            8            1
Schedules/class2d/sort_cls2d/       None           99            1 
Schedules/class2d/cryolo_train/       None           99            1 
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/preprocess/extract/particles.star            3 
Schedules/class2d/class2d_batch1/run_it020_data.star            3
Schedules/class2d/class2d_batch1/run_it020_model.star            8
Schedules/class2d/class2d_batch2/run_it020_data.star            3
Schedules/class2d/class2d_batch2/run_it020_model.star            8
Schedules/class2d/class2d_batch3/run_it020_data.star            3
Schedules/class2d/class2d_batch3/run_it020_model.star            8
Schedules/class2d/sort_cls2d/particles_for_training.star            3 
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/class2d/class2d_batch3/run_it020_data.star Schedules/class2d/sort_cls2d/
Schedules/class2d/sort_cls2d/particles_for_training.star Schedules/class2d/cryolo_train/ 
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/class2d/class2d_batch1/ Schedules/class2d/class2d_batch1/run_it020_data.star
Schedules/class2d/class2d_batch1/ Schedules/class2d/class2d_batch1/run_it020_model.star
Schedules/class2d/class2d_batch2/ Schedules/class2d/class2d_batch2/run_it020_data.star
Schedules/class2d/class2d_batch2/ Schedules/class2d/class2d_batch2/run_it020_model.star
Schedules/class2d/class2d_batch3/ Schedules/class2d/class2d_batch3/run_it020_data.star
Schedules/class2d/class2d_batch3/ Schedules/class2d/class2d_batch3/run_it020_model.star
Schedules/class2d/sort_cls2d/ Schedules/class2d/sort_cls2d/particles_for_training.star 
