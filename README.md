# CellViT Nuclei Area Analysis

This repository contains tools for analyzing nuclei areas and types from CellViT inference results, supporting both binary and multi-class cell type classification (e.g., PanNuke).

For detailed documentation of CellViT inference and model usage, please refer to the [CellViT documentation](https://tio-ikim.github.io/CellViT-Inference/getting-started.html), their [GitHub repository](https://github.com/TIO-IKIM/CellViT), and the [CellViT paper](https://www.sciencedirect.com/science/article/pii/S1361841524000689).

## Overview

The `calculate_nuclei_areas_cellvit.py` script processes CellViT JSON output to compute detailed nuclei morphometrics and cell type statistics. It works with both binary classification (nuclei vs background) and multi-class classification (Neoplastic, Inflammatory, Connective, Dead, Epithelial).

## Input Data Structure

### Primary Input: `cells.json`
Contains the complete cell detection and segmentation results:
```json
{
  "wsi_metadata": {
    "base_magnification": 40,
    "base_mpp": 0.25,
    "patch_size": 1024,
    ...
  },
  "type_map": {
    "1": "Neoplastic",
    "2": "Inflammatory", 
    "3": "Connective",
    "4": "Dead",
    "5": "Epithelial"
  },
  "cells": [
    {
      "bbox": [[958,25816],[976,25832]],           // Bounding box coordinates
      "centroid": [25823.0,966.0],                 // Center point [y, x]
      "contour": [[25816,958],[25816,962],...],    // Polygon vertices [y, x]
      "type_prob": 0.9549180288732868,             // Classification confidence
      "type": 3,                                   // Cell type ID
      "patch_coordinates": [1,26],                 // Which image patch
      "cell_status": 2,                           // Processing status
      "offset_global": [928,24928],               // Global offset
      "edge_position": false                       // Whether at patch edge
    }
  ]
}
```

### Secondary Input: `cell_detection.json` (for type mapping)
Located in the same directory as `cells.json`, provides cell type definitions:
```json
{
  "type_map": {
    "1": "Neoplastic",
    "2": "Inflammatory",
    "3": "Connective", 
    "4": "Dead",
    "5": "Epithelial"
  }
}
```

## Computation Process

### 1. Data Loading
- Loads cell data from `cells.json`
- Dynamically loads cell type mappings from `cell_detection.json` 
- Falls back to metadata type_map if cell_detection.json not found

### 2. Area Calculation
For each detected cell:

1. **Extract Contour**: Get polygon vertices from `contour` field
2. **Coordinate Conversion**: Convert from CellViT format [y,x] to Shapely format [x,y]
3. **Polygon Creation**: Create geometric polygon using Shapely library
4. **Area Computation**: 
   - Pixel area = `polygon.area` (exact geometric area, not bounding box)
   - Real area = `pixel_area × (pixel_size_um)²`
5. **Radius Calculation**: Equivalent circle radius = `√(area/π)`

### 3. Type Assignment
- Extract `type` field from each cell (integer ID)
- Map to human-readable names using `type_map`
- Associate area measurements with cell type

### 4. Statistical Analysis
- Compute descriptive statistics per cell type
- Calculate overall population statistics
- Generate percentile distributions

## Output Files

### 1. Detailed Results: `nuclei_areas_detailed.csv`

Per-cell measurements with the following columns:

| Column | Description | Units | Source/Computation | Example |
|--------|-------------|-------|-------------------|---------|
| `nuclei_id` | Sequential cell identifier | - | Row number (0-indexed) | 0, 1, 2, ... |
| `area_pixels` | Cell area in pixels | pixels² | `polygon.area` from contour | 215.5 |
| `area_um2` | Cell area in micrometers | μm² | `area_pixels × (pixel_size_um)²` | 13.46875 |
| `radius_pixels` | Equivalent circle radius | pixels | `√(area_pixels/π)` | 8.282 |
| `radius_um` | Equivalent circle radius | μm | `√(area_um2/π)` | 2.071 |
| `cell_type` | Cell type ID | - | `cell['type']` from JSON | 1, 2, 3 |
| `type_prob` | Classification confidence | 0-1 | `cell['type_prob']` from JSON | 0.955 |
| `centroid_x` | Cell center X coordinate | pixels | `cell['centroid'][1]` (x from [y,x]) | 966.0 |
| `centroid_y` | Cell center Y coordinate | pixels | `cell['centroid'][0]` (y from [y,x]) | 25823.0 |

**Example entries:**

*Binary Classification (all nuclei type 1):*
```csv
nuclei_id,area_pixels,area_um2,radius_pixels,radius_um,cell_type,type_prob,centroid_x,centroid_y
0,215.5,13.46875,8.282,2.071,1,0.955,966.0,25823.0
1,324.5,20.28125,10.163,2.541,1,0.992,968.0,25805.0
2,475.5,29.71875,12.303,3.076,1,0.986,973.0,25859.0
```

*Multi-Class PanNuke (mixed cell types):*
```csv
nuclei_id,area_pixels,area_um2,radius_pixels,radius_um,cell_type,type_prob,centroid_x,centroid_y
0,215.5,13.46875,8.282,2.071,3,0.955,966.0,25823.0
123,104.0,6.5,5.754,1.438,2,0.992,1739.0,27353.0
245,574.7,35.92,13.007,3.252,1,0.876,1234.0,25374.0
```

### 2. Summary Statistics: `nuclei_areas_summary.json`

Comprehensive statistical summary including:

#### Overall Population Statistics
```json
{
  "total_nuclei": 41047,
  "total_area_um2": 685904.59,
  "mean_area_um2": 16.71,
  "median_area_um2": 14.84,
  "std_area_um2": 9.54,
  "q25_area_um2": 10.06,
  "q75_area_um2": 21.06,
  "q95_area_um2": 35.12
}
```

#### Per-Cell-Type Statistics
```json
"cell_type_stats": {
  "Neoplastic_type_1": {
    "count": 10,
    "mean_area_um2": 35.92,
    "median_area_um2": 33.34,
    "std_area_um2": 19.44,
    "min_area_um2": 8.78,
    "max_area_um2": 69.19,
    "percentage_of_total": 0.024
  },
  "Inflammatory_type_2": {
    "count": 1416,
    "mean_area_um2": 10.00,
    "percentage_of_total": 3.45
  },
  "Connective_type_3": {
    "count": 39621,
    "mean_area_um2": 16.95,
    "percentage_of_total": 96.53
  }
}
```

#### Metadata and Configuration
```json
{
  "pixel_size_um": 0.25,
  "magnification": 40.0,
  "cell_type_meanings": {
    "1": "Neoplastic",
    "2": "Inflammatory", 
    "3": "Connective",
    "4": "Dead",
    "5": "Epithelial"
  },
  "image_metadata": {
    "base_magnification": 40,
    "patch_size": 1024,
    "patch_overlap": 64,
    "base_mpp": 0.25
  }
}
```

## Usage

### Basic Usage
```bash
conda activate cellvit
python calculate_nuclei_areas_cellvit.py --input /path/to/cells.json
```

### Example Workflows

#### Binary Classification Analysis
```bash
python calculate_nuclei_areas_cellvit.py --input /Data/Yujing/CellViT_adapt/output/HIPT_binary/x40_svs/cells.json
```

**Expected Output:**
- **41,047 nuclei** detected (all type 1 - nuclei)
- Mean area: **16.71 μm²**
- Single cell type statistics

#### Multi-Class PanNuke Analysis  
```bash
python calculate_nuclei_areas_cellvit.py --input /Data/Yujing/CellViT_adapt/output/HIPT_pannuke/x40_svs/cells.json
```

**Expected Output:**
- **41,047 total nuclei** across multiple types:
  - **Neoplastic**: 10 cells (0.02%), mean area 35.92 μm²
  - **Inflammatory**: 1,416 cells (3.45%), mean area 10.00 μm²  
  - **Connective**: 39,621 cells (96.53%), mean area 16.95 μm²
  - **Dead**: 0 cells (not detected)
  - **Epithelial**: 0 cells (not detected)

## Key Features

### Dynamic Type Loading
- Automatically loads cell type definitions from `cell_detection.json`
- Supports any number of cell types (binary, PanNuke 6-class, custom classifications)
- Graceful fallback to embedded type mappings

### Accurate Geometric Measurements
- Uses exact polygon area calculations (not bounding box approximations)
- Handles complex cell shapes and concave boundaries
- Validates and repairs invalid polygons

### Comprehensive Statistics
- Per-cell detailed measurements
- Population-level descriptive statistics  
- Cell-type-specific analysis
- Percentile distributions (25th, 75th, 95th)

### Flexible Output Formats
- Machine-readable CSV for further analysis
- Human-readable JSON summaries
- Compatible with downstream statistical analysis tools

## Technical Notes

### Coordinate Systems
- **CellViT contours**: [y, x] format
- **Shapely polygons**: [x, y] format  
- **Automatic conversion** handled by the script

### Area Calculation Method
- **Geometric approach**: Uses Shapely polygon area calculation
- **Not bounding box**: Calculates actual cell shape area
- **Pixel to micron conversion**: `area_um2 = area_pixels × (pixel_size_um)²`

### Cell Type Mapping Priority
1. **Primary**: `type_map` from `cell_detection.json` 
2. **Fallback**: `type_map` from `cells.json` metadata
3. **Default**: Numeric type IDs (Type_1, Type_2, etc.)

## Dependencies

- **Python 3.7+**
- **shapely**: Geometric calculations
- **pandas**: Data manipulation  
- **numpy**: Numerical computations
- **json**: Data parsing

## Installation

```bash
conda activate cellvit
pip install shapely pandas numpy
```

## File Structure

```
CellViT_adapt/
├── src/
│   └── calculate_nuclei_areas_cellvit.py    # Main analysis script
├── output/
│   ├── HIPT_binary/                         # Binary classification results
│   │   └── x40_svs/
│   │       ├── cells.json                   # Cell detection data  
│   │       ├── cell_detection.json          # Type mapping
│   │       ├── nuclei_areas_detailed.csv    # Per-cell results
│   │       └── nuclei_areas_summary.json    # Statistical summary
│   └── HIPT_pannuke/                        # Multi-class classification results
│       └── x40_svs/
│           ├── cells.json
│           ├── cell_detection.json
│           ├── nuclei_areas_detailed.csv
│           └── nuclei_areas_summary.json
└── README.md                                # This file
```

## Citation

If you use this analysis pipeline, please cite the original CellViT paper and acknowledge this analysis extension.
