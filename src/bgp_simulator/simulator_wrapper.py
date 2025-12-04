"""High-level Python interface to BGP simulator."""
import csv
from pathlib import Path
from typing import Dict, Set
from tqdm import tqdm

from ._core import ASNode, BGPSimulator, Announcement, BGPPolicy, ROVPolicy


class BGPSimulatorWrapper:
    """Python wrapper for the C++ BGP simulator."""
    
    def __init__(self) -> None:
        self.as_nodes: Dict[int, ASNode] = {}
        self.simulator: BGPSimulator | None = None
    
    def build_as_graph(self, graph_file: Path) -> None:
        """Build AS graph from CAIDA file."""
        print(f"Building AS graph from {graph_file}")
        with open(graph_file, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.strip().split("|")
                if len(parts) < 4:
                    continue
                
                try:
                    asn1 = int(parts[0])
                    asn2 = int(parts[1])
                    rel_type = int(parts[2])
                except (ValueError, IndexError):
                    continue
                
                # Create nodes if they don't exist
                if asn1 not in self.as_nodes:
                    self.as_nodes[asn1] = ASNode(asn1)
                if asn2 not in self.as_nodes:
                    self.as_nodes[asn2] = ASNode(asn2)
                
                # Add relationship
                # rel_type: 0 = provider-to-customer, -1 = peer
                if rel_type == 0:
                    self.as_nodes[asn1].add_customer(self.as_nodes[asn2])
                    self.as_nodes[asn2].add_provider(self.as_nodes[asn1])
                else:
                    self.as_nodes[asn1].add_peer(self.as_nodes[asn2])
                    self.as_nodes[asn2].add_peer(self.as_nodes[asn1])
        
        print(f"  Created {len(self.as_nodes)} ASes")
    
    def deploy_rov(self, rov_asns: Set[int]) -> None:
        """Deploy ROV on specified ASes."""
        print(f"Deploying ROV on {len(rov_asns)} ASes")
        for asn in rov_asns:
            if asn not in self.as_nodes:
                self.as_nodes[asn] = ASNode(asn)
            self.as_nodes[asn].set_policy(ROVPolicy(asn))
    
    def seed_announcements(self, announcements_file: Path) -> None:
        """Seed announcements from CSV file."""
        print(f"Seeding announcements from {announcements_file}")
        
        # Read announcements
        announcements = []
        with open(announcements_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seed_asn = int(row["seed_asn"])
                prefix = row["prefix"]
                rov_invalid = row["rov_invalid"].lower() == "true"
                announcements.append((seed_asn, prefix, rov_invalid))
        
        # Initialize simulator
        self.simulator = BGPSimulator(self.as_nodes)
        
        # Seed announcements
        for seed_asn, prefix, rov_invalid in announcements:
            ann = Announcement(
                prefix=prefix,
                as_path=[seed_asn],
                next_hop_asn=seed_asn,
                received_from="origin",
                rov_invalid=rov_invalid
            )
            self.simulator.seed_announcement(seed_asn, ann)
        
        print(f"  Seeded {len(announcements)} announcements")
    
    def run(self) -> None:
        """Run the BGP propagation simulation."""
        if self.simulator is None:
            raise RuntimeError("No announcements seeded")
        
        print("Running BGP propagation...")
        self.simulator.run_propagation()
        print("  Propagation complete")
    
    def output_ribs(self, output_file: Path) -> None:
        """Output RIBs to CSV in exact benchmark format."""
        if self.simulator is None:
            raise RuntimeError("Simulation not run - call run() first")

        print(f"\nWriting output to {output_file}")

        ribs = self.simulator.get_ribs()

        with open(output_file, "w", newline="\n") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

            # Exact header
            writer.writerow(["asn", "prefix", "as_path"])

            # Sort ASNs + prefixes
            for asn in sorted(ribs.keys()):
                for prefix in sorted(ribs[asn].keys()):

                    as_path = ribs[asn][prefix]

                    # EXACT REQUIRED FORMAT: "(1, 2, 3, 4)"
                    path_str = "(" + ", ".join(str(a) for a in as_path) + ")"

                    # FORCE quotes around AS-path
                    writer.writerow([asn, prefix, path_str])
