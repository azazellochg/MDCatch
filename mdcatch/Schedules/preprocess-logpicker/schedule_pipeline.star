
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
Schedules/preprocess-logpicker/importmovies/       None            0            1
Schedules/preprocess-logpicker/motioncorr/       None            1            1
Schedules/preprocess-logpicker/ctffind/       None            2            1
Schedules/preprocess-logpicker/logpicker/       None           4            1
Schedules/preprocess-logpicker/extract/       None            5            1
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/preprocess-logpicker/importmovies/movies.star            0
Schedules/preprocess-logpicker/motioncorr/corrected_micrographs.star            1
Schedules/preprocess-logpicker/motioncorr/logfile.pdf           13
Schedules/preprocess-logpicker/ctffind/micrographs_ctf.star            1
Schedules/preprocess-logpicker/ctffind/logfile.pdf           13
Schedules/preprocess-logpicker/logpicker/coords_suffix_autopick.star            2
Schedules/preprocess-logpicker/logpicker/logfile.pdf           13
Schedules/preprocess-logpicker/extract/particles.star            3
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/preprocess-logpicker/importmovies/movies.star Schedules/preprocess-logpicker/motioncorr/
Schedules/preprocess-logpicker/motioncorr/corrected_micrographs.star Schedules/preprocess-logpicker/ctffind/
Schedules/preprocess-logpicker/ctffind/micrographs_ctf.star Schedules/preprocess-logpicker/logpicker/
Schedules/preprocess-logpicker/ctffind/micrographs_ctf.star Schedules/preprocess-logpicker/extract/
Schedules/preprocess-logpicker/logpicker/coords_suffix_autopick.star Schedules/preprocess-logpicker/extract/
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/preprocess-logpicker/importmovies/ Schedules/preprocess-logpicker/importmovies/movies.star
Schedules/preprocess-logpicker/motioncorr/ Schedules/preprocess-logpicker/motioncorr/corrected_micrographs.star
Schedules/preprocess-logpicker/ctffind/ Schedules/preprocess-logpicker/ctffind/micrographs_ctf.star
Schedules/preprocess-logpicker/ctffind/ Schedules/preprocess-logpicker/ctffind/logfile.pdf
Schedules/preprocess-logpicker/logpicker/ Schedules/preprocess-logpicker/logpicker/coords_suffix_autopick.star
Schedules/preprocess-logpicker/logpicker/ Schedules/preprocess-logpicker/logpicker/logfile.pdf
Schedules/preprocess-logpicker/extract/ Schedules/preprocess-logpicker/extract/particles.star
