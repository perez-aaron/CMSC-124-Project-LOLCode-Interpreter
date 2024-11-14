import re
from tkinter import filedialog as fd

token_types = [
    ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9_]*'),
    ('NUMBAR', r'-?\d+\.\d+'),     
    ('NUMBR', r'-?\d+'),              
    ('YARN', r'\”[^\”]*\”'),    
    ('TROOF', r'(WIN)|(FAIL)'),     
    ('TYPE', r'(NOOB)|(NUMBR)|(NUMBAR)|(YARN)|(TROOF)'),         
    ('ASSIGNMENT', r'='),
    ('SPACE',     r'[ \t]+'),           
    ('NEWLINE', r'\n'),   
]

regex = '|'.join('(?P<%s>%s)' % pair for pair in token_types)
get_token = re.compile(regex).match

def open_file():
    new_file = fd.askopenfilename(title="Open LOLCODE file")
    if not new_file:                                                # If no file was selected
        print("No file selected.")
        return []
    
    with open(new_file, 'r', encoding='UTF-8-sig') as file:
        file_arr = []
        for line in file:
            # line = line.strip()
            # line = line.split(',')
            file_arr.append(line)
    return file_arr

def tokenize(code):
    tokenized = get_token(code)
    token_arr = []
    while tokenized is not None:
        type = tokenized.lastgroup
        value = tokenized.group(type)
        token_arr.append((type, value))
        tokenized = get_token(code, tokenized.end())
    return token_arr

# Example usage
file_arr = open_file()
cnt = 1
for line in file_arr:
    he = tokenize(line)
    print("Input: ", line)
    print("Line ", cnt)
    print(he)
    cnt += 1