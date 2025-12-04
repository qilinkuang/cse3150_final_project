from pathlib import Path
from bgp_simulator import run_simulation

# Example usage
if __name__ == "__main__":
    # Paths to your data files
    bench_dir = Path.home() / "Desktop" / "bench" / "prefix"
    
    as_rel_file = bench_dir / "CAIDAASGraphCollector_2025.10.15.txt"
    announcements_file = bench_dir / "anns.csv"
    rov_asns_file = bench_dir / "rov_asns.csv"
    output_file = "output_prefix.csv"
    
    print("Starting BGP simulation...")
    print(f"  AS relationships: {as_rel_file}")
    print(f"  Announcements: {announcements_file}")
    print(f"  ROV ASNs: {rov_asns_file}")
    print(f"  Output: {output_file}")
    print()
    
    run_simulation(
        as_relationships_file=str(as_rel_file),
        announcements_file=str(announcements_file),
        rov_asns_file=str(rov_asns_file),
        output_file=output_file
    )
    
    print(f"\n✓ Complete! Check {output_file} for results")
