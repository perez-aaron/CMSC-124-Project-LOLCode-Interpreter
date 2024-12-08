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
    ('BOOLEAN', r'(BOTH OF)|(EITHER OF)|(WON OF)|(NOT)|(ALL OF)|(ANY OF)'),
    ('CONNECTOR', r'AN|\+'),
    ('CONCATENATION', r'SMOOSH'),
    ('ARITHMETIC', r'(SUM OF)|(DIFF OF)|(PRODUKT OF)|(QUOSHUNT OF)|(BIGGR OF)|(SMALLR OF)|(MOD OF)'),
    ('COMPARISON', r'(BOTH SAEM)|(DIFFRINT)'),
    ('TYPECAST', r'(MAEK)|(IS NOW A)|(A)'),
    ('CONDITIONAL', r'(O RLY\?|YA RLY|MEBBE|NO WAI|OIC)'),
    ('SWITCH', r'(WTF\?|OMGWTF|OMG)'),
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
        self.tokens = []
        self.root.geometry("1500x700")
        self.root.title("HELLO, HAI, KTHXBYE INTERPRETER")
        self.create_widgets()
        self.symbol_table = []  

    def create_widgets(self):
        bold_font = font.Font(family="Helvetica", size=12, weight="bold")

        # TITLE FRAME
        self.title_frame = tk.Frame(self.root, background="#181818")
        self.title_label = tk.Label(self.title_frame, text="HELLO, HAI, KTHXBYE INTERPRETER", font=bold_font, background='#181818', fg='white')
        self.title_label.pack(expand=True)

        # FILE FRAME
        self.file_frame = tk.Frame(self.root, background="#181818")
        self.file_button = tk.Button(self.file_frame, text="FILE", background='#1F1F1F', fg='white', font=bold_font, width=10, height=2, command=self.open_file)
        self.file_button.pack(side=tk.TOP, padx=10, pady=10)
        self.lexical_analyze_button = tk.Button(self.file_frame, text="ANALYZE", background='#1F1F1F', fg='white', font=bold_font, width=10, height=2, command=self.lexical)
        self.lexical_analyze_button.pack(side=tk.TOP, padx=10, pady=10)
        self.reset_button = tk.Button(self.file_frame, text="RESET", background='#1F1F1F', fg='white', font=bold_font, width=10, height=2, command=self.reset)
        self.reset_button.pack(side=tk.TOP, padx=10, pady=10)

            # CODEBASE FRAME
        self.code_frame = tk.Frame(self.root, background="#1F1F1F")
        self.code_label = tk.Label(self.code_frame, text="CODE", font=bold_font, fg='white', background='#1F1F1F')
        self.code_label.pack(side=tk.TOP)

        self.line_numbers = tk.Text(self.code_frame, width=4, wrap=tk.NONE, background='#292929', fg='grey', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_text = tk.Text(self.code_frame, wrap=tk.WORD, background='#292929', fg='white')
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.code_scrollbar = tk.Scrollbar(self.code_frame, command=self.sync_scroll, background="grey")
        self.code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.code_text.config(yscrollcommand=self.code_scrollbar.set)
        self.code_text.bind('<KeyRelease>', self.update_line_numbers)
        # self.code_text.bind('<MouseWheel>', self.sync_scroll)

        self.code_text.config(yscrollcommand=self.sync_code_scroll)
        self.line_numbers.config(yscrollcommand=self.sync_line_scroll)

        #LEXEMES FRAME
        self.lex_frame = tk.Frame(self.root, background="#1F1F1F")
        self.lex_label = tk.Label(self.lex_frame, text="LEXEMES",font=bold_font,fg='white',background='#1F1F1F')
        self.lex_label.pack(side=tk.TOP)

        style = ttk.Style()
        style.configure("Treeview", background="#292929", fieldbackground="#292929", foreground="white")
        style.configure("Treeview.Heading", background="#292929", foreground="black")  

        style.map("Treeview", background=[("selected", "black")], foreground=[("selected","white")])

        self.lex_text = ttk.Treeview(self.lex_frame, columns = ("Lexemes","Tokens", "Lines"), show = "headings", style="Treeview")
        self.lex_text.heading("Lexemes", text="Lexemes")
        self.lex_text.heading("Tokens", text="Tokens")
        self.lex_text.heading("Lines", text="Lines")
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

    def sync_scroll(self, *args):
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)
    def sync_code_scroll(self, *args):
        self.line_numbers.yview_moveto(args[0])
        self.code_scrollbar.set(*args)

    def sync_line_scroll(self, *args):
        self.code_text.yview_moveto(args[0])
        self.code_scrollbar.set(*args)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)

        line_count = self.code_text.index('end-1c').split('.')[0]
        lines = "\n".join(str(i) for i in range(1, int(line_count) + 1))
        self.line_numbers.insert(1.0, lines)

        self.line_numbers.config(state='disabled')


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
            
            self.update_line_numbers()

    def tokenize(self,code, line):
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
                token_arr.append((value.strip(), type, line))
                tokenized = get_token(code, tokenized.end())
                continue

            elif self.multi_bool == True:
                if type != 'NEWLINE':
                    token_arr.append((value.strip(), type, line))
                tokenized = get_token2(code, tokenized.end())
                continue

            elif type == 'SINGLE_LINE_COMMENT':
                token_arr.append((value.strip(), type, line))
                tokenized = get_token2(code, tokenized.end())
                continue

            elif type == 'MULTI_LINE_COMMENT_START':
                token_arr.append((value.strip(), type, line)) 
                tokenized = get_token(code, tokenized.end()) 
                self.multi_bool = True
                continue

            elif type not in ['SPACE', 'NEWLINE']:                    # Ignore spaces and newlines
                token_arr.append((value.strip(), type, line))

            tokenized = get_token(code, tokenized.end())
        for i in token_arr:
            pass
            # print (i)
        # print("Token Array: ", token_arr)
        return token_arr

    def lexical(self):
        self.lexical_analyze_button.config(state=tk.DISABLED)
        code_content = self.code_text.get("1.0", tk.END).strip()
        if not code_content: 
            messagebox.showwarning("No Code", "Text editor is empty!")
            return

        # print(f"{'Lexeme':<40} {'Token Type':<40} {'Line':<40}")
        # print("=" * 85)

        all_tokens = []
        self.lex_line = []
        self.multi_bool = False
        self.error = False

        file_arr = code_content.splitlines() 

        for line_number, line in enumerate(file_arr, start=1):
            if self.error:
                break
            self.lex_line.append(line_number)
            tokens = self.tokenize(line, line_number)
            self.tokens.append(tokens)
            all_tokens.append(tokens)
            # if not self.error:
            #     for value, type_ ,line in tokens:
            #         print(f"{value:<40} {type_:<40} {line_number:<40}")
            # else:
            #     print("Lexeme Error: Lexeme Mismatch")

        if self.error:
            self.lex_text.insert("", "end", values=("ERROR", "ERROR"))
            return

        for i in range (len(all_tokens)):
            if all_tokens[i]:
                for j in range(len(all_tokens[i])):
                    self.lex_text.insert("", "end", values=(all_tokens[i][j][0], all_tokens[i][j][1], self.lex_line[i]))
                    
        self.syntax_analyze()

        print("SYMBOL TABLE:\n", self.symbol_table)

        
