#include "MultipleInterfaces.h"
#include <iostream>

MultipleInterfaces::MultipleInterfaces(const std::string& data) : data(data) {}

std::string MultipleInterfaces::read() const {
    return data;
}

void MultipleInterfaces::write(const std::string& data) {
    this->data = data;
}

void MultipleInterfaces::execute() {
    std::cout << "Executing with data: " << data << std::endl;
}

std::string MultipleInterfaces::getType() const {
    return "MultipleInterfaces";
}