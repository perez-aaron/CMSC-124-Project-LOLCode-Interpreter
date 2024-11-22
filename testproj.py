import os, os.path, shutil, random, copy, re, tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk, font
from decimal import Decimal
import re
from tkinter import filedialog as fd

token_types = [
    ('SINGLE_LINE_COMMENT', r'BTW'),
    ('MULTI_LINE_COMMENT_START', r'OBTW'),
    ('MULTI_LINE_COMMENT_END', r'TLDR'),
    ('PROGRAM_START', r'HAI'),  
    ('PROGRAM_END', r'KTHXBYE'),  
    ('VARIABLE_START', r'WAZZUP'),  
    ('VARIABLE_END', r'BUHBYE'), 
    ('DECLARATION', r'I HAS A'),
    ('DECLARATION_ASSIGNMENT', r'ITZ'),
    ('INPUT', r'GIMMEH'),
    ('PRINT', r'VISIBLE'),
    ('ASSIGNMENT', r'R'),
    ('CONNECTOR', r'AN|\+'),
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
    ('YARN', r'(\"[^\"]*\")'),    
    ('TYPE', r'(NOOB)|(NUMBR)|(NUMBAR)|(YARN)|(TROOF)'),        
    ('NUMBAR', r'-?\d+\.\d+'),
    ('NUMBR', r'-?\d+'),
    ('TROOF', r'(WIN)|(FAIL)'),      
    ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9_]*'),
    ('SPACE', r'[ \t]+'),
    ('NEWLINE', r'\n'),
    ('ERROR', r'.'),
]
token_comment = [
    ('MULTI_LINE_COMMENT_END', r'TLDR'),  
    ('NEWLINE', r'\n'), 
    ('COMMENT_BODY', r'(.*?)(?=\n|TLDR)'), 
]

regex = '|'.join('(?P<%s>%s)' % pair for pair in token_types)
get_token = re.compile(regex).match

regex2 = '|'.join('(?P<%s>%s)' % pair for pair in token_comment)
get_token2 = re.compile(regex2).match

