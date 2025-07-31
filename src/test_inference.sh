
conda activate cellvit

cellvit-inference \
    --model HIPT \
    --nuclei_taxonomy pannuke \
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/output/HIPT_pannuke \
    --cpu_count 46 \
    --ray_worker 10 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /Data/Yujing/CellViT_adapt/test_database/x40_svs/JP2K-33003-2.svs \
    --wsi_mpp 0.25 \
    --wsi_magnification 40 #20

cellvit-inference \
    --model HIPT \
    --nuclei_taxonomy binary \
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/output/HIPT_binary_geojson \
    --geojson \
    --cpu_count 46 \
    --ray_worker 10 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /Data/Yujing/CellViT_adapt/test_database/x40_svs/JP2K-33003-2.svs \
    --wsi_mpp 0.25 \
    --wsi_magnification 40 #20


export CUDA_VISIBLE_DEVICES=0,1
export RAY_DISABLE_IMPORT_WARNING=1
cellvit-inference \
    --model SAM \
    --batch_size 16 \
    --outdir /Data/Yujing/CellViT_adapt/SAM/output \
    --cpu_count 46 \
    --ray_worker 10 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /Data/Yujing/CellViT_adapt/test_database/x40_svs/JP2K-33003-2.svs \
    --wsi_mpp 0.25 \
    --wsi_magnification 40 #20


cellvit-inference \
    --model SAM \
    --nuclei_taxonomy binary \
    --gpu 0 \
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/SAM_nuclei_binary_output \
    --cpu_count 28 \
    --ray_worker 14 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /Data/Yujing/CellViT_adapt/test_database/x40_svs/JP2K-33003-2.svs \
    --wsi_mpp 0.25 \
    --wsi_magnification 40

CUDA_VISIBLE_DEVICES=0,1 # to use multiple GPUs 
cellvit-inference \
    --model SAM \
    --nuclei_taxonomy binary \
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/output/SAM_binary \
    --cpu_count 32 \
    --ray_worker 10 \
    --ray_remote_cpus 10 \
    --debug \
    process_wsi \
    --wsi_path /Data/Yujing/CellViT_adapt/test_database/x40_svs/JP2K-33003-2.svs \
    --wsi_mpp 0.25 \
    --wsi_magnification 40 #20


#===================================================
# Try a JGH case
# ===================================================

cellvit-inference \
    --model HIPT \
    --nuclei_taxonomy pannuke \
    --gpu 0\
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/output/JGH_cases/HIPT_pannuke/01 \
    --cpu_count 32 \
    --ray_worker 10 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /media/yujing/One\ Touch3/DATA/Head\ and\ Neck_Sultanem/Organized_PT_Subfolders2/output_box1/SS-16-03048/1012096.svs \
    --wsi_magnification 40 #40 

# ===================================================
# run another one on another GPU 
cellvit-inference \
    --model HIPT \
    --nuclei_taxonomy pannuke \
    --gpu 0\
    --batch_size 32 \
    --outdir /Data/Yujing/CellViT_adapt/output/JGH_cases/HIPT_pannuke/02 \
    --cpu_count 32 \
    --ray_worker 10 \
    --ray_remote_cpus 2 \
    --debug \
    process_wsi \
    --wsi_path /media/yujing/One\ Touch3/DATA/Head\ and\ Neck_Sultanem/Organized_PT_Subfolders2/output_box1/SS-16-11371/1012088.svs \
    --wsi_magnification 40 #40
