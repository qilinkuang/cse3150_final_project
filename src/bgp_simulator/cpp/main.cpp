#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "include/simulator.h"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "BGP Simulator C++ core module";

    py::class_<Simulator>(m, "Simulator")
        .def(py::init<const std::string&>(),
             py::arg("as_relationships_file"),
             "Initialize simulator with AS relationships file")
        
        .def("add_announcement", &Simulator::add_announcement,
             py::arg("seed_asn"),
             py::arg("prefix"),
             py::arg("rov_invalid") = false,
             "Add an announcement to the simulation")
        
        .def("add_rov_asn", &Simulator::add_rov_asn,
             py::arg("asn"),
             "Mark an ASN as deploying ROV filtering")
        
        .def("propagate", &Simulator::propagate,
             "Run BGP propagation simulation")
        
        .def("get_ribs", &Simulator::get_ribs,
             "Get all local RIBs as list of (asn, prefix, as_path) tuples");
}