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
#------------------------------------------------ GUI --------------------------------------------------------------------------------------
    def __init__(self, root):
        self.root = root
        self.file = None
        self.root.geometry("1500x700")
        self.root.title("HELLO, HAI, KTHXBYE INTERPRETER")
        self.create_widgets()
        self.symbol_table = {}  

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

        #SYNTAX FRAME
        self.syntax_frame = tk.Frame(self.root, background="#1F1F1F")
        self.syntax_label = tk.Label(self.syntax_frame, text="INTERPRETER",font=bold_font,fg='white',background='#1F1F1F')
        self.syntax_label.pack(side=tk.TOP)

        style = ttk.Style()
        style.configure("Treeview", background="#292929", fieldbackground="#292929", foreground="white")
        style.configure("Treeview.Heading", background="#292929", foreground="black")  

        style.map("Treeview", background=[("selected", "black")], foreground=[("selected","white")])

        self.syntax_text = ttk.Treeview(self.syntax_frame, columns = ("Error"), show = "headings", style="Treeview")
        self.syntax_text.heading("Error", text="Error")
        self.syntax_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.syntax_scrollbar = tk.Scrollbar(self.syntax_frame, orient=tk.VERTICAL, command=self.syntax_text.yview, background="grey")
        self.syntax_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.syntax_text.config(yscrollcommand=self.lex_scrollbar.set)

        #GRID
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 8)
        self.root.columnconfigure(2, weight = 16)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=40)
        self.root.rowconfigure(2, weight=40)

        self.title_frame.grid(row=0, column=0, columnspan=3,sticky='nswe')
        self.file_frame.grid(row=1,column=0, rowspan=3,sticky='nswe')
        self.code_frame.grid(row=1,column=1, rowspan=3,sticky='nswe')
        self.lex_frame.grid(row=1,column=2,sticky='nswe')
        self.syntax_frame.grid(row=2,column=2,sticky='nswe')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------- LEXICAL ENALYZER --------------------------------------------------------------------------------------------
    def open_file(self):
        new_file = fd.askopenfilename(title="Open LOLCODE file", filetypes=[("LOLCODE Files", "*.lol"), ("All Files", "*.*")])
        if new_file:
            with open(new_file, 'r', encoding='UTF-8-sig') as file:
                file_arr = []
                for line in file:
                    file_arr.append(line)
            self.file = file_arr
    
            self.code_text.delete(1.0, tk.END)
            for line in file_arr:
                self.code_text.insert(tk.END, line)

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
        for i in token_arr:
            print (i)
        print("Token Array: ", token_arr)
        return token_arr

    def lexical(self):
        self.lexical_analyze_button.config(state=tk.DISABLED)
        code_content = self.code_text.get("1.0", tk.END).strip()
        if not code_content: 
            messagebox.showwarning("No Code", "Text editor is empty!")
            return

        print(f"{'Lexeme':<40} {'Token Type':<40} {'Line':<40}")
        print("=" * 85)

        all_tokens = []
        self.lex_line = []
        self.multi_bool = False
        self.error = False

        file_arr = code_content.splitlines() 

        for line_number, line in enumerate(file_arr, start=1):
            if self.error:
                break
            self.lex_line.append(line_number)
            tokens = self.tokenize(line)
            all_tokens.append(tokens)
            if not self.error:
                for value, type_ in tokens:
                    print(f"{value:<40} {type_:<40} {line_number:<40}")
            else:
                print("Lexeme Error: Lexeme Mismatch")

        if self.error:
            self.lex_text.insert("", "end", values=("ERROR", "ERROR"))
            return

        for lexeme in all_tokens:
            if lexeme:
                for i in range(len(lexeme)):
                    self.lex_text.insert("", "end", values=(lexeme[i][0], lexeme[i][1]))

        self.syntax_analyze(code_content)

        print("SYMBOL TABLE: \n",self.symbol_table)

        
#-------------------------------------------------------------------------------------------------------------------------------------------     

