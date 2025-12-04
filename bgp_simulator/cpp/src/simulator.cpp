// src/simulator.cpp - FIXED VERSION

#include "../include/simulator.h"
#include "../include/rov.h"
#include "../include/bgp.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <algorithm>
#include <functional>

Simulator::Simulator(const std::string& as_relationships_file) {
    load_as_relationships(as_relationships_file);
    check_for_cycles();
    build_propagation_ranks();
}

void Simulator::load_as_relationships(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open AS relationships file: " + filepath);
    }
    
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;
        
        std::istringstream iss(line);
        int asn1, asn2, relationship;
        char sep1, sep2;
        
        if (!(iss >> asn1 >> sep1 >> asn2 >> sep2 >> relationship)) {
            continue;
        }
        
        if (as_graph.find(asn1) == as_graph.end()) {
            as_graph[asn1] = std::make_unique<AS>(asn1);
        }
        if (as_graph.find(asn2) == as_graph.end()) {
            as_graph[asn2] = std::make_unique<AS>(asn2);
        }
        
        if (relationship == -1) {
            // asn1 is provider of asn2 (asn2 is customer of asn1)
            as_graph[asn1]->customers.insert(asn2);
            as_graph[asn2]->providers.insert(asn1);
        } else if (relationship == 0) {
            as_graph[asn1]->peers.insert(asn2);
            as_graph[asn2]->peers.insert(asn1);
        }
    }
}

void Simulator::check_for_cycles() {
    std::unordered_map<int, int> color;
    
    std::function<bool(int)> has_cycle = [&](int asn) -> bool {
        color[asn] = 1;
        
        for (int provider : as_graph[asn]->providers) {
            if (color[provider] == 1) {
                return true;
            }
            if (color[provider] == 0 && has_cycle(provider)) {
                return true;
            }
        }
        
        color[asn] = 2;
        return false;
    };
    
    for (const auto& [asn, as] : as_graph) {
        if (color[asn] == 0) {
            if (has_cycle(asn)) {
                throw std::runtime_error("Cycle detected in AS relationships!");
            }
        }
    }
}

void Simulator::build_propagation_ranks() {
    std::unordered_map<int, int> rank_map;
    std::queue<int> to_process;
    
    // Start with ASes that have no customers (leaf nodes)
    for (const auto& [asn, as] : as_graph) {
        if (as->customers.empty()) {
            rank_map[asn] = 0;
            to_process.push(asn);
        }
    }
    
    // BFS to assign ranks - need to handle this more carefully
    // An AS's rank should be max(rank of all customers) + 1
    std::unordered_map<int, int> customer_count;
    for (const auto& [asn, as] : as_graph) {
        customer_count[asn] = as->customers.size();
    }
    
    while (!to_process.empty()) {
        int current_asn = to_process.front();
        to_process.pop();
        
        int current_rank = rank_map[current_asn];
        
        for (int provider : as_graph[current_asn]->providers) {
            // Update rank to be max of current and new potential rank
            if (rank_map.find(provider) == rank_map.end()) {
                rank_map[provider] = current_rank + 1;
            } else {
                rank_map[provider] = std::max(rank_map[provider], current_rank + 1);
            }
            
            // Decrement the customer count; when it hits 0, all customers processed
            customer_count[provider]--;
            if (customer_count[provider] == 0) {
                to_process.push(provider);
            }
        }
    }
    
    // Handle ASes with no customers that weren't reached (isolated or top-tier)
    for (const auto& [asn, as] : as_graph) {
        if (rank_map.find(asn) == rank_map.end()) {
            rank_map[asn] = 0;
        }
    }
    
    int max_rank = 0;
    for (const auto& [asn, rank] : rank_map) {
        max_rank = std::max(max_rank, rank);
        as_graph[asn]->propagation_rank = rank;
    }
    
    propagation_ranks.resize(max_rank + 1);
    for (const auto& [asn, rank] : rank_map) {
        propagation_ranks[rank].push_back(asn);
    }
}

void Simulator::add_announcement(int seed_asn, const std::string& prefix, bool rov_invalid) {
    if (as_graph.find(seed_asn) == as_graph.end()) {
        throw std::runtime_error("Seed ASN not found in graph: " + std::to_string(seed_asn));
    }
    
    Announcement ann(prefix, seed_asn, rov_invalid);
    as_graph[seed_asn]->local_rib.insert({prefix, ann});
}

void Simulator::add_rov_asn(int asn) {
    if (as_graph.find(asn) != as_graph.end()) {
        as_graph[asn]->set_policy(std::make_unique<ROV>());
        rov_asns.insert(asn);
    }
}

void Simulator::propagate_up() {
    // Process from rank 0 (leaf/stub ASes) upward to higher ranks
    for (size_t rank = 0; rank < propagation_ranks.size(); ++rank) {
        // First, process any received announcements at this rank
        for (int asn : propagation_ranks[rank]) {
            as_graph[asn]->process_received();
        }
        
        // Then, forward announcements to providers
        for (int asn : propagation_ranks[rank]) {
            AS* as = as_graph[asn].get();
            for (const auto& [prefix, ann] : as->local_rib) {
                // Create announcement to forward - DO NOT prepend here
                // The receiving AS will prepend its own ASN in process_announcements
                Announcement forwarded = ann;
                forwarded.next_hop_asn = asn;
                forwarded.received_from = Relationship::CUSTOMER;
                
                for (int provider : as->providers) {
                    as_graph[provider]->receive_announcement(forwarded);
                }
            }
        }
    }
}

void Simulator::propagate_across() {
    // Send to all peers - DO NOT prepend, receiver will prepend
    for (const auto& [asn, as] : as_graph) {
        for (const auto& [prefix, ann] : as->local_rib) {
            Announcement forwarded = ann;
            forwarded.next_hop_asn = asn;
            forwarded.received_from = Relationship::PEER;
            
            for (int peer : as->peers) {
                as_graph[peer]->receive_announcement(forwarded);
            }
        }
    }
    
    // Process all in sorted order for determinism
    std::vector<int> asns_to_process;
    for (const auto& [asn, as] : as_graph) {
        asns_to_process.push_back(asn);
    }
    std::sort(asns_to_process.begin(), asns_to_process.end());
    
    for (int asn : asns_to_process) {
        as_graph[asn]->process_received();
    }
}

void Simulator::propagate_down() {
    // Process from highest rank down to 0
    for (int rank = (int)propagation_ranks.size() - 1; rank >= 0; --rank) {
        // First, process any received announcements at this rank
        for (int asn : propagation_ranks[rank]) {
            as_graph[asn]->process_received();
        }
        
        // Then, forward announcements to customers - DO NOT prepend
        for (int asn : propagation_ranks[rank]) {
            AS* as = as_graph[asn].get();
            for (const auto& [prefix, ann] : as->local_rib) {
                Announcement forwarded = ann;
                forwarded.next_hop_asn = asn;
                forwarded.received_from = Relationship::PROVIDER;
                
                for (int customer : as->customers) {
                    as_graph[customer]->receive_announcement(forwarded);
                }
            }
        }
    }
}

void Simulator::propagate() {
    propagate_up();
    propagate_across();
    propagate_down();
}

std::vector<std::tuple<int, std::string, std::string>> Simulator::get_ribs() const {
    std::vector<std::tuple<int, std::string, std::string>> results;
    
    for (const auto& [asn, as] : as_graph) {
        for (const auto& [prefix, ann] : as->local_rib) {
            results.emplace_back(asn, prefix, ann.as_path_string());
        }
    }
    
    return results;
}