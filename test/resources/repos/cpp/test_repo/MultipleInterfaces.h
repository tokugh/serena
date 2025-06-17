#pragma once
#include "Processable.h"
#include <string>

class Readable {
public:
    virtual ~Readable() = default;
    virtual std::string read() const = 0;
};

class Writable {
public:
    virtual ~Writable() = default;
    virtual void write(const std::string& data) = 0;
};

class MultipleInterfaces : public Readable, public Writable, public Processable {
private:
    std::string data;
    
public:
    MultipleInterfaces(const std::string& data);
    std::string read() const override;
    void write(const std::string& data) override;
    void execute() override;
    std::string getType() const override;
};