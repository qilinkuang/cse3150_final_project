#pragma once
#include "bgp.h"

class ROV : public BGP {
public:
    bool should_accept(const Announcement& ann) const override;
};