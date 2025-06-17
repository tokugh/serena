#pragma once
#include "BaseClass.h"
#include "Processable.h"

class ConcreteProcessor : public BaseClass, public Processable {
private:
    std::string type;
    
public:
    ConcreteProcessor(const std::string& name, const std::string& type);
    void process() override;
    void execute() override;
    std::string getType() const override;
};