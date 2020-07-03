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
import syntax_tree.calculate as translate
import syntax_tree.execute as execute
class branch(node):
    # node id
    __id = ''

    # code generated
    __code = ''

    # last reference
    __ref = ''

    # used for goto
    __start_label_up_to = 0

    # _value, _type and _counter inherits from node class
    def __init__(self):
        self._value = {}
        self._counter = 0

    def add(self, value):
        self._value[self._counter] = value
        self._counter += 1

    def setType(self, typ):
        self._type = node.TYPE[typ]
        self.__id = typ

    def setValue(self, id):
        self.__id = id

    def getValue(self):
        return self.__id

    def getSize(self):
        return len(self._value)

    def getType(self):
        return self._type

    def getChild(self, index):
        if index < len(self._value) and index >= 0:
            return self._value[index]
        return None

    def append3D(self, threeD):
        self.__code += threeD

    def clear3D(self):
        self.__code = ''

    def gen3D(self, res, e1, op=None, e2=None):
        if res == 'label':
            self.__code += str(e1) + ' :'
        elif res == 'print':
            self.__code += 'print(\"' + str(e1) + '\");'
        elif res == 'declare':
            self.__code += str(e1) + ' = ' + str(op) + ' ;'
        elif res == 'goto':
            self.__code += 'goto ' + str(e1) + ' ;'
        elif res == 'if':
            self.__code += 'if (' + str(e1) + ') goto ' + str(op) + ';'
        else:
            self.__code += str(res) + ' = ' + str(e1) + ' ' + str(op) + ' ' + str(e2) + ' ;'
        self.__code += '\n'

    def get3D(self):
        return self.__code

    def setRef(self, temp):
        self.__ref = temp

    def getRef(self):
        return self.__ref

    def start_execute(self, sym_table, start_from):
        self.__start_label_up_to = 0
        for label in range(self.getSize()):
            label_node = self.getChild(label)
            if label_node.getValue() == start_from:
                break
            else:
                self.__start_label_up_to += 1

        return self.execute(sym_table)

    switch={
            # MATH
            node.TYPE["ADD"] : translate.ADD,
            node.TYPE["SUB"] : translate.SUB,
            node.TYPE["MUL"] : translate.MUL,
            node.TYPE["DIV"] : translate.DIV,
            node.TYPE["MOD"] : translate.MOD,

            # BITWISE
            node.TYPE["BAND"]   : translate.BAND,
            node.TYPE["BOR"]    : translate.BOR,
            node.TYPE["BXOR"]   : translate.BXOR,
            node.TYPE["SLEFT"]  : translate.SLEFT,
            node.TYPE["SRIGHT"] : translate.SRIGHT,

            node.TYPE["BNOT"]   : translate.BNOT,

            # LOGIC
            node.TYPE["AND"]   : translate.AND,
            node.TYPE["OR"]    : translate.OR,
            node.TYPE["XOR"]   : translate.XOR,

            node.TYPE["NOT"]   : translate.NOT,

            # CONVERT
            node.TYPE["TOINT"]  : translate.TOINT,
            node.TYPE["TOFLOAT"]: translate.TOFLOAT,
            node.TYPE["TOCHAR"] : translate.TOCHAR,

            # FUNCTION
            node.TYPE["FUNCTION"] : translate.FUNCTION,
            node.TYPE["CALL"]   : translate.CALL,
            node.TYPE["GOTO"]   : translate.GOTO,
            node.TYPE["LABEL"]  : translate.LABEL,
            node.TYPE["RETURN"] : translate.RETURN,
            node.TYPE["POINT"] : translate.POINT,

            # CONTROL
            node.TYPE["IF"]  : translate.IF,
            node.TYPE["EQUAL"]  : translate.EQUAL,
            node.TYPE["NOEQUAL"]  : translate.NOEQUAL,
            node.TYPE["GTHAN"]  : translate.GTHAN,
            node.TYPE["GE_OP"]  : translate.GE_OP,
            node.TYPE["LTHAN"]  : translate.LTHAN,
            node.TYPE["LE_OP"]  : translate.LE_OP,

            # STRUCTS
            node.TYPE["ARRAY"]  : translate.ARRAY,
            node.TYPE["ACCESS"]  : translate.ACCESS,
            node.TYPE["STRUCT"]  : translate.STRUCT,

            node.TYPE["VARRAY"]  : translate.VARRAY,

            # LOOPS
            node.TYPE["FOR"]  : translate.FOR,
            node.TYPE["DO"]  : translate.DO,
            node.TYPE["WHILE"]  : translate.WHILE,

            node.TYPE["ASSIGN"] : translate.ASSIGN,
            node.TYPE["PRINT"]  : translate.PRINT,
            node.TYPE["DECLARE"] : translate.DECLARE,
            node.TYPE["SCOPE"] : translate.SCOPE
            }

    switchExecutor={
            # MATH
            node.TYPE["ADD"] : execute.ADD,
            node.TYPE["SUB"] : execute.SUB,
            node.TYPE["MUL"] : execute.MUL,
            node.TYPE["DIV"] : execute.DIV,
            node.TYPE["MOD"] : execute.MOD,

            node.TYPE["ABS"] : execute.ABS,
            # LOGIC
            node.TYPE["AND"] : execute.AND,
            node.TYPE["OR"]  : execute.OR,
            node.TYPE["XOR"] : execute.XOR,

            node.TYPE["NOT"] : execute.NOT,
            # COMPARE
            node.TYPE["EQUAL"]  : execute.EQUAL,
            node.TYPE["NOEQUAL"]: execute.NOEQUAL,
            node.TYPE["GTHAN"]  : execute.GTHAN,
            node.TYPE["GE_OP"]  : execute.GE_OP,
            node.TYPE["LTHAN"]  : execute.LTHAN,
            node.TYPE["LE_OP"]  : execute.LE_OP,
            # BITWISE
            node.TYPE["BAND"]   : execute.BAND,
            node.TYPE["BOR"]    : execute.BOR,
            node.TYPE["BXOR"]   : execute.BXOR,
            node.TYPE["SLEFT"]  : execute.SLEFT,
            node.TYPE["SRIGHT"] : execute.SRIGHT,

            node.TYPE["BNOT"]   : execute.BNOT,
            # STRUCT
            node.TYPE["ACCESS"] : execute.ACCESS,

            # CONVERT
            node.TYPE["TOINT"]  : execute.TOINT,
            node.TYPE["TOFLOAT"]: execute.TOFLOAT,
            node.TYPE["TOCHAR"] : execute.TOCHAR,
            
            node.TYPE["READ"]  : execute.READ,
            node.TYPE["POINT"]  : execute.POINT,
            node.TYPE["UNSET"]  : execute.UNSET,
            node.TYPE["PRINT"]  : execute.PRINT,
            node.TYPE["ASSIGN"] : execute.ASSIGN
            }

    def execute(self, sym_table):
        # 0 mode for translate 1 for execute
        if sym_table.getMode():
            # executing intermediate code
            return self.execute3D(sym_table)
        else:
            # generating intermediate code
            func = self.switch.get(self.getType(),lambda :'Node not defined')
            result = func(self, sym_table)
            if result != None:
                return result

    def execute3D(self, sym_table):
        #TODO need to return semantic errors
        has_print = False
        goto_label = ''
        for label in range(self.__start_label_up_to, len(self._value), 1):
            label_node = self._value[label]
            if label_node.getType() == self.TYPE["LABEL"]:
                for child in range(label_node.getSize()):
                    child_node = label_node.getChild(child)
                    if child_node.getType() == self.TYPE["EXIT"]:
                        if has_print:
                            return [sym_table.getLog(), None]
                        return [None, None]
                    elif child_node.getType() == self.TYPE["IF"]:
                        boolean = execute.TOVALUE(child_node.getChild(0).execute(sym_table), sym_table)
                        if boolean != None:
                            if boolean == 1:
                                # need to finish the execution
                                # and return a value for restart execution for other point
                                goto_label = child_node.getChild(1).getValue()
                                if has_print:
                                    return [sym_table.getLog(), goto_label]
                                return [None, goto_label]
                    elif child_node.getType() != self.TYPE["GOTO"]:
                        func=self.switchExecutor.get(child_node.getType(),lambda :'Node not defined')
                        result = func(child_node, sym_table)
                        if child_node.getType() == self.TYPE["PRINT"]:
                            has_print = True
                    else:
                        # need to finish the execution
                        # and return a value for restart execution for other point
                        goto_label = child_node.getChild(0).getValue()
                        if has_print:
                            return [sym_table.getLog(), goto_label]
                        return [None, goto_label]
            else:
                func=self.switchExecutor.get(self.getType(),lambda :'Node not defined')
                return func(self, sym_table)
        if self.getType() == self.TYPE["READ"]:
            func=self.switchExecutor.get(self.getType(),lambda :'Node not defined')
            return func(self, sym_table)
        if has_print:
            return [sym_table.getLog(), None]
        return [None,None]