
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
Schedules/preprocess/importmovies/       None            0            1 
Schedules/preprocess/motioncorr/       None            1            1 
Schedules/preprocess/ctffind/       None            2            1 
Schedules/preprocess/cryolopicker/       None           99            1 
Schedules/preprocess/extract/       None            5            1 
 

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
Schedules/preprocess/cryolopicker/coords_suffix_autopick.star            2 
Schedules/preprocess/extract/particles.star            3 
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/preprocess/importmovies/movies.star Schedules/preprocess/motioncorr/ 
Schedules/preprocess/motioncorr/corrected_micrographs.star Schedules/preprocess/ctffind/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/cryolopicker/ 
Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/extract/ 
Schedules/preprocess/cryolopicker/coords_suffix_autopick.star Schedules/preprocess/extract/ 
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/preprocess/importmovies/ Schedules/preprocess/importmovies/movies.star 
Schedules/preprocess/motioncorr/ Schedules/preprocess/motioncorr/corrected_micrographs.star 
Schedules/preprocess/ctffind/ Schedules/preprocess/ctffind/micrographs_ctf.star 
Schedules/preprocess/ctffind/ Schedules/preprocess/ctffind/logfile.pdf 
Schedules/preprocess/cryolopicker/ Schedules/preprocess/cryolopicker/coords_suffix_autopick.star 
Schedules/preprocess/extract/ Schedules/preprocess/extract/particles.star 
 
