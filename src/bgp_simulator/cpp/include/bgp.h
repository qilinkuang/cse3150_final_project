#pragma once
#include "policy.h"

class BGP : public Policy {
public:
    void process_announcements(
        const std::vector<Announcement>& received,
        std::unordered_map<std::string, Announcement>& local_rib,
        int receiving_asn
    ) override;
};