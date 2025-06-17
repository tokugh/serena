#pragma once
#include <string>

class BaseClass {
protected:
    std::string name;
    
public:
    BaseClass(const std::string& name);
    virtual ~BaseClass() = default;
    virtual void process() = 0;
    std::string getName() const;
};