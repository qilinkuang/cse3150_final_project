#include "../include/bgp.h"

void BGP::process_announcements(
    const std::vector<Announcement>& received,
    std::unordered_map<std::string, Announcement>& local_rib,
    int receiving_asn) {
    
    for (const auto& ann : received) {
        if (!should_accept(ann)) {
            continue;
        }
        
        // Check for loop - don't accept if we're already in the path
        bool has_loop = false;
        for (int asn_in_path : ann.as_path) {
            if (asn_in_path == receiving_asn) {
                has_loop = true;
                break;
            }
        }
        if (has_loop) {
            continue;
        }
        
        Announcement processed = ann;
        // Prepend our ASN to the path
        processed.as_path.insert(processed.as_path.begin(), receiving_asn);
        
        auto it = local_rib.find(processed.prefix);
        if (it == local_rib.end()) {
            local_rib.insert({processed.prefix, processed});
        } else if (processed.is_better_than(it->second)) {
            it->second = processed;
        }
    }
}
