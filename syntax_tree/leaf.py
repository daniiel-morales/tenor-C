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

class leaf(node):
    # _value and _type inherits from node class
    def __init__(self, value, typ):
        self._value = value
        self._type = node.TYPE[typ]
        self._ref = value

    def setValue(self, value):
        self._value = value

    def setType(self, typ):
        self._type = node.TYPE[typ]

    def getValue(self):
        return self._value

    def getType(self):
        return self._type

    def getChild(self, index):
        return None

    def gen3D(self, res, e1, op, e2):
        return None

    def get3D(self):
        return ''

    def setRef(self, temp):
        self._ref = temp

    def getRef(self):
        if self._type == self.TYPE["STRING"] and '$' not in str(self._ref):
            self._ref  = "\"" + self._ref + "\""
        return self._ref

    def execute(self, sym_table):
        # 0 mode for translate 1 for execute
        if sym_table.getMode():
            # for execute
            if self._type == node.TYPE["ID"]:
                return sym_table.get(self._value)
            return self._value
        else:
            # for translate
            if self._type == self.TYPE["ID"]:
                ins = sym_table.get(self._value)
                if ins != None:
                    self._ref = ins.getRef()
                    self._type = ins.getType()
            return self
        