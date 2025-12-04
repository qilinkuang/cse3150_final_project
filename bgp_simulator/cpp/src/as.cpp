#include "../include/as.h"
#include "../include/bgp.h"

AS::AS(int asn_) : asn(asn_), policy(std::make_unique<BGP>()) {}

void AS::set_policy(std::unique_ptr<Policy> policy_) {
    policy = std::move(policy_);
}

void AS::receive_announcement(const Announcement& ann) {
    received_queue[ann.prefix].push_back(ann);
}

void AS::process_received() {
    bool changed = false;
    for (auto& [prefix, announcements] : received_queue) {
        size_t before = local_rib.size();
        // IMPORTANT: Pass this->asn as the receiving ASN parameter
        policy->process_announcements(announcements, local_rib, this->asn);
        changed |= (local_rib.size() != before) || false;
    }
    received_queue.clear();

    if (changed) {
        // enqueue outbound propagation (future optimization)
    }
}

std::vector<int> AS::get_customers() const {
    return std::vector<int>(customers.begin(), customers.end());
}

std::vector<int> AS::get_peers() const {
    return std::vector<int>(peers.begin(), peers.end());
}

std::vector<int> AS::get_providers() const {
    return std::vector<int>(providers.begin(), providers.end());
}