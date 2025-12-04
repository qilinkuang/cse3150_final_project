#pragma once
#include <memory>
#include <unordered_map>
#include <vector>
#include <set>
#include "announcement.h"
#include "policy.h"

class AS {
public:
    int asn;
    std::unique_ptr<Policy> policy;
    std::unordered_map<std::string, Announcement> local_rib;
    std::unordered_map<std::string, std::vector<Announcement>> received_queue;
    
    std::set<int> customers;
    std::set<int> peers;
    std::set<int> providers;
    
    int propagation_rank = -1;

    explicit AS(int asn_);
    
    void set_policy(std::unique_ptr<Policy> policy_);
    void receive_announcement(const Announcement& ann);
    void process_received();
    
    std::vector<int> get_customers() const;
    std::vector<int> get_peers() const;
    std::vector<int> get_providers() const;
};
