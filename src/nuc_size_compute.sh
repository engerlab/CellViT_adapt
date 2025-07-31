conda activate cellvit

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/HIPT_binary/x40_svs/cells.json

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/HIPT_pannuke/x40_svs/cells.json

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/JGH_cases/HIPT_pannuke/01/SS-16-03048/cells.json

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/JGH_cases/HIPT_pannuke/02/SS-16-11371/cells.json

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/SAM_binary/x40_svs/cells.json

python /Data/Yujing/CellViT_adapt/src/calculate_nuclei_areas_cellvit.py \
    --input /Data/Yujing/CellViT_adapt/output/SAM_pannuke/output/x40_svs/cells.json