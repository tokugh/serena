#pragma once
#include "BaseClass.h"

class ChildClass : public BaseClass {
private:
    int value;
    
public:
    ChildClass(const std::string& name, int value);
    void process() override;
    int getValue() const;
};