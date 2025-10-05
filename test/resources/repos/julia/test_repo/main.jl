include("src/calculator.jl")
include("src/utils.jl")

# Main module demonstrating Julia language features
module Main

using ..Calculator
using ..Utils

# Struct definition for testing symbol resolution
struct Point
    x::Float64
    y::Float64
end

# Function with references to imported modules
function process_data(p::Point)
    # Reference to Calculator module
    result = Calculator.add(p.x, p.y)

    # Reference to Utils module
    formatted = Utils.format_number(result)

    return formatted
end

# Nested function for testing hierarchical symbols
function outer_function(x, y)
    function inner_function(a, b)
        return a + b
    end

    intermediate = inner_function(x, y)
    return Calculator.multiply(intermediate, 2)
end

# Type with methods for testing method resolution
mutable struct Counter
    value::Int64
end

function increment!(c::Counter)
    c.value += 1
end

function get_value(c::Counter)
    return c.value
end

# Main entry point with cross-file references
function run()
    p = Point(3.0, 4.0)
    result = process_data(p)
    println("Result: ", result)

    counter = Counter(0)
    increment!(counter)
    println("Counter: ", get_value(counter))

    # Cross-file reference
    outer_result = outer_function(5, 10)
    println("Outer result: ", outer_result)
end

end # module
