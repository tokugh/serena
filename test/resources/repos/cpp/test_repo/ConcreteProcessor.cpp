#include "ConcreteProcessor.h"
#include <iostream>

ConcreteProcessor::ConcreteProcessor(const std::string& name, const std::string& type) 
    : BaseClass(name), type(type) {}

void ConcreteProcessor::process() {
    std::cout << "Processing " << name << std::endl;
}

void ConcreteProcessor::execute() {
    process();
}

std::string ConcreteProcessor::getType() const {
    return type;
}