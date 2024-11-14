import re
from tkinter import filedialog as fd

token_types = [
    ('SINGLE_LINE_COMMENT', r'BTW.*'),
    ('MULTI_LINE_COMMENT_START', r'OBTW'),
    ('MULTI_LINE_COMMENT_END', r'TLDR'),
    ('PROGRAM_START', r'HAI'),  
    ('PROGRAM_END', r'KTHNXBYE'),  
    ('VARIABLE_START', r'WAZZUP'),  
    ('VARIABLE_END', r'BUHBYE'), 
    ('DECLARATION', r'I HAS A'),
    ('DECLARATION_ASSIGNMENT', r'ITZ'),
    ('INPUT', r'GIMMEH'),
    ('PRINT', r'VISIBLE'),
    ('ASSIGNMENT', r'R'),
    ('CONCATENATION', r'SMOOSH'),
    ('ARITHMETIC', r'(SUM OF)|(DIFF OF)|(PRODUKT OF)|(QUOSHUNT OF)|(BIGGR OF)|(SMALLR OF)|(MOD OF)'),
    ('BOOLEAN', r'(BOTH OF)|(EITHER OF)|(WON OF)|(NOT)|(ALL)|(ANY)'),
    ('COMPARISON', r'(BOTH SAEM)|(DIFFRINT)'),
    ('TYPECAST', r'(MAEK)|(IS NOW A)'),
    ('CONDITIONAL', r'(O RLY\?|YA RLY|MEBBE|NO WAI|OIC)'),
    ('SWITCH', r'(WTF\?|OMG|OMGWTF)'),
    ('LOOP', r'(IM IN YR|UPPIN|NERFIN|YR|TIL|WILE|IM OUTTA YR)'),
    ('FUNCTION', r'(HOW IZ I|IF U SAY SO|GTFO|FOUND YR|I IZ)'),
    ('CONFIRMATION', r'MKAY'),
    ('STRING', r'\"[A-Za-z][A-Za-z0-9_]*\"'),                      
    ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9_]*'),
    ('NUMBAR', r'-?\d+\.\d+'),
    ('NUMBR', r'-?\d+'),
    ('YARN', r'\"[^\"]*\"'),
    ('TROOF', r'(WIN)|(FAIL)'),
    ('TYPE', r'(NOOB)|(NUMBR)|(NUMBAR)|(YARN)|(TROOF)'),
    ('SPACE', r'[ \t]+'),
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

        if type not in ['SPACE', 'NEWLINE']:                    # Ignore spaces and newlines
            token_arr.append((value.strip(), type))

        tokenized = get_token(code, tokenized.end())
    return token_arr

def main():
    file_arr = open_file()

    print(f"{'Lexeme':<40} {'Token Type':<40} {'Line':<40}")
    print("=" * 85)
    
    for line_number, line in enumerate(file_arr, start=1):
        tokens = tokenize(line)
        for value, type_ in tokens:
            print(f"{value:<40} {type_:<40} {line_number:<40}")

main()