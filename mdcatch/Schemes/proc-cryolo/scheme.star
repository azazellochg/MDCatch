

# version 30001

data_scheme_general

_rlnSchemeName                       Schemes/proc-cryolo/
_rlnSchemeCurrentNodeName            WAIT
 

# version 30001

data_scheme_floats

loop_ 
_rlnSchemeFloatVariableName #1
_rlnSchemeFloatVariableValue #2
_rlnSchemeFloatVariableResetValue #3
current_ini_size     0.000000     0.000000 
current_rest_size     0.000000     0.000000 
inibatch_size 10000.000000 10000.000000 
maxtime_hr    8.000000    8.000000
prev_rest_size     0.000000     0.000000 
wait_sec   60.000000   60.000000 
 

# version 30001

data_scheme_bools

loop_ 
_rlnSchemeBooleanVariableName #1
_rlnSchemeBooleanVariableValue #2
_rlnSchemeBooleanVariableResetValue #3
has_ctffind 0 0
do_prep 1 1 
do_2d 1 1 
do_3d 0 0 
has_larger_rest_size            0            0 
do_retrain_cryolo            1            1
has_cryolo_model            0            0
inibatch_big_enough            0            0
has_iniref            0            0  
 

# version 30001

data_scheme_strings

loop_ 
_rlnSchemeStringVariableName #1
_rlnSchemeStringVariableValue #2
_rlnSchemeStringVariableResetValue #3
ctffind_mics Schemes/prep/ctffind/micrographs_ctf.star Schemes/prep/ctffind/micrographs_ctf.star
ini_batch Schemes/proc-cryolo/split_ini/particles_split1.star Schemes/proc-cryolo/split_ini/particles_split1.star
particles  particles  particles 
rest_batch Schemes/proc-cryolo/extract_rest/particles.star Schemes/proc-cryolo/extract_rest/particles.star
cryolo_model Schemes/proc-cryolo/train_cryolo/fine_tuned_model.h5 Schemes/proc-cryolo/train_cryolo/fine_tuned_model.h5
iniref None None
myref undefined undefined
inimodel_output Schemes/proc-cryolo/inimodel3d/initial_model.mrc Schemes/proc-cryolo/inimodel3d/initial_model.mrc

# version 30001

data_scheme_operators

loop_ 
_rlnSchemeOperatorName #1
_rlnSchemeOperatorType #2
_rlnSchemeOperatorOutput #3
_rlnSchemeOperatorInput1 #4
_rlnSchemeOperatorInput2 #5
HAS_ctffind bool=file_exists has_ctffind ctffind_mics undefined
CHECK_ini    bool=ge inibatch_big_enough current_ini_size inibatch_size
CHECK_iniref  bool=file_exists has_iniref iniref  undefined 
COUNT_ini float=count_images current_ini_size   ini_batch  particles 
COUNT_restbatch float=count_images current_rest_size rest_batch  particles 
EXIT_maxtime exit_maxtime  undefined    maxtime_hr  undefined 
HAS_rest_increased    bool=gt has_larger_rest_size current_rest_size prev_rest_size 
HAS_cryolo_model bool=file_exists has_cryolo_model cryolo_model  undefined
SET_prev_rest_size  float=set prev_rest_size current_rest_size  undefined 
SET_myref_user string=set myref iniref undefined
SET_myref_inimodel string=set myref inimodel_output undefined
WAIT       wait  undefined   wait_sec  undefined 
 

# version 30001

data_scheme_jobs

loop_ 
_rlnSchemeJobNameOriginal #1
_rlnSchemeJobName #2
_rlnSchemeJobMode #3
_rlnSchemeJobHasStarted #4
select_mics select_mics continue    0
inipicker  inipicker   continue            0 
extract_ini extract_ini   continue            0 
split_ini split_ini   continue            0 
class2d_ini class2d_ini        new            0 
select_ini select_ini        new            0 
train_cryolo train_cryolo        new            0
restpicker restpicker   continue            0 
extract_rest extract_rest   continue            0 
class2d_rest class2d_rest        new            0 
select_rest select_rest        new            0 
inimodel3d inimodel3d        new            0 
refine3d   refine3d        new            0 
 

# version 30001

data_scheme_edges

loop_ 
_rlnSchemeEdgeInputNodeName #1
_rlnSchemeEdgeOutputNodeName #2
_rlnSchemeEdgeIsFork #3
_rlnSchemeEdgeOutputNodeNameIfTrue #4
_rlnSchemeEdgeBooleanVariable #5
WAIT HAS_ctffind              0  undefined  undefined 
HAS_ctffind WAIT             1 EXIT_maxtime has_ctffind
EXIT_maxtime select_mics              0  undefined  undefined 
select_mics restpicker            1 HAS_cryolo_model do_retrain_cryolo
HAS_cryolo_model  inipicker            1 restpicker has_cryolo_model
inipicker extract_ini            0  undefined  undefined 
extract_ini split_ini            0  undefined  undefined 
split_ini COUNT_ini            0  undefined  undefined 
COUNT_ini CHECK_ini            0  undefined  undefined 
CHECK_ini       WAIT            1 class2d_ini inibatch_big_enough 
class2d_ini select_ini            0  undefined  undefined 
select_ini train_cryolo            0  undefined  undefined
train_cryolo       WAIT            0  undefined  undefined
restpicker extract_rest           0  undefined  undefined 
extract_rest COUNT_restbatch       0  undefined  undefined 
COUNT_restbatch HAS_rest_increased            0  undefined  undefined 
HAS_rest_increased       WAIT            1 class2d_rest has_larger_rest_size 
class2d_rest select_rest            0  undefined  undefined 
select_rest   SET_prev_rest_size         0  undefined  undefined 
SET_prev_rest_size  WAIT       1 CHECK_iniref  do_3d 
CHECK_iniref inimodel3d 1 SET_myref_user has_iniref
inimodel3d SET_myref_inimodel            0  undefined  undefined 
SET_myref_inimodel   refine3d            0  undefined  undefined
SET_myref_user refine3d            0  undefined  undefined 
refine3d WAIT            0  undefined  undefined 
