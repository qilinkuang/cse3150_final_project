#include "../include/rov.h"

bool ROV::should_accept(const Announcement& ann) const {
    // ROV ASes drop announcements marked as invalid
    return !ann.rov_invalid;
}