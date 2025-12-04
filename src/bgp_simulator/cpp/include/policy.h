#pragma once
#include <unordered_map>
#include <vector>
#include <string>
#include "announcement.h"

class Policy {
public:
    virtual ~Policy() = default;
    
    // Process received announcements and update local RIB
    // receiving_asn: the ASN of this AS (needed to prepend to path)
    virtual void process_announcements(
        const std::vector<Announcement>& received,
        std::unordered_map<std::string, Announcement>& local_rib,
        int receiving_asn
    ) = 0;
    
    virtual bool should_accept(const Announcement& ann) const { return true; }
};