class LOL:
    def __init__(self, root):
        self.root = root
        self.file = None
        self.root.geometry("1500x700")
        self.root.title("HELLO, HAI, KTHXBYE INTERPRETER")
        self.create_widgets()

    def create_widgets(self):
        bold_font = font.Font(family="Helvetica", size=12, weight="bold")

        #TITLE FRAME
        self.title_frame = tk.Frame(self.root, background="#181818")
        self.title_label = tk.Label(self.title_frame, text="HELLO, HAI, KTHXBYE INTERPRETER",font=bold_font,background='#181818',fg='white')
        self.title_label.pack(expand=True)

        #FILE FRAME
        self.file_frame = tk.Frame(self.root, background="#181818")
        self.file_button = tk.Button(self.file_frame, text = "FILE", background = '#1F1F1F', fg = 'white', font=bold_font, width=10, height=2, command=self.open_file)
        self.file_button.pack(side=tk.TOP, padx=10, pady=10)
        self.lexical_analyze_button = tk.Button(self.file_frame, text = "ANALYZE", background = '#1F1F1F', fg = 'white', font=bold_font, width=10, height=2, command=self.lexical)
        self.lexical_analyze_button.pack(side=tk.TOP,padx=10, pady=10)
        self.reset_button = tk.Button(self.file_frame, text = "RESET", background = '#1F1F1F', fg = 'white', font=bold_font, width=10, height=2, command=self.reset)
        self.reset_button.pack(side=tk.TOP,padx=10, pady=10)

        #CODEBASE FRAME
        self.code_frame = tk.Frame(self.root, background="#1F1F1F")
        self.code_label = tk.Label(self.code_frame, text="CODE",font=bold_font,fg='white',background='#1F1F1F')
        self.code_label.pack(side=tk.TOP)

        self.code_text = tk.Text(self.code_frame, wrap=tk.WORD, background='#292929', fg='white')
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code_scrollbar = tk.Scrollbar(self.code_frame, command=self.code_text.yview,background="grey")
        self.code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.config(yscrollcommand=self.code_scrollbar.set)

        #LEXEMES FRAME
        self.lex_frame = tk.Frame(self.root, background="#1F1F1F")
        self.lex_label = tk.Label(self.lex_frame, text="LEXEMES",font=bold_font,fg='white',background='#1F1F1F')
        self.lex_label.pack(side=tk.TOP)

        style = ttk.Style()
        style.configure("Treeview", background="#292929", fieldbackground="#292929", foreground="white")
        style.configure("Treeview.Heading", background="#292929", foreground="black")  

        style.map("Treeview", background=[("selected", "black")], foreground=[("selected","white")])

        self.lex_text = ttk.Treeview(self.lex_frame, columns = ("Lexemes","Tokens"), show = "headings", style="Treeview")
        self.lex_text.heading("Lexemes", text="Lexemes")
        self.lex_text.heading("Tokens", text="Tokens")
        self.lex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lex_scrollbar = tk.Scrollbar(self.lex_frame, orient=tk.VERTICAL, command=self.lex_text.yview, background="grey")
        self.lex_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lex_text.config(yscrollcommand=self.lex_scrollbar.set)

        #GRID
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 8)
        self.root.columnconfigure(2, weight = 16)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=40)

        self.title_frame.grid(row=0, column=0, columnspan=3,sticky='nswe')
        self.file_frame.grid(row=1,column=0,sticky='nswe')
        self.code_frame.grid(row=1,column=1,sticky='nswe')
        self.lex_frame.grid(row=1,column=2,sticky='nswe')

    def open_file(self):
        new_file = fd.askopenfilename(title="Open LOLCODE file")
        with open(new_file, 'r', encoding='UTF-8-sig') as file:
            file_arr = []
            for line in file:
                file_arr.append(line)
        self.file = file_arr

    def tokenize(self,code):
        if self.multi_bool == False:
            tokenized = get_token(code)
            token_arr = []
        else:
            tokenized = get_token2(code)
            token_arr = []

        while tokenized is not None:
            type = tokenized.lastgroup
            value = tokenized.group(type)

            if type == 'ERROR':
                self.error = True
                break

            elif type == 'MULTI_LINE_COMMENT_END':
                self.multi_bool = False
                token_arr.append((value.strip(), type))
                tokenized = get_token(code, tokenized.end())
                continue

            elif self.multi_bool == True:
                if type != 'NEWLINE':
                    token_arr.append((value.strip(), type))
                tokenized = get_token2(code, tokenized.end())
                continue

            elif type == 'SINGLE_LINE_COMMENT':
                token_arr.append((value.strip(), type))
                tokenized = get_token2(code, tokenized.end())
                continue

            elif type == 'MULTI_LINE_COMMENT_START':
                token_arr.append((value.strip(), type)) 
                tokenized = get_token(code, tokenized.end()) 
                self.multi_bool = True
                continue

            elif type not in ['SPACE', 'NEWLINE']:                    # Ignore spaces and newlines
                token_arr.append((value.strip(), type))

            tokenized = get_token(code, tokenized.end())
        return token_arr

    def lexical(self):
        file_arr = self.file
        print(f"{'Lexeme':<40} {'Token Type':<40} {'Line':<40}")
        print("=" * 85)

        all=[]
        self.multi_bool = False
        self.error = False

        for line_number, line in enumerate(file_arr, start=1):
            if self.error != True:
                tokens = self.tokenize(line)
                all.append(tokens)
                if self.error != True:
                    for value, type_ in tokens:
                        print(f"{value:<40} {type_:<40} {line_number:<40}")
                else:
                    print("Error: Lexeme Mismatch")
        
        for word in file_arr:
            self.code_text.insert(tk.END,word)

        if(self.error == True):
            self.lex_text.insert("", "end", values=("ERROR", "ERROR"))
            return
        else:
            for lexeme in all:
                if(len(lexeme) != 0):
                    for i in range(len(lexeme)):
                        self.lex_text.insert("", "end", values=(lexeme[i][0], lexeme[i][1]))
                        
        self.syntax_analyze(''.join(file_arr))



    def match(self, type):
        current = self.tokens[self.pos]

        if current and current[1] == type:
            self.pos += 1
            return True
        else:
            return False
        
    def syntax_analyze(self, code):
        self.tokens = self.tokenize(code)
        self.errors = []
        self.pos = 0
        self.parse_program()

        if self.errors:
            print("Syntax Error:")

            for error in self.errors:
                print(error)
        else:
            print("Completed successfully!")

    def parse_program(self):

        if self.tokens[self.pos][1] == 'SINGLE_LINE_COMMENT':
            self.pos += 1
            self.match('COMMENT_BODY')
        
        elif self.tokens[self.pos][1] == 'MULTI_LINE_COMMENT_START':
            self.pos += 1
            self.match('COMMENT_BODY')
            if not self.match('MULTI_LINE_COMMENT_END'):
                self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos]}")

        if not self.match('PROGRAM_START'):
            self.errors.append(f"Error: Expected {'PROGRAM_START'}, found {self.tokens[self.pos]}")

        count = len(self.tokens)
        
        while self.pos < count:
            curr = self.tokens[self.pos]
            if curr[1] == 'PROGRAM_END':
                self.match('PROGRAM_END')
                break

            if self.tokens[self.pos][1] == 'SINGLE_LINE_COMMENT':
                self.pos += 1
                self.match('COMMENT_BODY')
        
            elif self.tokens[self.pos][1] == 'MULTI_LINE_COMMENT_START':
                self.pos += 1
                self.match('COMMENT_BODY')
                if not self.match('MULTI_LINE_COMMENT_END'):
                    self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos]}")

            elif curr[1] == 'DECLARATION':
                self.match('DECLARATION')
                self.declaration()

            elif curr[1] == 'INPUT':
                self.match('INPUT')
                self.getinput()

            elif curr[1] == 'PRINT':
                self.match('PRINT')
                self.printoutput()

            elif curr[1] == 'CONDITIONAL':
                self.match('CONDITIONAL')
                self.conditionals()

            elif curr[1] == 'LOOP':
                self.match('LOOP')
                self.loops()

            elif curr[1] == 'ARITHMETIC':
                self.match('ARITHMETIC')
                self.arithmetic()

            elif curr[1] == 'ASSIGNMENT':
                self.match('ASSIGNMENT')
                self.assignment()
            
            elif curr[1] == 'SWITCH':
                self.match('SWITCH')
                self.switch()

            elif curr[1] == 'FUNCTION':
                self.match('FUNCTION')
                self.function()

            else:
                self.errors.append(f"Error: Unexpected token {curr[1]}")
                self.pos += 1

    def declaration(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected {'IDENTIFIER'}, but found {self.tokens[self.pos][1]}")

        if not self.match('DECLARATION_ASSIGNMENT'):
            pass
        else:
            if not self.match('IDENTIFIER'):
                self.errors.append(f"Error: Expected 'IDENTIFIER',but found {self.tokens[self.pos][1]}")

    def getinput(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")

    def printoutput(self):
        while self.pos < len(self.tokens):
            if self.tokens[self.pos][1] in ['YARN', 'NUMBR', 'NUMBAR', 'TROOF', 'IDENTIFIER', 'CONNECTOR']:
                self.pos += 1
            else:
                break
    
    def loops(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")
            
        if not self.match('TIL'):
            self.errors.append(f"Error: Expected 'TIL', but found {self.tokens[self.pos][1]}")

    def conditionals(self):
        if not self.match('CONDITIONAL'):
            self.errors.append(f"Error: Expected 'CONDITIONAL', but found {self.tokens[self.pos][1]}")

        if not self.match('YA RLY'):
            self.errors.append(f"Error: Expected 'YA RLY', but found {self.tokens[self.pos][1]}")

        self.expression()

        if not self.match('NO WAI'):
            self.errors.append(f"Error: Expected 'NO WAI', but found {self.tokens[self.pos][1]}")

        if not self.match('OIC'):
            self.errors.append(f"Error: Expected 'OIC', but found {self.tokens[self.pos][1]}")
    
    def arithmetic(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")

        while self.match('CONNECTOR'):
            if not self.match('IDENTIFIER'):
                self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")

    def assignment(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")
        
        if not self.match('ASSIGNMENT'):
            self.errors.append(f"Error: Expected 'ASSIGNMENT', but found {self.tokens[self.pos][1]}")
        
        self.expression()

    def switch(self):
        if not self.match('SWITCH'):
            self.errors.append(f"Error: Expected 'SWITCH', but found {self.tokens[self.pos][1]}")

        while self.pos < len(self.tokens):
            if self.match('OMG'):
                self.expression()
            elif self.match('OMGWTF'):
                self.expression()
            elif self.match('OIC'):
                break
            else:
                self.errors.append(f"Error: Unexpected token in SWITCH {self.tokens[self.pos][1]}")
                self.pos += 1

    def function(self):
        if not self.match('FUNCTION'):
            self.errors.append(f"Error: Expected 'FUNCTION', but found {self.tokens[self.pos][1]}")
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")
        
        while self.pos < len(self.tokens):
            curr = self.tokens[self.pos]
            if curr[1] == 'FOUND YR':
                self.match('FOUND YR')
                self.expression()
            elif curr[1] == 'IF U SAY SO':
                self.match('IF U SAY SO')
                break
            else:
                self.parse_program()

    def expression(self):
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'IDENTIFIER']:
            self.pos += 1
        else:
            self.errors.append(f"Error: Expected an expression, but found {self.tokens[self.pos][1]}")
        
    def reset(self):
        self.code_text.delete(1.0, tk.END)
        for item in self.lex_text.get_children():
            self.lex_text.delete(item)

#CREATE AND RUN THE APP
root = tk.Tk()
app = LOL(root)
root.mainloop()