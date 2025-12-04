#include "../include/announcement.h"
#include <sstream>
#include <algorithm>

Announcement::Announcement(const std::string& prefix_, int seed_asn, bool rov_invalid_)
    : prefix(prefix_), 
      next_hop_asn(seed_asn),
      received_from(Relationship::ORIGIN), 
      rov_invalid(rov_invalid_),
      local_pref(100) {  // Default local preference
    as_path.push_back(seed_asn);
}

bool Announcement::is_better_than(const Announcement& other) const {
    // 1. Local preference (higher is better)
    if (local_pref != other.local_pref) {
        return local_pref > other.local_pref;
    }
    
    // 2. Relationship (ORIGIN > CUSTOMER > PEER > PROVIDER)
    if (received_from != other.received_from) {
        return received_from < other.received_from;
    }
    
    // 3. AS path length (shorter is better)
    if (as_path.size() != other.as_path.size()) {
        return as_path.size() < other.as_path.size();
    }
    
    // 4. Next hop ASN (lower is better - second element in path)
    // If path has multiple elements, use second; otherwise use first
    int this_neighbor = (as_path.size() > 1) ? as_path[1] : as_path[0];
    int other_neighbor = (other.as_path.size() > 1) ? other.as_path[1] : other.as_path[0];
    
    if (this_neighbor != other_neighbor) {
        return this_neighbor < other_neighbor;
    }
    
    // 5. Final tie-break: keep existing (first-come first-served)
    return false;
}

std::string Announcement::as_path_string() const {
    std::ostringstream oss;
    oss << "(";
    for (size_t i = 0; i < as_path.size(); ++i) {
        if (i > 0) oss << ", ";
        oss << as_path[i];
    }
    // Add trailing comma for single-element paths (Python tuple format)
    if (as_path.size() == 1) {
        oss << ",";
    }
    oss << ")";
    return oss.str();
}