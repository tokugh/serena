# Utility module with helper functions
module Utils

using Printf

export format_number, process_array

"""
Format a number as a string with 2 decimal places.
"""
function format_number(n::Number)
    return @sprintf("%.2f", n)
end

"""
Process an array and return the sum.
"""
function process_array(arr::Vector{<:Number})
    return sum(arr)
end

"""
Find the maximum value in an array.
"""
function find_max(arr::Vector{<:Number})
    if isempty(arr)
        return nothing
    end
    return maximum(arr)
end

# Nested type definition
struct DataProcessor
    name::String
    multiplier::Float64
end

function process(dp::DataProcessor, value::Number)
    return value * dp.multiplier
end

end # module
