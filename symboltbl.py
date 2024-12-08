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
        self.user_input_var = tk.StringVar()

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

        self.syntax_text = ttk.Treeview(self.syntax_frame, columns = ("output"), show = "headings", style="Treeview")
        self.syntax_text.heading("output", text="output")
        self.syntax_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.syntax_scrollbar = tk.Scrollbar(self.syntax_frame, orient=tk.VERTICAL, command=self.syntax_text.yview, background="grey")
        self.syntax_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.syntax_text.config(yscrollcommand=self.lex_scrollbar.set)

        #CONSOLE FRAME
        self.console_frame = tk.Frame(self.root, background="#1F1F1F")
        self.console_label = tk.Label(self.console_frame, text="CONSOLE",font=bold_font,fg='white',background='#1F1F1F')
        self.console_label.pack(side=tk.TOP)
        self.console_text = tk.Text(self.console_frame, wrap=tk.WORD, background='#292929', fg='white')
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #SYMBOL TABLE
        self.symbol_frame = tk.Frame(self.root, background="#1F1F1F")
        self.symbol_label = tk.Label(self.symbol_frame, text="SYMBOL TABLE",font=bold_font,fg='white',background='#1F1F1F')
        self.symbol_label.pack(side=tk.TOP)

        style = ttk.Style()
        style.configure("Treeview", background="#292929", fieldbackground="#292929", foreground="white")
        style.configure("Treeview.Heading", background="#292929", foreground="black")  

        style.map("Treeview", background=[("selected", "black")], foreground=[("selected","white")])

        self.symbol_text = ttk.Treeview(self.symbol_frame, columns = ("variable","type","value"), show = "headings", style="Treeview")
        self.symbol_text.heading("variable", text="variable")
        self.symbol_text.heading("type", text="type")
        self.symbol_text.heading("value", text="value")
        self.symbol_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.symbol_scrollbar = tk.Scrollbar(self.symbol_frame, orient=tk.VERTICAL, command=self.syntax_text.yview, background="grey")
        self.symbol_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.symbol_text.config(yscrollcommand=self.lex_scrollbar.set)

        #GRID
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 8)
        self.root.columnconfigure(2, weight = 16)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=40)
        self.root.rowconfigure(2, weight=40)
        self.root.rowconfigure(3, weight=40)
        self.root.rowconfigure(4, weight=60)

        self.title_frame.grid(row=0, column=0, columnspan=3,sticky='nswe')
        self.file_frame.grid(row=1,column=0, rowspan=3,sticky='nswe')
        self.code_frame.grid(row=1,column=1, rowspan=3,sticky='nswe')
        self.lex_frame.grid(row=1,column=2,sticky='nswe')
        self.syntax_frame.grid(row=2,column=2,sticky='nswe')
        self.symbol_frame.grid(row=3,column=2, sticky='nswe')
        self.console_frame.grid(row=4,column=0,columnspan=3, sticky='nswe')

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

        return token_arr

    def lexical(self):
        self.lexical_analyze_button.config(state=tk.DISABLED)
        code_content = self.code_text.get("1.0", tk.END).strip()
        if not code_content: 
            messagebox.showwarning("No Code", "Text editor is empty!")
            return

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

        for i in range (len(self.symbol_table)):
            self.symbol_text.insert("", "end", values=(self.symbol_table[i][1], self.symbol_table[i][0],self.symbol_table[i][2]))

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

            elif curr[1] == 'IDENTIFIER':
                self.match('IDENTIFIER')
                if self.tokens[self.pos][1] == 'ASSIGNMENT':
                    self.match('ASSIGNMENT')
                    self.pos -= 2
                    self.assignment()
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
        op = self.tokens[self.pos][0]
            
        if not self.match('COMPARISON'):
            self.errors.append(f"Syntax Error: Expected {'COMPARISON'}, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return
        
        if self.tokens[self.pos][1] == 'ARITHMETIC':

            val1 = self.arithmetic()
            self.match('AN')

            if self.tokens[self.pos][1] == 'ARITHMETIC':

                val2 = self.arithmetic()
            else:
                val2 = self.expression()

        elif self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'TROOF', 'YARN', 'IDENTIFIER']:
            val1 = self.expression()
            self.match('AN')
            if self.tokens[self.pos][1] == 'ARITHMETIC':
                
                val2 = self.arithmetic()
            else:
                val2 = self.expression()
        else:
            val1 = self.expression()
            self.match('AN')
            val2 = self.expression()

        if op == 'BOTH SAEM':

            if type(val1) == float:
                man =  float(val1) == float(val2)
                if man == True:
                    return 'WIN'
                else:
                    return 'FAIL'
            elif type(val2) == float:
                man = float(val1) == float(val2)
                if man == True:
                    return 'WIN'
                else:
                    return 'FAIL'
            else:
                man = int(val1) == int(val2)
                if man == True:
                    for var in self.symbol_table:
                        if(var[1] == 'IT'):
                            remove = (var[0],var[1],var[2])
                            self.symbol_table = [tup for tup in self.symbol_table if tup != remove]
                    self.symbol_table.append(('TROOF','IT','WIN'))
                    return 'WIN'
                else:
                    for var in self.symbol_table:
                        if(var[1] == 'IT'):
                            remove = (var[0],var[1],var[2])
                            self.symbol_table = [tup for tup in self.symbol_table if tup != remove]
                    self.symbol_table.append(('TROOF','IT','FAIL'))
                    return 'FAIL'
        else:
            if type(val1) == float:
                man = float(val1) != float(val2)
                if man == True:
                    return 'WIN'
                else:
                    return 'FAIL'
            elif type(val2) == float:
                man = float(val1) != float(val2)
                if man == True:
                    return 'WIN'
                else:
                    return 'FAIL'
            else:
                man = int(val1) != int(val2)
                if man == True:
                    for var in self.symbol_table:
                        if(var[1] == 'IT'):
                            remove = (var[0],var[1],var[2])
                            self.symbol_table = [tup for tup in self.symbol_table if tup != remove]
                    self.symbol_table.append(('TROOF','IT','WIN'))
                    return 'WIN'
                else:
                    for var in self.symbol_table:
                        if(var[1] == 'IT'):
                            remove = (var[0],var[1],var[2])
                            self.symbol_table = [tup for tup in self.symbol_table if tup != remove]
                    self.symbol_table.append(('TROOF','IT','FAIL'))
                    return 'FAIL'

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

        #FOR VALUE LITERAL
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            if(self.tokens[self.pos][1] == 'NUMBR'):
                var_value = int(self.tokens[self.pos][0])
            elif(self.tokens[self.pos][1] == 'NUMBAR'):
                var_value = float(self.tokens[self.pos][0])
            elif(self.tokens[self.pos][1] == 'TROOF'):
                if(self.tokens[self.pos][0] == 'WIN'):
                    var_value = True
                elif(self.tokens[self.pos][0] == 'FAIL'):
                    var_value = False
            else:            
                var_value = self.tokens[self.pos][0]
            self.pos += 1
        
        #FOR OPERATIONS
        elif self.tokens[self.pos][1]  == 'ARITHMETIC':
            var_value = self.arithmetic()

        self.symbol_table.append((var_type, var_name, var_value))

        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            self.pos += 1  
        
        print(f"Declared {var_name} of type {var_type}")

    def textinput(self, event=None):
        user_input = self.console_text.get(f"1.0 + {self.length} chars", tk.END).strip()    
        self.user_input_var.set(user_input)
        self.console_text.unbind("<Return>")

    def getinput(self):
        var_name = self.tokens[self.pos][0] 
        variable = next((var for var in self.symbol_table if var[1] == var_name), None)

        if not variable:
            self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
            return 'err'

        if self.tokens[self.pos][1] != 'IDENTIFIER':
            self.errors.append(f"Error: Expected 'IDENTIFIER', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return
        
        #EXECUTION
        self.pos+=1
        var_name = self.tokens[self.pos-1][0]

        #Check if the variable is already in the symbol table
        for var in self.symbol_table:
            if(var[1] == var_name):
                remove = (var[0],var[1],var[2])
                self.symbol_table = [tup for tup in self.symbol_table if tup != remove]

        initial_content = self.console_text.get("1.0", tk.END)
        self.length = len(initial_content) -1
        self.console_text.bind("<Return>", self.textinput)

        #Get user input
        self.console_text.wait_variable(self.user_input_var)
        text = self.user_input_var.get()

        #Replace with user input
        self.symbol_table.append(('IDENTIFIER', var_name, text))

    def printoutput(self):
        to_print = ""
        while self.pos < len(self.tokens):
            #FOR VALUE LITERAL
            if self.tokens[self.pos][1] in ['YARN', 'NUMBR', 'NUMBAR', 'TROOF', 'IDENTIFIER'] and self.tokens[self.pos][2] == self.tokens[self.pos-1][2]:
                if self.tokens[self.pos][1] == 'IDENTIFIER':
                    var_name = self.tokens[self.pos][0] 
                    variable = next((var for var in self.symbol_table if var[1] == var_name), None)

                    if not variable:
                        self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                        return 'err'
                    elif(variable[0] == 'NOOB'):
                        to_print = to_print + str(variable[0])  
                    else:
                        to_print = to_print + str(variable[2])
                else:
                    print("THIS IS DA WAE", self.tokens[self.pos][0])
                    to_print = to_print + str(self.tokens[self.pos][0].replace('"',''))
                self.pos+=1
            
            #FOR ARITHMETIC EXPRESSIONS
            elif self.tokens[self.pos][1] == 'ARITHMETIC':
                answer = self.arithmetic()
                to_print = to_print + str(answer)

            elif self.match('CONNECTOR'):
                continue
            
            elif self.match('CONCATENATION'):
                concat = self.expression()
                to_print = to_print + concat
            
            elif self.tokens[self.pos][1] == 'BOOLEAN':
                bools = self.boolean()
                if bools == True:
                    to_print = to_print + 'WIN'
                else:
                    to_print = to_print + 'FAIL'
            
            elif self.tokens[self.pos][1] == 'COMPARISON':
                comp = self.comparison()
                to_print = to_print + str(comp)
            else:
                break
        self.console_text.insert(tk.END,(to_print + "\n"))

    def boolean(self):
        
        operation = self.tokens[self.pos][0]
        self.pos += 1
        operands = []

        # Collect operands for boolean operation
        while self.tokens[self.pos][1] in ['IDENTIFIER', 'TROOF', 'NUMBR', 'NUMBAR', 'CONNECTOR', 'BOOLEAN']:
            print(f"Processing token: {self.tokens[self.pos]}")

            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0]
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)
                
                print("Variable:", variable)
                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                    return None
                
                # convert WIN or FAIL to true or false para akma sa python
                value = variable[2]  # 'WIN' or 'FAIL'
                operands.append(True if value == 'WIN' else False)
            
            elif self.tokens[self.pos][1] == 'TROOF':
                literal = self.tokens[self.pos][0]
                operands.append(True if literal == 'WIN' else False)
            
            elif self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR']:
                if self.tokens[self.pos][0] != None:
                    operands.append(True)
                else:
                    operands.append(False)
            
            elif self.tokens[self.pos][1] == 'BOOLEAN':
                operands.append(self.tokens[self.pos][0])
            
            elif self.tokens[self.pos][1] == 'CONNECTOR':
                pass  # Ignore AN
            
            self.pos += 1
        
        self.match('CONFIRMATION')
        
        print('OPERATION', operation, 'at line', self.tokens[self.pos-1][2])
        print('OPERANDS', operands)
        print('SPACE PEOPLE \n\n')
        # Perform the boolean operation
        if operation == 'BOTH OF':
            result = bool(operands[0]) and bool(operands[1])
        elif operation == 'EITHER OF':
            result = bool(operands[0]) or bool(operands[1])
        elif operation == 'WON OF':
            result = bool(operands[0]) != bool(operands[1])
        elif operation == 'NOT':
            result = not bool(operands[0])
        elif operation == 'ALL OF':
            result = all(bool(op) for op in operands)
        elif operation == 'ANY OF':
            result = any(bool(op) for op in operands)
        else:
            self.errors.append(f"Unknown boolean operation '{operation}' at line {self.tokens[self.pos][2]}")
            return None

        return result
  
  
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
            self.errors.append(f"Syntax Error: Expected asdas'YA RLY', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return
        self.pos-=1
        for var in self.symbol_table:
            if var[1] == 'IT':
                if var[2] == 'WIN':
                    print("NAGEXECUTE IF")
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

                    while(self.tokens[self.pos][0] != 'OIC'):
                        self.pos +=1
                    self.pos +=1
                    print("ETO SAYO",self.tokens[self.pos])
                    return
                else:
                    print("NAGEXECUTE ELSE")
                    while(self.pos < len(self.tokens) and self.tokens[self.pos][0] != 'NO WAI'):
                        self.pos +=1
                    if self.pos < len(self.tokens):
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
            

    def sum_of(self,a,b):
        return a+b
    def diff_of(self,a,b):
        return a-b
    def produkt_of(self,a,b):
        return a*b
    def quoshunt_of(self,a,b):
        return a/b
    def biggr_of(self,a,b):
        return (max(a,b))
    def smallr_of(self,a,b):
        return (min(a,b))
    def mod_of(self,a,b):
        return (a%b)
    
    def arithmetic(self):
        operators = {
            'SUM OF': self.sum_of,
            'DIFF OF': self.diff_of,
            'PRODUKT OF': self.produkt_of,
            'QUOSHUNT OF': self.quoshunt_of,
            'BIGGR OF': self.biggr_of,
            'SMALLR OF': self.smallr_of,
            'MOD OF': self.mod_of
        }
        operations = []
        answers = []
        while self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'IDENTIFIER', 'CONNECTOR', 'ARITHMETIC', 'YARN', 'TROOF']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0] 
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)
                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                    return            
            token_type = self.tokens[self.pos][1]
            token_value = self.tokens[self.pos][0]

            if token_type == 'ARITHMETIC':
                operations.append(token_value)
            elif token_type == 'IDENTIFIER':
                is_var = False
                for var in self.symbol_table:
                    if token_value == var[1]:
                        operations.append(float(var[2]))
                        is_var = True
                        break
                if not is_var:
                    self.errors.append(f"Semantic Error: Variable '{token_value}' is not declared at line {self.tokens[self.pos][2]}")
                    return
            elif token_type == 'NUMBR':
                operations.append(int(token_value))
            elif token_type == 'NUMBAR':
                operations.append(float(token_value))
            elif token_type == 'TROOF':
                if(token_value == 'WIN'):
                    operations.append(1)
                elif(token_value == 'FAIL'):
                    operations.append(0)
            elif token_type == 'YARN':
                cleaned_string = token_value.strip('"')
                operations.append(float(cleaned_string))
            elif token_type == 'CONNECTOR':
                if operations[-1] in ['SUM OF', 'DIFF OF','PRODUKT OF','QUOSHUNT OF','BIGGR OF','SMALLR OF','MOD OF'] or operations[-2] in ['SUM OF', 'DIFF OF','PRODUKT OF','QUOSHUNT OF','BIGGR OF','SMALLR OF','MOD OF']:
                    pass
                else:
                    if len(operations) > 3:
                        if operations[-3] in ['SUM OF', 'DIFF OF','PRODUKT OF','QUOSHUNT OF','BIGGR OF','SMALLR OF','MOD OF'] and operations[-4] in ['SUM OF', 'DIFF OF','PRODUKT OF','QUOSHUNT OF','BIGGR OF','SMALLR OF','MOD OF']:
                            pass
                        else:
                            break
                    else:
                        break
            else:
                break
            print("OPPSSSS",operations)
            print('\n\n')
            self.pos += 1

        for element in reversed(operations):

            if isinstance(element, (int, float)):
                answers.append(element)
            elif(len(answers) <= 1):
                self.errors.append(f"Semantic Error: Variable '{token_value}' invalid length of operator/operations {self.tokens[self.pos][2]}")
                return 
            else:
                operand1 = answers.pop()
                operand2 = answers.pop()
                result = operators[element](operand1, operand2)
                answers.append(result)
        return answers[0]

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

                    if self.tokens[self.pos][1] == 'TROOF':
                        self.symbol_table = [('TROOF', var_name, new_value) if name == var_name else (var_type, name, value)
                                    for var_type, name, value in self.symbol_table]
                    else:
                        self.symbol_table = [(var_type, var_name, new_value) if name == var_name else (var_type, name, value)
                                    for var_type, name, value in self.symbol_table]
                elif self.tokens[self.pos][1] == 'IDENTIFIER':
                    var_name = self.tokens[self.pos][0] 
                    variable = next((var for var in self.symbol_table if var[1] == var_name), None)

                    if not variable:
                        self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                        self.pos += 2
                        return
                    
                    self.symbol_table = [(variable[1], var_name, variable[2]) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]
                else:
                    new_value = int(self.tokens[self.pos][0])

                    self.symbol_table = [(var_type, var_name, new_value) if name == var_name else (var_type, name, value)
                                    for var_type, name, value in self.symbol_table]
                
                self.pos += 1
                
            elif self.tokens[self.pos][1] == 'TYPECAST':
                self.match('TYPECAST')
                self.typecast()
                self.pos += 1

            elif self.tokens[self.pos][1] == 'CONCATENATION':
                new_value = self.concatenation()

                self.symbol_table = [(var_type, var_name, new_value) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]

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
                            return val
                    elif self.tokens[self.pos][1] == 'INPUT':
                        self.match('INPUT')
                        val = self.getinput()
                        if val == 'err':
                            return val
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
        if self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'IDENTIFIER', 'TROOF']:
            if self.tokens[self.pos][1] == 'IDENTIFIER':
                var_name = self.tokens[self.pos][0]
                variable = next((var for var in self.symbol_table if var[1] == var_name), None)
                if not variable:
                    self.errors.append(f"Semantic Error: Variable '{var_name}' is not declared at line {self.tokens[self.pos][2]}")
                    return 'err'
                
                self.pos += 1
                return variable[2]
            elif self.tokens[self.pos][1] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
                new = self.tokens[self.pos][0]
                self.pos += 1
                return new
        
        else:
            self.errors.append(f"Syntax Error: Expected an expression, but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return 'err'


    def concatenation(self):
        if self.match('CONCATENATION'):

            val = str(self.expression())
            while self.tokens[self.pos][1] == 'CONNECTOR':
                self.match('AN')
                val = val + str(self.expression())

            return val
        else:
            self.errors.append(f"Syntax Error: Expected 'CONCATENATION', but found {self.tokens[self.pos][1]} at line {self.tokens[self.pos][2]}")
            return 'err'



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

        if new_type == 'NUMBR':
            self.symbol_table = [(new_type, var_name, int(value)) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]
        elif new_type == 'NUMBAR':
            self.symbol_table = [(new_type, var_name, float(value)) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]
        elif new_type == 'YARN':
            self.symbol_table = [(new_type, var_name, str(value)) if name == var_name else (var_type, name, value)
                                for var_type, name, value in self.symbol_table]
        elif new_type == 'TROOF':
            if variable[2] != None:
                self.symbol_table = [(new_type, var_name, 'WIN') if name == var_name else (var_type, name, value)
                                    for var_type, name, value in self.symbol_table]
            else:
                self.symbol_table = [(new_type, var_name, 'FAIL') if name == var_name else (var_type, name, value)
                                    for var_type, name, value in self.symbol_table]
    def reset(self):
        self.lexical_analyze_button.config(state=tk.NORMAL)
        self.symbol_table.clear()
        self.tokens.clear()
        self.console_text.delete("1.0",tk.END)
        for item in self.lex_text.get_children():
            self.lex_text.delete(item)
        for item in self.syntax_text.get_children():
            self.syntax_text.delete(item)
        for item in self.symbol_text.get_children():
            self.symbol_text.delete(item)

#CREATE AND RUN THE APP
root = tk.Tk()
app = LOL(root)
root.mainloop()