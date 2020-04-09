
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
Schedules/preprocess/importmovies/       None            0            1 
Schedules/preprocess/motioncorr/       None            1            1 
Schedules/preprocess/ctffind/       None            2            1 
Schedules/preprocess/logpicker/       None            4            1 
Schedules/preprocess/refpicker/       None            4            1 
Schedules/preprocess/extract_logpick/       None            5            1 
Schedules/preprocess/extract_refpick/       None            5            1 
Schedules/preprocess/split_logpick/       None            7            1 
Schedules/preprocess/split_refpick/       None            7            1 
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/preprocess/importmovies/movies.star            0 
Schedules/preprocess/motioncorr/corrected_micrographs.star            1 
Schedules/preprocess/motioncorr/logfile.pdf           13 
Schedules/preprocess/ctffind/micrographs_ctf.star            1 
Schedules/preprocess/ctffind/logfile.pdf           13 
Schedules/preprocess/logpicker/coords_suffix_autopick.star            2 
Schedules/preprocess/logpicker/logfile.pdf           13 
$$2drefs_name            5 
Schedules/preprocess/refpicker/coords_suffix_autopick.star            2 
Schedules/preprocess/refpicker/logfile.pdf           13 
Schedules/preprocess/extract_logpick/particles.star            3 
Schedules/preprocess/extract_refpick/particles.star            3 
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/preprocess/importmovies/movies.star Schedules/preprocess/motioncorr/ 
Schedules/preprocess/motioncorr/corrected_micrographs.star Schedules/preprocess/ctffind/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/logpicker/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/refpicker/ 
$$2drefs_name Schedules/preprocess/refpicker/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/extract_logpick/ 
Schedules/preprocess/logpicker/coords_suffix_autopick.star Schedules/preprocess/extract_logpick/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/extract_refpick/ 
Schedules/preprocess/refpicker/coords_suffix_autopick.star Schedules/preprocess/extract_refpick/ 
Schedules/preprocess/extract_logpick/particles.star Schedules/preprocess/split_logpick/ 
Schedules/preprocess/extract_refpick/particles.star Schedules/preprocess/split_refpick/ 
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/preprocess/importmovies/ Schedules/preprocess/importmovies/movies.star 
Schedules/preprocess/motioncorr/ Schedules/preprocess/motioncorr/corrected_micrographs.star 
Schedules/preprocess/ctffind/ Schedules/preprocess/ctffind/micrographs_ctf.star 
Schedules/preprocess/ctffind/ Schedules/preprocess/ctffind/logfile.pdf 
Schedules/preprocess/logpicker/ Schedules/preprocess/logpicker/coords_suffix_autopick.star 
Schedules/preprocess/logpicker/ Schedules/preprocess/logpicker/logfile.pdf 
Schedules/preprocess/refpicker/ Schedules/preprocess/refpicker/coords_suffix_autopick.star 
Schedules/preprocess/refpicker/ Schedules/preprocess/refpicker/logfile.pdf 
Schedules/preprocess/extract_logpick/ Schedules/preprocess/extract_logpick/particles.star 
Schedules/preprocess/extract_refpick/ Schedules/preprocess/extract_refpick/particles.star 
 
