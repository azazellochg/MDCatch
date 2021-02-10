
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
Schedules/preprocess-topaz/importmovies/       None            0            1
Schedules/preprocess-topaz/motioncorr/       None            1            1
Schedules/preprocess-topaz/ctffind/       None            2            1
Schedules/preprocess-topaz/topazpicker/       Schedules/preprocess-topaz/Autopick_topaz           99            1
Schedules/preprocess-topaz/extract/       None            5            1
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/preprocess-topaz/importmovies/movies.star            0
Schedules/preprocess-topaz/motioncorr/corrected_micrographs.star            1
Schedules/preprocess-topaz/motioncorr/logfile.pdf           13
Schedules/preprocess-topaz/ctffind/micrographs_ctf.star            1
Schedules/preprocess-topaz/ctffind/logfile.pdf           13
Schedules/preprocess-topaz/topazpicker/coords_suffix_topaz.star            2
Schedules/preprocess-topaz/extract/particles.star            3
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/preprocess-topaz/importmovies/movies.star Schedules/preprocess-topaz/motioncorr/
Schedules/preprocess-topaz/motioncorr/corrected_micrographs.star Schedules/preprocess-topaz/ctffind/
Schedules/preprocess-topaz/ctffind/micrographs_ctf.star Schedules/preprocess-topaz/topazpicker/
Schedules/preprocess-topaz/ctffind/micrographs_ctf.star Schedules/preprocess-topaz/extract/
Schedules/preprocess-topaz/topazpicker/coords_suffix_topaz.star Schedules/preprocess-topaz/extract/
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/preprocess-topaz/importmovies/ Schedules/preprocess-topaz/importmovies/movies.star
Schedules/preprocess-topaz/motioncorr/ Schedules/preprocess-topaz/motioncorr/corrected_micrographs.star
Schedules/preprocess-topaz/ctffind/ Schedules/preprocess-topaz/ctffind/micrographs_ctf.star
Schedules/preprocess-topaz/ctffind/ Schedules/preprocess-topaz/ctffind/logfile.pdf
Schedules/preprocess-topaz/topazpicker/ Schedules/preprocess-topaz/topazpicker/coords_suffix_topaz.star
Schedules/preprocess-topaz/extract/ Schedules/preprocess-topaz/extract/particles.star
 
