cmake_minimum_required(VERSION 3.10)
project(test_repo)

set(CMAKE_CXX_STANDARD 17)

add_executable(test_repo
    BaseClass.cpp
    ChildClass.cpp
    ConcreteProcessor.cpp
    MultipleInterfaces.cpp
)