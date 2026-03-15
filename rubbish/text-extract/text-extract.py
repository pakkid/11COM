# This function removes non-alphabetic characters
def clean(text):
    result = ""
    for letter in text:
        if letter.isalpha() or letter.isspace():
            result += letter
    return result

FILE_NAME = "Pride_and_Prejudice.txt"

with open(FILE_NAME) as file:
    words = clean(file.read().lower()).split()

# How many words are there?
print(len(words))

# What is the 66th word?

# What is the 13th word?

# How many words begin with the letter 'm'?

# Is the word "preternatural" in the list of words?

# How many words end in the letter 's'?

# How many words begin with a vowel?

# How many times does the word "bee" occur?

# How many words contain the word "her" in them?

# What is the last word with a double letter (e.g., "hello")?

# How many words have double letters?

# What is the most common word?
