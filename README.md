# BGP Simulator

A high-performance BGP routing simulator with C++ core and Python bindings.

## Features

- ROV (Route Origin Validation) support
- Python interface for ease of use
- Handles large-scale AS topologies

### Prerequisites

- Python 3.8+
- C++ compiler with C++17 support
- CMake 3.15+
- pybind11

### From source

```bash
# Clone the repository
git clone git@github.com:qilinkuang/cse3150_final_project.git
cd bgp_simulator

# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install in development mode
pip install -e ".[test]"
```

## Usage

### Command Line

```bash
bgp-simulate \
  --as-rel path/to/as_relationships.txt \
  --announcements path/to/announcements.csv \
  --rov-asns path/to/rov_asns.csv \
  --output results.csv
```

### Python API

```python
from bgp_simulator import run_simulation

run_simulation(
    as_relationships_file="caida_relationships.txt",
    announcements_file="announcements.csv",
    rov_asns_file="rov_asns.csv",
    output_file="output.csv"
)
```

## Input File Formats

### AS Relationships
CAIDA format: `asn1|asn2|relationship|type`
- relationship: -1 (provider-customer), 0 (peer-peer)

### Announcements CSV
Columns: `seed_asn,prefix,rov_invalid`

### ROV ASNs
One ASN per line

## Running Tests

```bash
pytest src/bgp_simulator/tests
```

## Development

```bash
# Format code
ruff format src/bgp_simulator

# Lint
ruff check src/bgp_simulator

# Type check
mypy src/bgp_simulator

# Run all checks
tox
```

## License

MIT License