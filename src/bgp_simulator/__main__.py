"""Command-line interface for BGP simulator."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import run_simulation


def main() -> None:
    """Main entry point for BGP simulator CLI."""
    parser = argparse.ArgumentParser(
        description="BGP Routing Simulator with ROV support"
    )
    
    parser.add_argument(
        "--as-rel",
        type=str,
        required=True,
        help="Path to CAIDA AS relationships file"
    )
    
    parser.add_argument(
        "--announcements",
        type=str,
        required=True,
        help="Path to announcements CSV (columns: seed_asn,prefix,rov_invalid)"
    )
    
    parser.add_argument(
        "--rov-asns",
        type=str,
        default=None,
        help="Path to ROV ASNs file (one ASN per line)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output.csv",
        help="Output CSV path (default: output.csv)"
    )
    
    args = parser.parse_args()
    
    # Validate input files
    if not Path(args.as_rel).exists():
        print(f"Error: AS relationships file not found: {args.as_rel}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.announcements).exists():
        print(f"Error: Announcements file not found: {args.announcements}", file=sys.stderr)
        sys.exit(1)
    
    if args.rov_asns and not Path(args.rov_asns).exists():
        print(f"Error: ROV ASNs file not found: {args.rov_asns}", file=sys.stderr)
        sys.exit(1)
    
    # Run simulation
    try:
        run_simulation(
            as_relationships_file=args.as_rel,
            announcements_file=args.announcements,
            rov_asns_file=args.rov_asns,
            output_file=args.output
        )
        print(f"✓ Simulation complete! Results written to {args.output}")
    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
