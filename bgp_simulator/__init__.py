from typing import Optional
try:
    from ._core import Simulator as _CppSimulator
except ImportError:
    _CppSimulator = None

__version__ = "0.1.0"
__all__ = ["Simulator", "run_simulation"]


class Simulator:
    """Python wrapper for C++ BGP Simulator."""
    
    def __init__(self, as_relationships_file: str):
        """Initialize simulator with AS relationships.
        
        Args:
            as_relationships_file: Path to CAIDA AS relationships file
        """
        if _CppSimulator is None:
            raise ImportError("C++ extension not available. Please rebuild the package.")
        self._sim = _CppSimulator(as_relationships_file)
    
    def add_announcement(self, seed_asn: int, prefix: str, rov_invalid: bool = False) -> None:
        """Add an announcement to the simulation.
        
        Args:
            seed_asn: ASN originating the announcement
            prefix: IP prefix (e.g., "1.2.0.0/16")
            rov_invalid: Whether this announcement is ROV invalid
        """
        self._sim.add_announcement(seed_asn, prefix, rov_invalid)
    
    def add_rov_asn(self, asn: int) -> None:
        """Mark an ASN as deploying ROV filtering.
        
        Args:
            asn: ASN to enable ROV on
        """
        self._sim.add_rov_asn(asn)
    
    def propagate(self) -> None:
        """Run BGP propagation simulation."""
        self._sim.propagate()
    
    def get_ribs(self) -> list[tuple[int, str, str]]:
        """Get all local RIBs after propagation.
        
        Returns:
            List of (asn, prefix, as_path) tuples
        """
        return self._sim.get_ribs()


def run_simulation(
    as_relationships_file: str,
    announcements_file: str,
    rov_asns_file: Optional[str] = None,
    output_file: str = "output.csv"
) -> None:
    """Run complete BGP simulation from input files.
    
    Args:
        as_relationships_file: Path to CAIDA AS relationships file
        announcements_file: CSV with columns: seed_asn,prefix,rov_invalid
        rov_asns_file: Optional file with ROV-enabled ASNs (one per line)
        output_file: Output CSV path for results
    """
    import csv
    from pathlib import Path
    
    # Initialize simulator
    sim = Simulator(as_relationships_file)
    
    # Load ROV ASNs if provided
    if rov_asns_file:
        with open(rov_asns_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    sim.add_rov_asn(int(line))
    
    # Load announcements
    with open(announcements_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            seed_asn = int(row['seed_asn'])
            prefix = row['prefix']
            rov_invalid = row['rov_invalid'].lower() == 'true'
            sim.add_announcement(seed_asn, prefix, rov_invalid)
    
    # Run propagation
    print("Running BGP propagation...")
    sim.propagate()
    
    # Write output
    ribs = sim.get_ribs()
    with open(output_file, 'w', newline='') as f:
        f.write("asn,prefix,as_path\n")
        for asn, prefix, as_path in ribs:
            f.write(f'{asn},{prefix},"{as_path}"\n')