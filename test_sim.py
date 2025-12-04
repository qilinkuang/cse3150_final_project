from bgp_simulator import run_simulation
run_simulation(
    as_relationships_file="bench/prefix/CAIDAASGraphCollector_2025.10.15.txt",
    announcements_file="bench/prefix/anns.csv",
    rov_asns_file="bench/prefix/rov_asns.csv",
    output_file="output_prefix.csv"
)
