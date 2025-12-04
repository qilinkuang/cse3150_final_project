#pragma once
#include <string>
#include <vector>

enum class Relationship {
    ORIGIN,     
    CUSTOMER,
    PEER,
    PROVIDER
};

class Announcement {
public:
    std::string prefix;
    std::vector<int> as_path;
    int next_hop_asn;
    Relationship received_from;
    bool rov_invalid;
    int local_pref;

    Announcement(const std::string& prefix_, int seed_asn, bool rov_invalid_ = false);
    
    bool is_better_than(const Announcement& other) const;
    std::string as_path_string() const;
    
    int getLocalPref() const { return local_pref; }
    void setLocalPref(int pref) { local_pref = pref; }
};