#------------------------------------------------- SYNTAX ANALYZER -------------------------------------------------------------------------
    def match(self, type):
        current = self.tokens[self.pos]

        if current and (current[1] == type or current[0] == type):
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
                self.syntax_text.insert("", "end", values=(error,))

        else:
            print("Completed successfully!")
            self.syntax_text.insert("", "end", values=("Completed",))

    def parse_program(self):

        if self.tokens[self.pos][1] == 'SINGLE_LINE_COMMENT':
            self.pos += 1
            self.match('COMMENT_BODY')
        
        elif self.tokens[self.pos][1] == 'MULTI_LINE_COMMENT_START':
            self.pos += 1
            self.match('COMMENT_BODY')
            if not self.match('MULTI_LINE_COMMENT_END'):
                self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]}")

        if not self.match('PROGRAM_START'):
            self.errors.append(f"Error: Expected {'PROGRAM_START'}, found {self.tokens[self.pos][1]}")

        count = len(self.tokens)
        
        while self.pos < count:
            if self.tokens[-1][1] != 'PROGRAM_END':
                self.errors.append(f"Error: Expected {'PROGRAM_END'}, found {self.tokens[self.pos][1]}")
                break
            curr = self.tokens[self.pos]
            print("Current", curr)
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
                    self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]}")

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
                self.function()

            elif curr[1] == 'VARIABLE_START':
                self.variables_start()

                while self.tokens[self.pos][1] != 'VARIABLE_END':

                    if self.tokens[self.pos][1] == 'DECLARATION':
                        self.match('DECLARATION')
                        self.declaration()

                    elif self.tokens[self.pos][1] == 'SINGLE_LINE_COMMENT':
                        self.pos += 1
                        self.match('COMMENT_BODY')
                
                    elif self.tokens[self.pos][1] == 'MULTI_LINE_COMMENT_START':
                        self.pos += 1
                        self.match('COMMENT_BODY')
                        if not self.match('MULTI_LINE_COMMENT_END'):
                            self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]}")
                    else:
                        self.pos += 1
                        print("ERRORRRRRRR")

                self.variables_end()
            else:
                self.errors.append(f"Syntax Error: Unexpected token {curr[1]}")
                self.pos += 1
                break

    def variables_start(self):
        if not self.match('VARIABLE_START'):
            self.errors.append(f"Syntax Error: Expected {'VARIABLE_START'}, but found {self.tokens[self.pos][1]}")


    def variables_end(self):
        if not self.match('VARIABLE_END'):
            self.errors.append(f"Syntax Error: Expected {'VARIABLE_END'}, but found {self.tokens[self.pos][1]}")


    def declaration(self):
        if self.tokens[self.pos][1] == ('IDENTIFIER'):
            var_name = self.tokens[self.pos][0] 
            self.match('IDENTIFIER')
        else:
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")
            return

        if not self.match('DECLARATION_ASSIGNMENT'):
            self.symbol_table[var_name] = 'NOVAL'
            return
        
        var_type = self.tokens[self.pos][1]  
        

        self.symbol_table[var_name] = var_type
        print(f"Declared {var_name} of type {var_type}")


        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            self.pos += 1  

    def getinput(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")

    def printoutput(self):
        while self.pos < len(self.tokens):
            if self.tokens[self.pos][1] in ['YARN', 'NUMBR', 'NUMBAR', 'TROOF', 'IDENTIFIER', 'CONNECTOR', 'ARITHMETIC']:
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
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR','IDENTIFIER']:
            if self.tokens[self.pos][0] not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{self.tokens[self.pos][0] }' is not declared")
            self.pos += 1
        else:
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")

        while self.match('CONNECTOR'):
            if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR','IDENTIFIER']:
                if self.tokens[self.pos][0] not in self.symbol_table:
                    self.errors.append(f"Semantic Error: Variable '{self.tokens[self.pos][0] }' is not declared")
                self.pos += 1
            else:
                self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")


    def assignment(self):
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]}")
            return
        
        var_name = self.tokens[self.pos][0] 
        if var_name not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared")
            return

        self.pos += 1  

        if not self.match('ASSIGNMENT'):
            self.errors.append(f"Syntax Error: Expected 'R', but found {self.tokens[self.pos][1]}")
            return

        self.expression()

    def switch(self):
        if not self.match('SWITCH'):
            self.errors.append(f"Syntax Error: Expected 'SWITCH', but found {self.tokens[self.pos][1]}")

        while self.pos < len(self.tokens):
            if self.match('OMG'):
                self.expression()
            elif self.match('OMGWTF'):
                self.expression()
            elif self.match('OIC'):
                break
            else:
                self.errors.append(f"Syntax Error: Unexpected token in SWITCH {self.tokens[self.pos][1]}")
                self.pos += 1

    def function(self):
        if not self.tokens[self.pos][0] == 'HOW IZ I':
            if not self.tokens[self.pos][0] == 'IF U SAY SO':
                if not self.tokens[self.pos][0] == 'I IZ':
                    self.errors.append(f"Syntax Error: Expected 'FUNCTION', but found {self.tokens[self.pos][1]}")        
        while self.pos < len(self.tokens):
            curr = self.tokens[self.pos]
            if curr[0] == 'FOUND YR':
                self.match('FOUND YR')
            elif curr[0] == 'IF U SAY SO':
                self.match('IF U SAY SO')
                return True
            elif curr[0] == 'GTFO':
                self.match('GTFO')
                return True
            elif curr[1] == 'ARITHMETIC':
                self.match('ARITHMETIC')
            elif curr[1] == 'PRINT':
                self.match("PRINT")
                self.printoutput()
            elif curr[0] == 'YR':
                self.match('YR')
            elif curr[0] == 'AN':
                self.match('AN')
            elif curr[1] in ['NUMBR', 'NUMBAR', 'YARN', 'IDENTIFIER']:
                self.expression()
            elif curr[1] == 'FUNCTION':
                self.match('FUNCTION')
            else:
                return False

    def expression(self):
        """ Handle expressions, evaluating or checking types """
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'IDENTIFIER']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0]
                if var_name not in self.symbol_table:
                    self.errors.append(f"Error: Variable '{var_name}' is not declared")
            self.pos += 1
        else:
            self.errors.append(f"Syntax Error: Expected an expression, but found {self.tokens[self.pos][1]}")
    
    def reset(self):
        # self.code_text.delete(1.0, tk.END)
        self.lexical_analyze_button.config(state=tk.NORMAL)
        self.symbol_table.clear()
        for item in self.lex_text.get_children():
            self.lex_text.delete(item)
        for item in self.syntax_text.get_children():
            self.syntax_text.delete(item)

#CREATE AND RUN THE APP
root = tk.Tk()
app = LOL(root)
root.mainloop()