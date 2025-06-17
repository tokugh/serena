#include "ChildClass.h"
#include <iostream>

ChildClass::ChildClass(const std::string& name, int value) 
    : BaseClass(name), value(value) {}

void ChildClass::process() {
    std::cout << "Processing " << name << " with value " << value << std::endl;
}

int ChildClass::getValue() const {
    return value;
}