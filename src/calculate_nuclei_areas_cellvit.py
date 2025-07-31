#!/usr/bin/env python3
"""
Calculate nuclei areas from CellViT JSON output with individual cell contours
"""

import json
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from pathlib import Path
import argparse

def load_cell_type_meanings(cells_json_path):
    """
    Load cell type meanings from the type_map in cell_detection.json
    located in the same directory as cells.json
    """
    cells_path = Path(cells_json_path)
    cell_detection_path = cells_path.parent / "cell_detection.json"
    
    if not cell_detection_path.exists():
        print(f"Warning: cell_detection.json not found at {cell_detection_path}")
        return {}
    
    try:
        with open(cell_detection_path, 'r') as f:
            cell_detection_data = json.load(f)
        
        # Extract type_map
        type_map = cell_detection_data.get('type_map', {})
        
        # Convert string keys to integers for consistency
        cell_type_meanings = {}
        for key, value in type_map.items():
            try:
                cell_type_meanings[int(key)] = value
            except (ValueError, TypeError):
                cell_type_meanings[key] = value
        
        print(f"Loaded cell type meanings: {cell_type_meanings}")
        return cell_type_meanings
    
    except Exception as e:
        print(f"Error loading cell_detection.json: {e}")
        return {}

def load_cellvit_json(file_path):
    """Load CellViT JSON output with individual cell data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    cells = data.get('cells', [])
    metadata = data.get('wsi_metadata', {})
    
    print(f"Found {len(cells)} cells in CellViT output")
    print(f"Image metadata: {metadata.get('base_mpp', 'N/A')} mpp, {metadata.get('magnification', 'N/A')}x magnification")
    
    return cells, metadata

def create_polygon_from_contour(contour_points):
    """Create a Shapely polygon from CellViT contour points."""
    if len(contour_points) < 3:
        return None
    
    # CellViT contour points are in [y, x] format, convert to [x, y] for Shapely
    polygon_coords = [(point[1], point[0]) for point in contour_points]
    
    try:
        polygon = Polygon(polygon_coords)
        if polygon.is_valid:
            return polygon
        else:
            # Try to fix invalid polygons
            polygon = polygon.buffer(0)
            return polygon if polygon.is_valid else None
    except Exception:
        return None

def calculate_areas_from_cells(cells, pixel_size_um=0.25):
    """Calculate areas from CellViT cell data."""
    areas_pixels = []
    areas_um2 = []
    valid_cells = 0
    
    for cell in cells:
        contour = cell.get('contour', [])
        if not contour:
            continue
            
        polygon = create_polygon_from_contour(contour)
        if polygon is not None:
            area_pixels = polygon.area
            area_um2 = area_pixels * (pixel_size_um ** 2)
            
            areas_pixels.append(area_pixels)
            areas_um2.append(area_um2)
            valid_cells += 1
    
    print(f"Successfully processed {valid_cells} cells out of {len(cells)} total cells")
    return areas_pixels, areas_um2

def main():
    parser = argparse.ArgumentParser(description='Calculate nuclei areas from CellViT JSON output')
    parser.add_argument('--input', '-i', type=str, 
                       default="/Data/Yujing/CellViT_adapt/output/HIPT_binary/x40_svs/cells.json",
                       help='Path to the CellViT cells.json file')
    
    args = parser.parse_args()
    json_path = args.input
    
    if not Path(json_path).exists():
        print(f"Error: JSON file not found: {json_path}")
        return
    
    print(f"Processing CellViT JSON file: {json_path}")
    
    try:
        # Load cell type meanings from cell_detection.json
        cell_type_meanings = load_cell_type_meanings(json_path)
        
        # Load CellViT data
        cells, metadata = load_cellvit_json(json_path)
        
        if len(cells) == 0:
            print("No cells found in the JSON file")
            return
        
        # Get pixel size from metadata or use default
        pixel_size_um = metadata.get('base_mpp', 0.25)  # microns per pixel
        print(f"Using pixel size: {pixel_size_um} μm/pixel")
        
        # Calculate areas
        areas_pixels, areas_um2 = calculate_areas_from_cells(cells, pixel_size_um)
        
        if len(areas_um2) == 0:
            print("No valid areas calculated")
            return
        
        # Convert to numpy arrays for statistics
        areas_pixels_array = np.array(areas_pixels)
        areas_um2_array = np.array(areas_um2)
        
        # Calculate equivalent circle radii
        # For a circle: area = π * r², so r = sqrt(area / π)
        radius_pixels_array = np.sqrt(areas_pixels_array / np.pi)
        radius_um_array = np.sqrt(areas_um2_array / np.pi)
        
        # Calculate statistics
        print(f"\nOverall Nuclei Area Statistics:")
        print(f"Number of nuclei: {len(areas_um2)}")
        print(f"Total area: {areas_um2_array.sum():.2f} μm²")
        print(f"Mean area: {areas_um2_array.mean():.2f} μm²")
        print(f"Median area: {np.median(areas_um2_array):.2f} μm²")
        print(f"Standard deviation: {areas_um2_array.std():.2f} μm²")
        print(f"Min area: {areas_um2_array.min():.2f} μm²")
        print(f"Max area: {areas_um2_array.max():.2f} μm²")
        
        # Percentiles
        print(f"25th percentile: {np.percentile(areas_um2_array, 25):.2f} μm²")
        print(f"75th percentile: {np.percentile(areas_um2_array, 75):.2f} μm²")
        print(f"95th percentile: {np.percentile(areas_um2_array, 95):.2f} μm²")
        
        # Equivalent radius statistics
        print(f"\nEquivalent Circle Radius Statistics:")
        print(f"Mean radius: {radius_um_array.mean():.2f} μm ({radius_pixels_array.mean():.2f} pixels)")
        print(f"Median radius: {np.median(radius_um_array):.2f} μm ({np.median(radius_pixels_array):.2f} pixels)")
        print(f"Min radius: {radius_um_array.min():.2f} μm ({radius_pixels_array.min():.2f} pixels)")
        print(f"Max radius: {radius_um_array.max():.2f} μm ({radius_pixels_array.max():.2f} pixels)")
        
        # Analyze by cell type
        cell_types = [cell.get('type', 1) for cell in cells[:len(areas_um2)]]
        unique_types = sorted(set(cell_types))
        # Use dynamically loaded cell type meanings or fall back to metadata type_map
        type_map = cell_type_meanings if cell_type_meanings else metadata.get('type_map', {})
        
        if len(unique_types) > 1:
            print(f"\nCell Type Breakdown:")
            print(f"Found {len(unique_types)} different cell types: {unique_types}")
            
            for cell_type in unique_types:
                type_name = type_map.get(cell_type, type_map.get(str(cell_type), f"Type_{cell_type}"))
                type_indices = [i for i, t in enumerate(cell_types) if t == cell_type]
                type_areas_um2 = areas_um2_array[type_indices]
                type_radii_um = radius_um_array[type_indices]
                
                print(f"\n  {type_name} (Type {cell_type}):")
                print(f"    Count: {len(type_indices)}")
                print(f"    Mean area: {type_areas_um2.mean():.2f} μm²")
                print(f"    Mean radius: {type_radii_um.mean():.2f} μm")
                print(f"    Area range: {type_areas_um2.min():.2f} - {type_areas_um2.max():.2f} μm²")
        
        # Create a DataFrame for analysis
        df = pd.DataFrame({
            'nuclei_id': range(len(areas_um2)),
            'area_pixels': areas_pixels,
            'area_um2': areas_um2,
            'radius_pixels': radius_pixels_array.tolist(),
            'radius_um': radius_um_array.tolist(),
            'cell_type': [cell.get('type', 1) for cell in cells[:len(areas_um2)]],
            'type_prob': [cell.get('type_prob', 0.0) for cell in cells[:len(areas_um2)]],
            'centroid_x': [cell.get('centroid', [0, 0])[1] for cell in cells[:len(areas_um2)]],
            'centroid_y': [cell.get('centroid', [0, 0])[0] for cell in cells[:len(areas_um2)]]
        })
        
        # Save results to CSV in the same directory as the input JSON file
        json_parent_dir = Path(json_path).parent
        output_path = json_parent_dir / "nuclei_areas_detailed.csv"
        df.to_csv(output_path, index=False)
        print(f"\nDetailed results saved to: {output_path}")
        
        # Save summary statistics
        summary_stats = {
            'total_nuclei': len(areas_um2),
            'total_area_um2': float(areas_um2_array.sum()),
            'mean_area_um2': float(areas_um2_array.mean()),
            'median_area_um2': float(np.median(areas_um2_array)),
            'std_area_um2': float(areas_um2_array.std()),
            'min_area_um2': float(areas_um2_array.min()),
            'max_area_um2': float(areas_um2_array.max()),
            'q25_area_um2': float(np.percentile(areas_um2_array, 25)),
            'q75_area_um2': float(np.percentile(areas_um2_array, 75)),
            'q95_area_um2': float(np.percentile(areas_um2_array, 95)),
            # Include pixel area statistics as well
            'total_area_pixels': float(areas_pixels_array.sum()),
            'mean_area_pixels': float(areas_pixels_array.mean()),
            'median_area_pixels': float(np.median(areas_pixels_array)),
            'std_area_pixels': float(areas_pixels_array.std()),
            'min_area_pixels': float(areas_pixels_array.min()),
            'max_area_pixels': float(areas_pixels_array.max()),
            'q25_area_pixels': float(np.percentile(areas_pixels_array, 25)),
            'q75_area_pixels': float(np.percentile(areas_pixels_array, 75)),
            'q95_area_pixels': float(np.percentile(areas_pixels_array, 95)),
            # Equivalent radius statistics in microns
            'mean_radius_um': float(radius_um_array.mean()),
            'median_radius_um': float(np.median(radius_um_array)),
            'std_radius_um': float(radius_um_array.std()),
            'min_radius_um': float(radius_um_array.min()),
            'max_radius_um': float(radius_um_array.max()),
            'q25_radius_um': float(np.percentile(radius_um_array, 25)),
            'q75_radius_um': float(np.percentile(radius_um_array, 75)),
            'q95_radius_um': float(np.percentile(radius_um_array, 95)),
            # Equivalent radius statistics in pixels
            'mean_radius_pixels': float(radius_pixels_array.mean()),
            'median_radius_pixels': float(np.median(radius_pixels_array)),
            'std_radius_pixels': float(radius_pixels_array.std()),
            'min_radius_pixels': float(radius_pixels_array.min()),
            'max_radius_pixels': float(radius_pixels_array.max()),
            'q25_radius_pixels': float(np.percentile(radius_pixels_array, 25)),
            'q75_radius_pixels': float(np.percentile(radius_pixels_array, 75)),
            'q95_radius_pixels': float(np.percentile(radius_pixels_array, 95)),
            # Cell type statistics
            'cell_type_stats': {},
            # Metadata and cell type information
            'pixel_size_um': pixel_size_um,
            'magnification': metadata.get('magnification', 'N/A'),
            'cell_type_meanings': cell_type_meanings if cell_type_meanings else {
                'background': 0,
                'nuclei': 1
            },
            'type_map': type_map if type_map else metadata.get('type_map', {'0': 'background', '1': 'nuclei'}),
            'image_metadata': {
                'base_magnification': metadata.get('base_magnification', 'N/A'),
                'patch_size': metadata.get('patch_size', 'N/A'),
                'patch_overlap': metadata.get('patch_overlap', 'N/A'),
                'base_mpp': metadata.get('base_mpp', 'N/A'),
                'target_patch_mpp': metadata.get('target_patch_mpp', 'N/A')
            }
        }
        
        # Add detailed cell type statistics
        cell_types = [cell.get('type', 1) for cell in cells[:len(areas_um2)]]
        unique_types = sorted(set(cell_types))
        
        for cell_type in unique_types:
            type_name = type_map.get(cell_type, type_map.get(str(cell_type), f"Type_{cell_type}"))
            type_indices = [i for i, t in enumerate(cell_types) if t == cell_type]
            type_areas_um2 = areas_um2_array[type_indices]
            type_areas_pixels = areas_pixels_array[type_indices]
            type_radii_um = radius_um_array[type_indices]
            type_radii_pixels = radius_pixels_array[type_indices]
            
            summary_stats['cell_type_stats'][f"{type_name}_type_{cell_type}"] = {
                'count': len(type_indices),
                'mean_area_um2': float(type_areas_um2.mean()),
                'median_area_um2': float(np.median(type_areas_um2)),
                'std_area_um2': float(type_areas_um2.std()),
                'min_area_um2': float(type_areas_um2.min()),
                'max_area_um2': float(type_areas_um2.max()),
                'mean_area_pixels': float(type_areas_pixels.mean()),
                'mean_radius_um': float(type_radii_um.mean()),
                'mean_radius_pixels': float(type_radii_pixels.mean()),
                'percentage_of_total': float(len(type_indices) / len(areas_um2) * 100)
            }
        
        summary_path = json_parent_dir / "nuclei_areas_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_stats, f, indent=2)
        print(f"Summary statistics saved to: {summary_path}")
        
    except Exception as e:
        print(f"Error processing CellViT JSON file: {e}")

if __name__ == "__main__":
    main()
