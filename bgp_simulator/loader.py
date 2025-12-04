import argparse
from pathlib import Path
from .simulator_wrapper import BGPSimulatorWrapper
import pandas as pd

def main() -> None:
    """Run the BGP simulator."""
    parser = argparse.ArgumentParser(
        description="BGP Routing Simulator with ROV support"
    )
    parser.add_argument(
        "--graph",
        required=True,
        type=Path,
        help="CAIDA AS graph file",
    )
    parser.add_argument(
        "--announcements",
        required=True,
        type=Path,
        help="Announcements CSV file",
    )
    parser.add_argument(
        "--rov-asns",
        type=Path,
        help="ROV ASNs file (one ASN per line)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output RIBs CSV file",
    )
    
    args = parser.parse_args()
    
    # Create simulator
    sim = BGPSimulatorWrapper()
    
    # Build graph
    sim.build_as_graph(args.graph)
    
    # Deploy ROV if specified
    if args.rov_asns:
        with open(args.rov_asns, "r") as f:
            rov_asns = {int(line.strip()) for line in f if line.strip()}
        sim.deploy_rov(rov_asns)
    
    # Run simulation
    sim.seed_announcements(args.announcements)
    sim.run()
    sim.output_ribs(args.output)
    
    # Sort output by ASN (numeric) and prefix
    print("Sorting output...")
    df = pd.read_csv(args.output)
    df['asn'] = df['asn'].astype(int)  # Ensure numeric sort
    df_sorted = df.sort_values(['asn', 'prefix']).reset_index(drop=True)
    df_sorted.to_csv(args.output, index=False)
    
    print("\n✓ Simulation complete!")


if __name__ == "__main__":
    main()