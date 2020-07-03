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
from sym_table.sym import sym
from tkinter import StringVar
class table:
    __table = None
    __log = None
    __scope = None
    __grammar = None
    __temp_count = None
    __label_count = None
    __parameter_count = None
    error = ''
    read_input = None
    terminal = None
    global_code = ''

    __mode = None

    def __init__(self):
        self.__table = {0: {}}
        self.__log = ''
        self.__scope = 0
        self.__grammar = {}
        self.__temp_count = 0
        self.__label_count = 0
        self.__parameter_count = 0
        self.__mode = 0
        self.read_input = StringVar ()

    def add(self, identifier, typ, size, role, ref):
        if self.__mode:
            if self.get(identifier) == None:
                # value for instance in __table diccionary
                ins = sym(identifier, typ, size, role, ref, typ)
                
                # adds the instance in the table
                self.__table[identifier] = ins
                return True
            return False
        else:
            # value for instance in __table[scope] diccionary
            ins = sym(identifier, typ, size, role, 'GLOBAL', ref)
            ins_id = ins.getID()

            # check if not exists in local scope to add it
            if ins_id not in self.__table[self.__scope]:
                self.__table[self.__scope][ins_id] = ins
                return True

            return False
        
    def update(self, ins_id, ins):
        if self.__mode:
            # check if exists
            if self.get(ins_id) != None:
                # updates the instance in the table
                self.__table[ins_id] = ins
                return True
            return False
        else:
            # check if exists in global scope
            if ins_id in self.__table[0]:
                self.__table[self.__scope][0] = ins
                return True

            # check if exists in local scope
            if ins_id in self.__table[self.__scope]:
                self.__table[self.__scope][ins_id] = ins
                return True

            return False

    def remove(self, identifier):
        if identifier:
            try:
                self.__table.pop(identifier)
                return True
            except:
                return False
        return False

    def get(self, ins_id):
        if self.__mode :
            # returns sym class
            try:
                return self.__table[ins_id]
            except:
                return None   
        else:

            # check if exists in local scope and returns sym class
            if ins_id in self.__table[self.__scope]:
                return self.__table[self.__scope][ins_id]

            # check if exists in global scope and returns sym class
            if ins_id in self.__table[0]:
                return self.__table[0][ins_id]

            return None

    # scope for execute
    def setScope(self, scope):
        self.__scope = scope

    def getScope(self):
        return self.__scope
    #####################
    
    # scope for translate
    def addScope(self):
        self.__scope += 1
        self.__table[self.__scope] = {}

    def removeScope(self):
        if self.__scope > 0:
            self.__table.pop(self.__scope)
            self.__scope -= 1
    ######################

    def appendLog(self, txt):
        self.__log += str(txt)

    def cleanLog(self):
        self.__log = ''

    def appendGrammar(self, index, txt):
        try:
            self.__grammar[index]
        except:
            self.__grammar[index] = txt

    def getGrammar(self):
        return self.__grammar

    def getLog(self):
        return self.__log

    def printTable(self):
        return self.__table

    def setTable(self, table):
        self.__table = table

    def getTemp(self):
        new_ref = "$t" + str(self.__temp_count)
        self.__temp_count += 1 
        return new_ref

    def getLabel(self):
        new_ref = "L" + str(self.__label_count)
        self.__label_count += 1 
        return new_ref

    def getParameter(self):
        new_ref = "$a" + str(self.__parameter_count)
        self.__parameter_count += 1 
        return new_ref

    def setMode(self, mode):
        # verify range mode is permitted
        if mode<2 and mode >-1:
            self.__mode = mode

    def getMode(self):
        return self.__mode