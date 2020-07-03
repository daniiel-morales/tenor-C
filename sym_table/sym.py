#▓█████▄  ▄▄▄       ███▄    █ ▒██░ ██░ ███▄ ▄███░ ▒█████   ██▀███  
#▒██▀ ██▌▒████▄     ██ ▀█   █ ▒██▒▒██▒▓██▒▀█▀ ██▒▒██▒  ██▒▓██ ▒ ██▒
#░██   █▌▒██  ▀█▄  ▓██  ▀█ ██▒▒██▒▒██▒▓██    ▓██░▒██░  ██▒▓██ ░▄█ ▒
#░▓█▄   ▌░██▄▄▄▄██ ▓██▒  ▐▌██▒░██░░██░▒██    ▒██ ▒██   ██░▒██▀▀█▄  
#░▒████▓  ▓█   ▓██▒▒██░   ▓██░░██░░██░▒██▒   ░██▒░ ████▓▒░░██▓ ▒██▒
# ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░▓  ░▓  ░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░
# ░ ▒  ▒   ▒   ▒▒ ░░ ░░   ░ ▒░ ▒ ░ ▒ ░░  ░      ░  ░ ▒ ▒░   ░▒ ░ ▒░
# ░ ░  ░   ░   ▒      ░   ░ ░  ▒ ░ ▒ ░░      ░   ░ ░ ░ ▒    ░░   ░ 
#   ░          ░  ░         ░  ░   ░         ░       ░ ░     ░     
# pylint: disable=W,import-error
from syntax_tree.node import node

class sym:
    __id = ''
    __type = 0
    __size = 0
    __role = None
    __scope = ''
    __ref = 0
    __function_node = None
    
    def __init__(self, identifier, typ, size, role, scope, ref):
        self.__id = identifier
        self.__type = typ
        self.__size = size
        self.__role = role
        self.__scope = scope
        self.__ref = ref

        
    def setID(self, identifier):
        self.__id = identifier

    def setType(self, typ):
        self.__type = node.TYPE[typ]

    def setSize(self, size):
        self.__size = size

    def setValue(self, role):
        self.__role = role

    def setScope(self, value):
        self.__value = value

    def setRef(self, ref):
        self.__ref = ref

    def setFunction(self, node):
        self.__function_node = node

    def getID(self):
        return self.__id

    def getType(self):
        return self.__type

    def getSize(self):
        return self.__size
    
    def getValue(self):
        return self.__role
	
    def getScope(self):
        return self.__scope

    def getRef(self):
        return self.__ref

    def getFunction(self):
        return self.__function_node
