#!/usr/bin/env python3
"""
Test script for swap_data_and_space_group_lines function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_utils'))

from _processing_utils import swap_data_and_space_group_lines

# Test case 1: CIF with quoted space group (normal case)
test_cif_quoted = """data_SrTiO3
_cell_length_a    3.90
_cell_length_b    3.90
_cell_length_c    3.90
_symmetry_space_group_name_H-M          'P 1'
_symmetry_Int_Tables_number             1
loop_
_symmetry_equiv_pos_site_id
_symmetry_equiv_pos_as_xyz
  1  'x, y, z'
_chemical_formula_sum                'Sr Ti O3'
_cell_volume                    59.32
"""

# Test case 2: CIF with unquoted space group
test_cif_unquoted = """data_NaCl
_cell_length_a    5.64
_cell_length_b    5.64
_cell_length_c    5.64
_symmetry_space_group_name_H-M          Fm-3m
_symmetry_Int_Tables_number             225
loop_
_symmetry_equiv_pos_site_id
_symmetry_equiv_pos_as_xyz
  1  'x, y, z'
_chemical_formula_sum                'Na Cl'
_cell_volume                    179.78
"""

# Test case 3: CIF missing data_ line
test_cif_no_data = """_cell_length_a    3.90
_symmetry_space_group_name_H-M          'P 1'
loop_
_symmetry_equiv_pos_site_id
_symmetry_equiv_pos_as_xyz
  1  'x, y, z'
"""

# Test case 4: CIF missing space group line
test_cif_no_spacegroup = """data_SrTiO3
_cell_length_a    3.90
_cell_length_b    3.90
loop_
_symmetry_equiv_pos_site_id
_symmetry_equiv_pos_as_xyz
  1  'x, y, z'
"""

def test_quoted_space_group():
    """Test with quoted space group"""
    print("Test 1: CIF with quoted space group")
    try:
        result = swap_data_and_space_group_lines(test_cif_quoted)
        lines = result.strip().split('\n')
        
        # Check that first non-empty line is space group
        assert "_symmetry_space_group_name_H-M" in lines[0], f"First line should contain space group, got: {lines[0]}"
        # Check that second line is data_
        assert "data_SrTiO3" in lines[1], f"Second line should be data_, got: {lines[1]}"
        
        print("✓ PASSED: Space group line is now first, data_ line is second")
        print(f"  First two lines:\n    {lines[0]}\n    {lines[1]}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_unquoted_space_group():
    """Test with unquoted space group"""
    print("\nTest 2: CIF with unquoted space group")
    try:
        result = swap_data_and_space_group_lines(test_cif_unquoted)
        lines = result.strip().split('\n')
        
        assert "_symmetry_space_group_name_H-M" in lines[0], f"First line should contain space group, got: {lines[0]}"
        assert "data_NaCl" in lines[1], f"Second line should be data_, got: {lines[1]}"
        
        print("✓ PASSED: Unquoted space group handled correctly")
        print(f"  First two lines:\n    {lines[0]}\n    {lines[1]}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

def test_missing_data_line():
    """Test error when data_ line is missing"""
    print("\nTest 3: CIF missing data_ line (should raise error)")
    try:
        result = swap_data_and_space_group_lines(test_cif_no_data)
        print(f"✗ FAILED: Should have raised ValueError but returned:\n{result}")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError")
        print(f"  Error message: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {type(e).__name__}: {e}")
        return False

def test_missing_space_group_line():
    """Test error when space group line is missing"""
    print("\nTest 4: CIF missing space group line (should raise error)")
    try:
        result = swap_data_and_space_group_lines(test_cif_no_spacegroup)
        print(f"✗ FAILED: Should have raised ValueError but returned:\n{result}")
        return False
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError")
        print(f"  Error message: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {type(e).__name__}: {e}")
        return False

def test_idempotent_parsing():
    """Test that swapped CIF can still be parsed"""
    print("\nTest 5: Swapped CIF validity (can extract lines correctly)")
    try:
        result = swap_data_and_space_group_lines(test_cif_quoted)
        
        # Try to extract both lines again using regex
        import re
        data_match = re.search(r"^data_\S+", result, re.MULTILINE)
        spacegroup_match = re.search(r"^_symmetry_space_group_name_H-M", result, re.MULTILINE)
        
        assert data_match is not None, "Could not find data_ line after swap"
        assert spacegroup_match is not None, "Could not find space group line after swap"
        
        # Space group should come before data_
        sg_pos = spacegroup_match.start()
        data_pos = data_match.start()
        assert sg_pos < data_pos, f"Space group position ({sg_pos}) should be before data_ position ({data_pos})"
        
        print("✓ PASSED: Swapped CIF is valid and lines are in correct order")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Testing swap_data_and_space_group_lines() function")
    print("=" * 70)
    
    results = [
        test_quoted_space_group(),
        test_unquoted_space_group(),
        test_missing_data_line(),
        test_missing_space_group_line(),
        test_idempotent_parsing(),
    ]
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"✗ {total - passed} test(s) failed")
        sys.exit(1)