#-------------------------------------------------------------------------------------------------------------------------------------------     

#------------------------------------------------- SYNTAX AND SEMANTIC ANALYZER-------------------------------------------------------------------------
    def match(self, type):
        current = self.tokens[self.pos]

        if current and (current[1] == type or current[0] == type):
            self.pos += 1
            return True
        else:
            return False   


    def syntax_analyze(self):

        self.tokens = [item for sublist in self.tokens for item in sublist]
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

        while self.tokens[self.pos][1] in ['SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT_START']:

            if self.tokens[self.pos][1] == 'SINGLE_LINE_COMMENT':
                self.pos += 1
                self.match('COMMENT_BODY')
            
            elif self.tokens[self.pos][1] == 'MULTI_LINE_COMMENT_START':
                self.pos += 1
                self.match('COMMENT_BODY')
                if not self.match('MULTI_LINE_COMMENT_END'):
                    self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")

        if not self.match('PROGRAM_START'):
            self.errors.append(f"Error: Expected {'PROGRAM_START'}, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")

        count = len(self.tokens)
        
        while self.pos < count:
            if self.tokens[-1][1] != 'PROGRAM_END':
                self.errors.append(f"Error: Expected {'PROGRAM_END'}, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                break
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
                    self.errors.append(f"Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")

            elif curr[1] == 'DECLARATION':
                self.match('DECLARATION')
                self.declaration()

            elif curr[1] == 'INPUT':
                self.match('INPUT')
                val = self.getinput()

                if val == 'err':
                    return

            elif curr[1] == 'PRINT':
                self.match('PRINT')
                val = self.printoutput()

                if val == 'err':
                    return

            elif curr[1] == 'CONDITIONAL':
                self.match('CONDITIONAL')
                self.conditionals()

            elif curr[1] == 'LOOP':
                self.match('LOOP')
                self.loops()

            elif curr[1] == 'ARITHMETIC':
                self.match('ARITHMETIC')
                self.arithmetic()

            elif curr[1] == 'IDENTIFIER':
                self.match('IDENTIFIER')
                if self.tokens[self.pos][1] == 'ASSIGNMENT':
                    self.match('ASSIGNMENT')
                    self.pos -= 2
                    self.assignment()
                    self.pos += 1
                elif self.tokens[self.pos][1] == 'TYPECAST':
                    self.match('TYPECAST')
                    self.pos -= 2
                    self.typecast()
                    self.pos += 1
                elif self.tokens[self.pos][1] == 'SWITCH':
                    self.match('SWITCH')
                    self.switch()
                else:
                    self.pos += 1

            elif curr[1] == 'TYPECAST':
                self.match('TYPECAST')
            

            elif curr[1] == 'BOOLEAN':
                self.match('BOOLEAN')
                self.boolean()

            
            elif curr[1] == 'COMPARISON':
                self.comparison()
            
            elif curr[1] == 'SWITCH':
                self.match('SWITCH')
                self.switch()

            elif curr[1] == 'FUNCTION':
                self.function()
            
            elif curr[1] == 'CONCATENATION':
                self.match('CONCATENATION')
                self.expression()
                if not self.match('AN'):
                    self.errors.append(f"Syntax Error: Expected {'CONNECTOR'}, found {self.tokens[self.pos-1][1]} at line {self.tokens[self.pos-1][2]}")
                    return
                self.expression()

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
                            self.errors.append(f"Syntax Error: Expected {'MULTI_LINE_COMMENT_END'}, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                            return
                    else:
                        self.pos += 1
                    
                    if len(self.tokens) <= self.pos:
                        self.errors.append(f"Syntax Error: Expected 'VARIABLE_END', found {self.tokens[self.pos-1][1]} at line {self.tokens[self.pos-1][2]}")
                        return

                self.variables_end()

            else:
                self.errors.append(f"Syntax Error: Unexpected token {curr[1]} at line {self.tokens[self.pos][2]}")
                self.pos += 1
                break
    def comparison(self):
        if not self.match('COMPARISON'):
            self.errors.append(f"Syntax Error: Expected {'COMPARISON'}, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return
        
        if self.tokens[self.pos][1] == 'ARITHMETIC':
            self.match('ARITHMETIC')
            self.arithmetic()
            self.match('AN')

            if self.tokens[self.pos][1] == 'ARITHMETIC':
                self.match('ARITHMETIC')
                self.arithmetic()
            else:
                self.expression()

        elif self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'TROOF', 'YARN', 'IDENTIFIER']:
            self.expression()
            self.match('AN')
            if self.tokens[self.pos][1] == 'ARITHMETIC':
                self.match('ARITHMETIC')
                self.arithmetic()
            else:
                self.expression()
        else:
            self.expression()
            self.match('AN')
            self.expression()

    def variables_start(self):
        if not self.match('VARIABLE_START'):
            self.errors.append(f"Syntax Error: Expected {'VARIABLE_START'}, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

    def variables_end(self):
        if not self.match('VARIABLE_END'):
            self.errors.append(f"Syntax Error: Expected {'VARIABLE_END'}, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

    def declaration(self):
        if self.tokens[self.pos][1] == ('IDENTIFIER'):
            var_name = self.tokens[self.pos][0] 
            self.match('IDENTIFIER')    
        else:
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

        if not self.match('DECLARATION_ASSIGNMENT'):
            self.symbol_table.append(('NOOB', var_name, None))
            return
        
        var_type = self.tokens[self.pos][1]  
        var_value = None

        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            var_value = self.tokens[self.pos][0]
            self.pos += 1
        

        self.symbol_table.append((var_type, var_name, var_value))
        print(f"Declared {var_name} of type {var_type}")


        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            self.pos += 1  

    def getinput(self):
        var_name = self.tokens[self.pos][0] 
        variable = next((var for var in self.symbol_table if var[1] == var_name), None)

        if not variable:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            return 'err'
        
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return 'err'

    def printoutput(self):
        while self.pos < len(self.tokens):
            if self.tokens[self.pos][1] in ['YARN', 'NUMBR', 'NUMBAR', 'TROOF', 'IDENTIFIER', 'CONNECTOR', 'ARITHMETIC', 'CONCATENATION', 'COMPARISON', 'BOOLEAN', 'CONFIRMATION'] and self.tokens[self.pos][2] == self.tokens[self.pos-1][2]:
                #declaration check, print output must call the other functions not just check the type ok so this is still work in progress
                if self.tokens[self.pos][1] == 'IDENTIFIER':
                    var_name = self.tokens[self.pos][0] 
                    variable = next((var for var in self.symbol_table if var[1] == var_name), None)

                    if not variable:
                        self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                        return 'err'

                self.pos += 1
            else:
                break


    def boolean(self):

        var_name = self.tokens[self.pos][0] 
        variable = next((var for var in self.symbol_table if var[1] == var_name), None)

        if not variable:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            return
        
        if not self.match('IDENTIFIER'):
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

        cnt = 0

        while self.tokens[self.pos][1] == 'CONNECTOR':
            self.match('CONNECTOR')
            if self.tokens[self.pos][1] in ['IDENTIFIER', 'NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
                self.match(self.tokens[self.pos][1])
            else:
                self.errors.append(f"Error: Expected 'EXPRESSION', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            cnt += 1
        
        if cnt > 1:
            if not self.match('CONFIRMATION'):
                self.errors.append(f"Error: Expected 'CONFIRMATION', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                return



    
    def loops(self):
        loopname = self.tokens[self.pos][0]

        if not self.match('IDENTIFIER'):
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

        while self.tokens[self.pos][2] == self.tokens[self.pos-1][2]:
            print("THISISSS DOOOEEEE", self.tokens[self.pos])
            if self.tokens[self.pos][0] == 'UPPIN':
                self.match('UPPIN')
                self.match('YR')
                self.match('EXPRESSION')
            elif self.tokens[self.pos][0] == 'NERFIN':
                self.match('NERFIN')
                self.match('YR')
                self.match('EXPRESSION')
            elif self.tokens[self.pos][0] in ['TIL', 'WILE']:
                self.match('LOOP')
                if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR','IDENTIFIER', 'YARN', 'TROOF']:
                    self.expression()
                elif self.tokens[self.pos][1] == 'COMPARISON':
                    self.comparison()
                else:
                    self.errors.append(f"Syntax Error: Expected 'EXPRESSION', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                    return
            else:
                self.pos += 1
        
        while self.tokens[self.pos][0] != 'IM OUTTA YR':
            print("BUTTTTTTT DOOOEEEE", self.tokens[self.pos])
            if self.tokens[self.pos][1] == 'PRINT':
                self.match('PRINT')
                val = self.printoutput()
                if val == 'err':
                    return

            elif self.tokens[self.pos][1] == 'INPUT':
                self.match('INPUT')
                val = self.getinput()
                if val == 'err':
                    return 
            else:
                self.pos += 1
        
        if self.tokens[self.pos][0] == 'IM OUTTA YR':
            self.match("LOOP")
            if loopname == self.tokens[self.pos][0]:
                self.match('IDENTIFIER')
        else:
            return
        


    def conditionals(self):
        if not self.match('YA RLY'):
            self.errors.append(f"Syntax Error: Expected 'YA RLY', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

        while not self.tokens[self.pos][0] in  ['OIC', 'NO WAI']:
            if self.tokens[self.pos][1] == 'PRINT':
                self.match('PRINT')
                val = self.printoutput()
                if val == 'err':
                    return

            elif self.tokens[self.pos][1] == 'INPUT':
                self.match('INPUT')
                val = self.getinput()
                if val == 'err':
                    return
            else:
                self.pos += 1

        if self.tokens[self.pos][0] == 'NO WAI':
            self.match('NO WAI')

            while self.tokens[self.pos][0] != 'OIC':
                if self.tokens[self.pos][1] == 'PRINT':
                    self.match('PRINT')
                    val = self.printoutput()
                    if val == 'err':
                        return
                elif self.tokens[self.pos][1] == 'INPUT':
                    self.match('INPUT')
                    val = self.getinput()
                    if val == 'err':
                        return
                else:
                    self.errors.append(f"Syntax Error: Expected 'ERRRORR', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                    return
            
            if self.tokens[self.pos][0] == 'OIC':
                self.match('OIC')
                return
            else:
                self.errors.append(f"Syntax Error: Expected 'OIC', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                return

        elif self.tokens[self.pos][0] == 'OIC':
            self.match('OIC')
            return
        else:
            self.errors.append(f"Syntax Error: Expected 'NO WAI or OIC', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

      

    def arithmetic(self):
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR','IDENTIFIER']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':

                var_name = self.tokens[self.pos][0] 
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)

                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                    return
                
            self.pos += 1
        else:
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")

    
        self.match('CONNECTOR')
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR','IDENTIFIER']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0] 
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)

                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                    return
                
            self.pos += 1
        else:
            self.errors.append(f"Syntax Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")


    def assignment(self):    
        var_name = self.tokens[self.pos][0] 
        variable = next((var for var in self.symbol_table if var[1] == var_name), None)

        if not variable:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            self.pos += 2
            return
        
        self.pos += 1

        if self.tokens[self.pos][1] == 'ASSIGNMENT':
            self.match('ASSIGNMENT')
            
            if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
                if self.tokens[self.pos][1] in ['YARN', 'TROOF']:
                    new_value = self.tokens[self.pos][0]
                else:
                    new_value = int(self.tokens[self.pos][0])

                self.symbol_table = [(var_type, var_name, new_value) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]
                
            elif self.tokens[self.pos][1] == 'TYPECAST':
                self.match('TYPECAST')
                self.typecast()

            elif self.tokens[self.pos][1] == 'CONCATENATION':
                self.match('CONCATENATION')
                self.expression()
                if not self.match('AN'):
                    self.errors.append(f"Syntax Error: Expected {'CONNECTOR'}, found {self.tokens[self.pos-1][1]} at line {self.tokens[self.pos-1][2]}")
                    return
                self.expression()

                self.pos -= 1

            else:
                self.errors.append(f"Syntax Error: Expected 'TYPECAST OR IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                print(f"Found {self.tokens[self.pos][0]}")
                return

        else:
            self.errors.append(f"Syntax Error: Expected 'ASSIGNMENT', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            print(f"Found {self.tokens[self.pos][0]}")
            return
        


    def switch(self):

        print(self.tokens[self.pos])
        while self.tokens[self.pos][0] in ['OMG', 'OMGWTF', 'OIC']:

            if self.tokens[self.pos][0] == 'OMG':
                self.match('OMG')
                self.expression()
                print('ABOT BA ADITO')
                while not self.tokens[self.pos][0] in ['OMG', 'OMGWTF', 'OIC']:
                    if self.tokens[self.pos][1] == 'PRINT':
                        self.match('PRINT')
                        val = self.printoutput()
                        if val == 'err':
                            return
                    elif self.tokens[self.pos][1] == 'INPUT':
                        self.match('INPUT')
                        val = self.getinput()
                        if val == 'err':
                            return
                    elif self.tokens[self.pos][0] == 'GTFO':
                        self.match('GTFO')
                        break
                    else:
                        self.pos += 1

            elif self.tokens[self.pos][0] == 'OMGWTF':
                self.match('OMGWTF')

                while not self.tokens[self.pos][0] in ['OMG', 'OMGWTF', 'OIC']:
                    if self.tokens[self.pos][1] == 'PRINT':
                        self.match('PRINT')
                        val = self.printoutput()
                        if val == 'err':
                            return
                    elif self.tokens[self.pos][1] == 'INPUT':
                        self.match('INPUT')
                        val = self.getinput()
                        if val == 'err':
                            return
                    elif self.tokens[self.pos][0] == 'GTFO':
                        self.match('GTFO')
                        break
                    else:
                        self.pos += 1

            elif self.tokens[self.pos][0] == 'OIC':
                self.match('OIC')
                break
            else:
                self.errors.append(f"Syntax Error: Unexpected token in SWITCH, found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
                self.pos += 1

    def function(self):
        if not self.tokens[self.pos][0] == 'HOW IZ I':
            if not self.tokens[self.pos][0] == 'IF U SAY SO':
                if not self.tokens[self.pos][0] == 'I IZ':
                    self.errors.append(f"Syntax Error: Expected 'FUNCTION', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")        
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
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'IDENTIFIER']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0]
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)
                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            self.pos += 1
        else:
            self.errors.append(f"Syntax Error: Expected an expression, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")


    def typecast(self):
        var_name = self.tokens[self.pos][0] 
        variable = next((var for var in self.symbol_table if var[1] == var_name), None)

        if not variable:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            self.pos += 2
            return
        
        self.pos += 1

        if self.match('IS NOW A'):
            pass
        elif self.match('A'):
            pass
        else:
            self.errors.append(f"Syntax Error: Expected 'TYPECAST', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return

        new_type = self.tokens[self.pos][0]

        self.symbol_table = [(new_type, var_name, value) if name == var_name else (var_type, name, value)
                            for var_type, name, value in self.symbol_table]
    
        
    def reset(self):
        # self.code_text.delete(1.0, tk.END)
        self.lexical_analyze_button.config(state=tk.NORMAL)
        self.symbol_table.clear()
        self.tokens.clear()
        for item in self.lex_text.get_children():
            self.lex_text.delete(item)
        for item in self.syntax_text.get_children():
            self.syntax_text.delete(item)

#CREATE AND RUN THE APP
root = tk.Tk()
app = LOL(root)
root.mainloop()