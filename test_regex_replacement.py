import re

# Test case to demonstrate the issue with newlines in replacement strings
original_text = "print(f'Some text')"
regex_pattern = r"print\(f'Some text'\)"

# Test 1: Using a replacement string with \n
replacement_with_newline = r"print(f'\n    Some more detailed text')"
result1, count1 = re.subn(regex_pattern, replacement_with_newline, original_text, flags=re.DOTALL | re.MULTILINE)

print("Original text:", repr(original_text))
print("Replacement string:", repr(replacement_with_newline))
print("Result 1:", repr(result1))
print("Count 1:", count1)

# Test 2: Using a replacement string with literal newline
replacement_with_literal_newline = "print(f'\n    Some more detailed text')"
result2, count2 = re.subn(regex_pattern, replacement_with_literal_newline, original_text, flags=re.DOTALL | re.MULTILINE)

print("\nReplacement with literal newline:", repr(replacement_with_literal_newline))
print("Result 2:", repr(result2))
print("Count 2:", count2)

# Test 3: Using a replacement string with double backslash
replacement_with_double_backslash = r"print(f'\\n    Some more detailed text')"
result3, count3 = re.subn(regex_pattern, replacement_with_double_backslash, original_text, flags=re.DOTALL | re.MULTILINE)

print("\nReplacement with double backslash:", repr(replacement_with_double_backslash))
print("Result 3:", repr(result3))
print("Count 3:", count3)

# Test 4: Using re.escape on the replacement string
replacement_to_escape = r"print(f'\n    Some more detailed text')"
escaped_replacement = re.escape(replacement_to_escape).replace(r'\\n', r'\n')
result4, count4 = re.subn(regex_pattern, escaped_replacement, original_text, flags=re.DOTALL | re.MULTILINE)

print("\nEscaped replacement:", repr(escaped_replacement))
print("Result 4:", repr(result4))
print("Count 4:", count4)