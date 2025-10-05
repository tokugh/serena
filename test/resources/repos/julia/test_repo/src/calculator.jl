# Calculator module for basic arithmetic operations
module Calculator

export add, subtract, multiply, divide

"""
Add two numbers together.
"""
function add(a::Number, b::Number)
    return a + b
end

"""
Subtract b from a.
"""
function subtract(a::Number, b::Number)
    return a - b
end

"""
Multiply two numbers.
"""
function multiply(a::Number, b::Number)
    return a * b
end

"""
Divide a by b.
"""
function divide(a::Number, b::Number)
    if b == 0
        error("Division by zero")
    end
    return a / b
end

# Internal helper function (not exported)
function _internal_helper(x)
    return x * 2
end

end # module
