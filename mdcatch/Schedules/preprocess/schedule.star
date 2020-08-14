
# version 30001

data_schedule_general

_rlnScheduleName                       Schedules/preprocess/
_rlnScheduleCurrentNodeName            WAIT_wait_sec
 

# version 30001

data_schedule_floats

loop_ 
_rlnScheduleFloatVariableName #1 
_rlnScheduleFloatVariableValue #2 
_rlnScheduleFloatVariableResetValue #3 
        Cs     2.700000     2.700000
    angpix     1.000000     1.000000
    batch1  10000.000000  10000.000000
    batch2  20000.000000  20000.000000
  box_size   256.000000   256.000000
box_size_bin    64.000000    64.000000 
count_parts     0.000000     0.000000
count_mics      0.000000     0.000000
count_mics_curr      0.000000     0.000000
cryolo_thresh     0.300000     0.300000 
do_at_most     5.000000     5.000000 
 dose_rate     1.000000     1.000000
 mask_diam   200.000000   200.000000 
 mask_diam_px  200.000000   200.000000 
motioncorr_bin     1.000000     1.000000 
   voltage   300.000000   200.000000
  wait_sec   100.000000   100.000000
      tmp     0.000000     0.000000
     zero     0.000000     0.000000


# version 30001

data_schedule_bools

loop_ 
_rlnScheduleBooleanVariableName #1 
_rlnScheduleBooleanVariableValue #2 
_rlnScheduleBooleanVariableResetValue #3 
batch1_ready            0            0
batch2_ready            0            0
has_copied_cryolostar   0            0
has_copied_ptcls1            0            0
has_copied_ptcls2            0            0
finished_batches        0            0
    is_VPP            0            0
    end               0            0
 

# version 30001

data_schedule_strings

loop_ 
_rlnScheduleStringVariableName #1 
_rlnScheduleStringVariableValue #2 
_rlnScheduleStringVariableResetValue #3 
 cryolobox Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnOriginalImageSize Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnOriginalImageSize 
cryoloboxbinned Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnImageSize Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnImageSize 
cryolodiam Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnParticleDiameter Schedules/preprocess/cryolopicker/output_for_relion.star,cryolo,rlnParticleDiameter 
cryolostar Schedules/preprocess/cryolopicker/output_for_relion.star Schedules/preprocess/cryolopicker/output_for_relion.star 
cryolostar_copy Work/cryolo_params.star Work/cryolo_params.star 
defect_file         ""         "" 
extracted_batch1 Work/particles_batch1.star Work/particles_batch1.star
extracted_batch2 Work/particles_batch2.star Work/particles_batch2.star
extracted_star Schedules/preprocess/extract/particles.star Schedules/preprocess/extract/particles.star
   gainref Movies/gain.mrc Movies/gain.mrc 
