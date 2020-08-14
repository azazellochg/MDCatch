
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
Schedules/round2/cryolopicker/       None           99            1
Schedules/round2/extract/       None            5            1
Schedules/round2/class2d/       None            8            1
Schedules/round2/sort_cls2d/       None           99            1
Schedules/round2/cryolo_train/       None           99            1
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/round2/class2d/run_it020_data.star            3
Schedules/round2/class2d/run_it020_model.star            8
Schedules/round2/extract/particles.star            3
Schedules/round2/cryolopicker/coords_suffix_autopick.star            2
Schedules/round2/sort_cls2d/particles_for_training.star            3
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/round2/cryolopicker/coords_suffix_autopick.star Schedules/round2/extract/
Schedules/round2/extract/particles.star Schedules/round2/class2d/
Schedules/round2/class2d/run_it020_data.star Schedules/round2/sort_cls2d/
Schedules/round2/sort_cls2d/particles_for_training.star Schedules/round2/cryolo_train/
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/round2/cryolopicker/ Schedules/round2/cryolopicker/coords_suffix_autopick.star
Schedules/round2/extract/ Schedules/round2/extract/particles.star
Schedules/round2/class2d/ Schedules/round2/class2d/run_it020_data.star
Schedules/round2/class2d/ Schedules/round2/class2d/run_it020_model.star
Schedules/round2/sort_cls2d/ Schedules/round2/sort_cls2d/particles_for_training.star
 
