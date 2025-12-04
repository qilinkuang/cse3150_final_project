#pragma once
#include <unordered_map>
#include <vector>
#include <string>
#include <memory>
#include "as.h"

class Simulator {
private:
    std::unordered_map<int, std::unique_ptr<AS>> as_graph;
    std::vector<std::vector<int>> propagation_ranks;
    std::set<int> rov_asns;
    
    void load_as_relationships(const std::string& filepath);
    void build_propagation_ranks();
    void check_for_cycles();
    void propagate_up();
    void propagate_across();
    void propagate_down();
    
    
    size_t count_total_ribs() const;  // Helper to count total RIB entries
    
    
public:
    explicit Simulator(const std::string& as_relationships_file);
    
    void add_announcement(int seed_asn, const std::string& prefix, bool rov_invalid);
    void add_rov_asn(int asn);
    void propagate();
    
    std::vector<std::tuple<int, std::string, std::string>> get_ribs() const;
};