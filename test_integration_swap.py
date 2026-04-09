#!/usr/bin/env python3
"""
Integration test for swap_space_group_order in cleaning pipeline
"""

import sys
import os
import tempfile
import pandas as pd

sys.path.insert(0, '/home/matthew/src/CrystaLLM-pi')

from _utils._preprocessing._cleaning import augment_cif_chunk
import multiprocessing as mp

# Sample CIF for testing
sample_cif = """data_SrTiO3
_cell_length_a    3.90
_cell_length_b    3.90
_cell_length_c    3.90
_cell_angle_alpha    90
_cell_angle_beta    90
_cell_angle_gamma    90
_symmetry_space_group_name_H-M          'P m m m'
_symmetry_Int_Tables_number             47
_cell_volume                    59.32
_cell_formula_units_Z                   1
_chemical_formula_sum                   'Sr Ti O3'
loop_
_symmetry_equiv_pos_site_id
_symmetry_equiv_pos_as_xyz
  1  'x, y, z'
loop_
_atom_site_label
_atom_site_occupancy
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
  Sr1  1.0  0.5  0.5  0.5
  Ti1  1.0  0.0  0.0  0.0
  O1   1.0  0.0  0.5  0.0
  O2   1.0  0.5  0.0  0.0
  O3   1.0  0.5  0.5  0.0
"""

def test_cleaning_pipeline_with_swap():
    """Test the full cleaning pipeline with space group swap enabled"""
    print("Integration Test: Cleaning pipeline with swap_space_group_order=True")
    print("-" * 70)
    
    try:
        # Create test data
        chunk = [(0, sample_cif)]
        progress_queue = mp.Manager().Queue()
        
        # Test WITHOUT swap
        print("\n1. Testing WITHOUT swap_space_group_order:")
        results_no_swap = augment_cif_chunk(
            chunk, 
            oxi=False, 
            progress_queue=progress_queue,
            make_ordered=False,
            swap_space_group_order=False
        )
        
        if results_no_swap:
            no_swap_cif = results_no_swap[0][1]
            no_swap_lines = no_swap_cif.strip().split('\n')
            first_line_no_swap = no_swap_lines[0]
            print(f"   ✓ Pipeline executed successfully")
            print(f"   First line: {first_line_no_swap[:60]}...")
            assert "data_" in first_line_no_swap, "First line should be data_ when swap is disabled"
            print(f"   ✓ Confirmed: data_ line is first (swap disabled)")
        else:
            print(f"   ✗ FAILED: No results returned")
            return False
        
        # Reset queue and test WITH swap
        progress_queue = mp.Manager().Queue()
        print("\n2. Testing WITH swap_space_group_order=True:")
        results_with_swap = augment_cif_chunk(
            chunk,
            oxi=False,
            progress_queue=progress_queue,
            make_ordered=False,
            swap_space_group_order=True
        )
        
        if results_with_swap:
            with_swap_cif = results_with_swap[0][1]
            with_swap_lines = with_swap_cif.strip().split('\n')
            first_line_with_swap = with_swap_lines[0]
            print(f"   ✓ Pipeline executed successfully")
            print(f"   First line: {first_line_with_swap[:60]}...")
            assert "_symmetry_space_group_name_H-M" in first_line_with_swap, "First line should be space group when swap is enabled"
            print(f"   ✓ Confirmed: _symmetry_space_group_name_H-M line is first (swap enabled)")
        else:
            print(f"   ✗ FAILED: No results returned")
            return False
        
        # Verify both contain all expected data
        print("\n3. Verifying both CIFs contain all structural data:")
        assert "_cell_volume" in no_swap_cif, "Missing _cell_volume in no-swap result"
        assert "_cell_volume" in with_swap_cif, "Missing _cell_volume in swap result"
        assert "Sr1" in no_swap_cif, "Missing Sr1 in no-swap result"
        assert "Sr1" in with_swap_cif, "Missing Sr1 in swap result"
        print(f"   ✓ Both CIFs contain all structural data")
        
        print("\n" + "=" * 70)
        print("✓ Integration test PASSED!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cleaning_pipeline_with_swap()
    sys.exit(0 if success else 1)
