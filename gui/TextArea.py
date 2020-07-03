#▓█████▄  ▄▄▄       ███▄    █ ▒██░ ██░ ███▄ ▄███░ ▒█████   ██▀███  
#▒██▀ ██▌▒████▄     ██ ▀█   █ ▒██▒▒██▒▓██▒▀█▀ ██▒▒██▒  ██▒▓██ ▒ ██▒
#░██   █▌▒██  ▀█▄  ▓██  ▀█ ██▒▒██▒▒██▒▓██    ▓██░▒██░  ██▒▓██ ░▄█ ▒
#░▓█▄   ▌░██▄▄▄▄██ ▓██▒  ▐▌██▒░██░░██░▒██    ▒██ ▒██   ██░▒██▀▀█▄  
#░▒████▓  ▓█   ▓██▒▒██░   ▓██░░██░░██░▒██▒   ░██▒░ ████▓▒░░██▓ ▒██▒
# ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░▓  ░▓  ░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░
# ░ ▒  ▒   ▒   ▒▒ ░░ ░░   ░ ▒░ ▒ ░ ▒ ░░  ░      ░  ░ ▒ ▒░   ░▒ ░ ▒░
# ░ ░  ░   ░   ▒      ░   ░ ░  ▒ ░ ▒ ░░      ░   ░ ░ ░ ▒    ░░   ░ 
#   ░          ░  ░         ░  ░   ░         ░       ░ ░     ░     
# pylint: disable=import-error                                                
from tkinter import Frame, Text, Scrollbar, Label
import tkinter.font as tkFont
import re
from gui.edit import TextLineNumbers, CustomText
class TextArea(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        # setting self.textarea
        self.textarea = CustomText(self)
        self.textarea["wrap"] = "none"
        self.textarea["background"] = "white"
        self.textarea["borderwidth"] = 0
        self.textarea["highlightthickness"] = 0
        self.textarea["height"] = 5

        textarea_scroll_x = Scrollbar(self)
        textarea_scroll_x["orient"] = "horizontal"
        textarea_scroll_x["borderwidth"] = 1
        textarea_scroll_x["command"] = self.textarea.xview
        textarea_scroll_x.pack(in_=self,side="bottom", fill="x", expand=False)

        textarea_scroll_y = Scrollbar(self)
        textarea_scroll_y["orient"] = "vertical"
        textarea_scroll_y["borderwidth"] = 1
        textarea_scroll_y["command"] = self.textarea.yview
        textarea_scroll_y.pack(in_=self,side="right", fill="y", expand=False)

        self.textarea.configure(xscrollcommand=textarea_scroll_x.set)
        self.textarea.configure(yscrollcommand=textarea_scroll_y.set)

        self.linenumbers = TextLineNumbers(self, width=20, bg = "lightgray")
        self.linenumbers.attach(self.textarea)
        self.linenumbers.pack(side="left", fill="y")

        self.cursor_info = Label(self.textarea, text='Line: 1 | Column: 1')
        self.cursor_info.pack(expand='no', fill=None, side='right', anchor='se')

        self.textarea.bind("<<Change>>", self._on_change)
        self.textarea.bind("<Configure>", self._on_change)

        self.textarea.pack(in_=self, side="left", fill="both", expand=True)
        # binding with the keyboard press
        self.textarea.bind("<space>", self.highlighting)
        self.textarea.bind("<Return>", self.highlighting)

        # Control+V
        self.textarea.bind("<Control_L>v", self.analyze_pasted_text)
        self.textarea.bind("<Control_L>V", self.analyze_pasted_text)

        bold_font = tkFont.Font(self.textarea, self.textarea.cget("font"))
        bold_font.configure(weight="bold")
        # setting the reserved words
        self._words=["if", "else", "goto", "print", "unset", "read();"]
        
        self.textarea.tag_configure("reserved_word", foreground="#8f288c")          #violet
        self.textarea.tag_configure("variable", foreground="#5bc0de")               #sky-blue
        self.textarea.tag_configure("comment", foreground="#5cb85c")                #green-mint
        self.textarea.tag_configure("value", foreground="#428bca", font=bold_font)  #light-blue BOLDED

        self.toggle_string = 1
        self.toggle_comment = 1

    def update_cursor_info_bar(self, event=None):
        row, col = self.textarea.index('insert').split('.')
        line_num, col_num = str(int(row)), str(int(col) + 1)  # col starts at 0
        infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
        self.cursor_info.config(text=infotext)

    def _on_change(self, event):
        self.update_cursor_info_bar()
        self.linenumbers.redraw()
    
    def analyze_pasted_text(self,event):
        # TODO for each word pasted send it to highlight method
        print("pasted")

    def highlighting(self, event):
        # lookup the last whitespace
        index = self.textarea.search(r'\s', "insert", backwards=True, regexp=True)
        
        # verify it is the first word
        word = self.textarea.get(str(index), "insert")
        if word == "":
            index ="1.0"
        else:
            index = self.textarea.index("%s+1c" % index)

        # lookup the word itself
        word = self.textarea.get(index, "insert")

        # define patterns
        is_variable = re.search(r'\A[$][tavrsTAVRS]', word)
        is_comment = re.search(r'\A[#]', word)
        is_value = re.search(r'(-|[+])?[0-9]+([.][0-9]+)?', word)
        is_string = re.search(r'\b["]|["]\b|["]', word)

        # check the pattern to apply tag
        if is_string != None:
            self.textarea.tag_add("value", index, "%s+%dc" % (index, len(word)))
            self.toggle_string *= -1
        elif is_comment != None:
            self.textarea.tag_add("comment", index, "%s+%dc" % (index, len(word)))
            self.toggle_comment = -1
        elif self.toggle_string < 0:
            self.textarea.tag_add("value", index, "%s+%dc" % (index, len(word)))
        elif self.toggle_comment < 0:
            self.textarea.tag_add("comment", index, "%s+%dc" % (index, len(word)))
        elif word in self._words:
            self.textarea.tag_add("reserved_word", index, "%s+%dc" % (index, len(word)))
        elif is_variable != None:
            self.textarea.tag_add("variable", index, "%s+%dc" % (index, len(word)))
        elif is_value != None and len(is_value.string) == len(is_value.group()):
            self.textarea.tag_add("value", index, "%s+%dc" % (index, len(word)))
        else:
            self.textarea.tag_remove("reserved_word", index, "%s+%dc" % (index, len(word)))
            self.textarea.tag_remove("variable", index, "%s+%dc" % (index, len(word)))
            self.textarea.tag_remove("comment", index, "%s+%dc" % (index, len(word)))
            self.textarea.tag_remove("value", index, "%s+%dc" % (index, len(word)))
        
        # verify if pressed Return
        if event.keycode == 13:
            self.toggle_comment = 1
