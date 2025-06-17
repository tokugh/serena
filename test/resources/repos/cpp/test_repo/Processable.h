#pragma once
#include <string>

class Processable {
public:
    virtual ~Processable() = default;
    virtual void execute() = 0;
    virtual std::string getType() const = 0;
};