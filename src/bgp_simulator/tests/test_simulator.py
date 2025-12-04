"""Tests for BGP simulator functionality."""

import tempfile
from pathlib import Path
import csv

import pytest

from bgp_simulator import Simulator, run_simulation


def create_test_as_relationships() -> str:
    """Create a temporary AS relationships file for testing."""
    content = """# Test AS relationships
1|2|-1|bgp
2|3|-1|bgp
1|4|0|bgp
5|6|-1|bgp
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        return f.name


def create_test_announcements() -> str:
    """Create a temporary announcements file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        writer = csv.writer(f)
        writer.writerow(['seed_asn', 'prefix', 'rov_invalid'])
        writer.writerow([3, '1.2.0.0/16', False])
        return f.name


def create_test_rov_asns() -> str:
    """Create a temporary ROV ASNs file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("1\n2\n")
        return f.name


def test_simulator_initialization() -> None:
    """Test that simulator initializes correctly."""
    as_rel_file = create_test_as_relationships()
    try:
        sim = Simulator(as_rel_file)
        assert sim is not None
    finally:
        Path(as_rel_file).unlink()


def test_basic_propagation() -> None:
    """Test basic BGP propagation."""
    as_rel_file = create_test_as_relationships()
    try:
        sim = Simulator(as_rel_file)
        sim.add_announcement(3, "1.2.0.0/16", False)
        sim.propagate()
        
        ribs = sim.get_ribs()
        assert len(ribs) > 0
        
        # Check that announcement reached other ASes
        asns_with_route = {rib[0] for rib in ribs}
        assert 3 in asns_with_route  # Origin should have it
        assert 2 in asns_with_route  # Provider should have it
        assert 1 in asns_with_route  # Provider of provider should have it
    finally:
        Path(as_rel_file).unlink()


def test_rov_filtering() -> None:
    """Test that ROV filtering drops invalid announcements."""
    as_rel_file = create_test_as_relationships()
    try:
        sim = Simulator(as_rel_file)
        
        # Add ROV to AS 2
        sim.add_rov_asn(2)
        
        # Add invalid announcement at AS 3
        sim.add_announcement(3, "1.2.0.0/16", True)
        sim.propagate()
        
        ribs = sim.get_ribs()
        
        # AS 3 should have it (origin)
        asns_with_route = {rib[0] for rib in ribs if rib[1] == "1.2.0.0/16"}
        assert 3 in asns_with_route
        
        # AS 2 (ROV enabled) should NOT have it
        assert 2 not in asns_with_route
        
        # AS 1 should not have it either (since AS 2 filtered it)
        assert 1 not in asns_with_route
    finally:
        Path(as_rel_file).unlink()


def test_run_simulation_end_to_end() -> None:
    """Test complete simulation from files."""
    as_rel_file = create_test_as_relationships()
    ann_file = create_test_announcements()
    rov_file = create_test_rov_asns()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as out_f:
        output_file = out_f.name
    
    try:
        run_simulation(
            as_relationships_file=as_rel_file,
            announcements_file=ann_file,
            rov_asns_file=rov_file,
            output_file=output_file
        )
        
        # Verify output file exists and has content
        assert Path(output_file).exists()
        
        with open(output_file) as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) > 1  # Header + at least one data row
            assert rows[0] == ['asn', 'prefix', 'as_path']
    finally:
        Path(as_rel_file).unlink()
        Path(ann_file).unlink()
        Path(rov_file).unlink()
        Path(output_file).unlink()