mics_to_pick_dst Work/micrographs_ctf.star Work/micrographs_ctf.star 
mics_to_pick_src Schedules/preprocess/ctffind/micrographs_ctf.star Schedules/preprocess/ctffind/micrographs_ctf.star 
movies_wildcard Movies/*.tiff Movies/*.tiff 
  mtf_file mtf_K3_300kv_nocds.star mtf_K3_300kv_nocds.star
optics_group  opticsGroup1  opticsGroup1
micrographs micrographs micrographs


# version 30001

data_schedule_operators

loop_ 
_rlnScheduleOperatorName #1 
_rlnScheduleOperatorType #2 
_rlnScheduleOperatorOutput #3 
_rlnScheduleOperatorInput1 #4 
_rlnScheduleOperatorInput2 #5
has_copied_cryolostar=EXISTS_cryolostar_copy bool=file_exists has_copied_cryolostar cryolostar_copy  undefined
COPY_cryolostar_TO_cryolostar_copy  copy_file  undefined cryolostar cryolostar_copy 
COPY_extracted_star_TO_extracted_batch1  copy_file  undefined extracted_star extracted_batch1
COPY_extracted_star_TO_extracted_batch2  copy_file  undefined extracted_star extracted_batch2
COPY_mics_to_pick_src_TO_mics_to_pick_dst  copy_file  undefined mics_to_pick_src mics_to_pick_dst
WAIT_wait_sec       wait  undefined   wait_sec  undefined
box_size=STAR_cryolobox_zero float=read_star   box_size  cryolobox       zero
box_size_bin=STAR_cryoloboxbinned_zero float=read_star box_size_bin cryoloboxbinned       zero
count_mics_curr=COUNT_IMGS_mics_to_pick_src_micrographs float=count_images count_mics_curr mics_to_pick_src  micrographs
count_mics=SET_count_mics_curr float=set count_mics count_mics_curr  undefined
count_parts=COUNT_IMGS_extracted_star_undefined float=count_images count_parts extracted_star  undefined 
batch1_ready=count_parts_GE_batch1    bool=ge batch1_ready count_parts      batch1
batch2_ready=count_parts_GE_batch2    bool=ge batch2_ready count_parts      batch2
has_copied_ptcls1=EXISTS_extracted_batch1 bool=file_exists has_copied_ptcls1 extracted_batch1  undefined
has_copied_ptcls2=EXISTS_extracted_batch2 bool=file_exists has_copied_ptcls2 extracted_batch2  undefined
mask_diam=STAR_cryolodiam_zero float=read_star  mask_diam cryolodiam       zero
tmp=DIVIDE_mask_diam_angpix float=divide  tmp mask_diam  angpix 
mask_diam_px=DIVIDE_tmp_motioncorr_bin float=divide mask_diam_px tmp motioncorr_bin 
finished_batches=EXISTS_extracted_batch2 bool=file_exists finished_batches extracted_batch2  undefined
end=count_mics_curr_EQ_count_mics bool=eq end count_mics_curr count_mics
EXIT exit undefined undefined undefined


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
 cryolopicker cryolopicker   continue            0
   extract    extract   continue            0


# version 30001

data_schedule_edges

loop_ 
_rlnScheduleEdgeInputNodeName #1 
_rlnScheduleEdgeOutputNodeName #2 
_rlnScheduleEdgeIsFork #3 
_rlnScheduleEdgeOutputNodeNameIfTrue #4 
_rlnScheduleEdgeBooleanVariable #5 
WAIT_wait_sec importmovies            0  undefined  undefined 
importmovies motioncorr            0  undefined  undefined 
motioncorr    ctffind            0  undefined  undefined 
ctffind COPY_mics_to_pick_src_TO_mics_to_pick_dst            0 undefined undefined
COPY_mics_to_pick_src_TO_mics_to_pick_dst finished_batches=EXISTS_extracted_batch2 0 undefined undefined
finished_batches=EXISTS_extracted_batch2 cryolopicker            1 count_mics_curr=COUNT_IMGS_mics_to_pick_src_micrographs finished_batches
count_mics_curr=COUNT_IMGS_mics_to_pick_src_micrographs end=count_mics_curr_EQ_count_mics 0 undefined undefined
end=count_mics_curr_EQ_count_mics count_mics=SET_count_mics_curr 1 EXIT end
count_mics=SET_count_mics_curr importmovies 0 undefined undefined
cryolopicker has_copied_cryolostar=EXISTS_cryolostar_copy 0 undefined undefined
has_copied_cryolostar=EXISTS_cryolostar_copy COPY_cryolostar_TO_cryolostar_copy  1  extract  has_copied_cryolostar
COPY_cryolostar_TO_cryolostar_copy mask_diam=STAR_cryolodiam_zero 0  undefined  undefined
mask_diam=STAR_cryolodiam_zero tmp=DIVIDE_mask_diam_angpix 0  undefined  undefined
tmp=DIVIDE_mask_diam_angpix mask_diam_px=DIVIDE_tmp_motioncorr_bin   0  undefined  undefined 
mask_diam_px=DIVIDE_tmp_motioncorr_bin box_size=STAR_cryolobox_zero   0  undefined  undefined
box_size=STAR_cryolobox_zero box_size_bin=STAR_cryoloboxbinned_zero   0  undefined  undefined
box_size_bin=STAR_cryoloboxbinned_zero extract 0  undefined  undefined
extract count_parts=COUNT_IMGS_extracted_star_undefined   0  undefined  undefined
count_parts=COUNT_IMGS_extracted_star_undefined batch2_ready=count_parts_GE_batch2   0  undefined  undefined
batch2_ready=count_parts_GE_batch2 batch1_ready=count_parts_GE_batch1 1 has_copied_ptcls2=EXISTS_extracted_batch2 batch2_ready
batch1_ready=count_parts_GE_batch1 WAIT_wait_sec 1 has_copied_ptcls1=EXISTS_extracted_batch1 batch1_ready
has_copied_ptcls1=EXISTS_extracted_batch1 COPY_extracted_star_TO_extracted_batch1 1 WAIT_wait_sec has_copied_ptcls1
COPY_extracted_star_TO_extracted_batch1 WAIT_wait_sec 0  undefined  undefined
has_copied_ptcls2=EXISTS_extracted_batch2 COPY_extracted_star_TO_extracted_batch2 1 WAIT_wait_sec has_copied_ptcls2
COPY_extracted_star_TO_extracted_batch2 WAIT_wait_sec 0  undefined  undefined
