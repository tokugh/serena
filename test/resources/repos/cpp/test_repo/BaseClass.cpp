#include "BaseClass.h"

BaseClass::BaseClass(const std::string& name) : name(name) {}

std::string BaseClass::getName() const {
    return name;
}