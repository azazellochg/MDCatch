
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
Schedules/preprocess-cryolo/importmovies/       None            0            1
Schedules/preprocess-cryolo/motioncorr/       None            1            1
Schedules/preprocess-cryolo/ctffind/       None            2            1
Schedules/preprocess-cryolo/cryolopicker/       Schedules/preprocess-cryolo/Autopick_cryolo           99            1
Schedules/preprocess-cryolo/extract/       None            5            1
 

# version 30001

data_pipeline_nodes

loop_ 
_rlnPipeLineNodeName #1 
_rlnPipeLineNodeType #2 
Schedules/preprocess-cryolo/importmovies/movies.star            0
Schedules/preprocess-cryolo/motioncorr/corrected_micrographs.star            1
Schedules/preprocess-cryolo/motioncorr/logfile.pdf           13
Schedules/preprocess-cryolo/ctffind/micrographs_ctf.star            1
Schedules/preprocess-cryolo/ctffind/logfile.pdf           13
Schedules/preprocess-cryolo/cryolopicker/coords_suffix_cryolo.star            2
Schedules/preprocess-cryolo/extract/particles.star            3
 

# version 30001

data_pipeline_input_edges

loop_ 
_rlnPipeLineEdgeFromNode #1 
_rlnPipeLineEdgeProcess #2 
Schedules/preprocess-cryolo/importmovies/movies.star Schedules/preprocess-cryolo/motioncorr/
Schedules/preprocess-cryolo/motioncorr/corrected_micrographs.star Schedules/preprocess-cryolo/ctffind/
Schedules/preprocess-cryolo/ctffind/micrographs_ctf.star Schedules/preprocess-cryolo/cryolopicker/
Schedules/preprocess-cryolo/ctffind/micrographs_ctf.star Schedules/preprocess-cryolo/extract/
Schedules/preprocess-cryolo/cryolopicker/coords_suffix_cryolo.star Schedules/preprocess-cryolo/extract/
 

# version 30001

data_pipeline_output_edges

loop_ 
_rlnPipeLineEdgeProcess #1 
_rlnPipeLineEdgeToNode #2 
Schedules/preprocess-cryolo/importmovies/ Schedules/preprocess-cryolo/importmovies/movies.star
Schedules/preprocess-cryolo/motioncorr/ Schedules/preprocess-cryolo/motioncorr/corrected_micrographs.star
Schedules/preprocess-cryolo/ctffind/ Schedules/preprocess-cryolo/ctffind/micrographs_ctf.star
Schedules/preprocess-cryolo/ctffind/ Schedules/preprocess-cryolo/ctffind/logfile.pdf
Schedules/preprocess-cryolo/cryolopicker/ Schedules/preprocess-cryolo/cryolopicker/coords_suffix_cryolo.star
Schedules/preprocess-cryolo/extract/ Schedules/preprocess-cryolo/extract/particles.star
 
