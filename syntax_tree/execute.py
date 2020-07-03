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
from syntax_tree.leaf import leaf
import tkinter as tk
from tkinter import Label, StringVar, Tk
def ADD(node, sym_table):
    return MATH('+', node, sym_table)

def SUB(node, sym_table):
    return MATH('-', node, sym_table)

def MUL(node, sym_table):
    return MATH('*', node, sym_table)

def DIV(node, sym_table):
    return MATH('/', node, sym_table)

def MOD(node, sym_table):
    return MATH('%', node, sym_table)

def AND(node, sym_table):
    return LOGIC('*', node, sym_table)

def OR(node, sym_table):
    result = LOGIC('+', node, sym_table)
    if result == 2:
        return 1
    else:
        return result

def EQUAL(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() == exp2.getValue():
        return 1
    return 0

def NOEQUAL(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() != exp2.getValue():
        return 1
    return 0

def GTHAN(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() > exp2.getValue():
        return 1
    return 0

def GE_OP(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() >= exp2.getValue():
        return 1
    return 0

def LTHAN(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() < exp2.getValue():
        return 1
    return 0

def LE_OP(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp.getValue() <= exp2.getValue():
        return 1
    return 0

def BAND(node, sym_table):
    return BITWISE('&', node, sym_table)

def BOR(node, sym_table):
    return BITWISE('|', node, sym_table)

def BXOR(node, sym_table):
    return BITWISE('^', node, sym_table)

def SLEFT(node, sym_table):
    return BITWISE('<<', node, sym_table)

def SRIGHT(node, sym_table):
    return BITWISE('>>', node, sym_table)

def PRINT(node, sym_table):
    exp = node.getChild(0)
    if exp.getType() == exp.TYPE["ACCESS"]:
        exp = TOVALUE(exp.execute(sym_table), sym_table)
    else:
        try:
            exp = sym_table.get(exp.getValue())
            if exp != None:
                exp = exp.getValue()
                if type(exp) == leaf:
                    exp = exp.execute(sym_table).getValue()
            else:
                if node.getChild(0).getType() == leaf.TYPE["STRING"]:
                    exp = node.getChild(0).getValue()
                    exp = exp.replace('\\n', '\n')
                    exp = exp.replace('\\t', '\t')
                else:
                    exp = node.getChild(0).getValue()
        except:
            pass
    if exp != None:
        sym_table.appendLog(exp)
        return "No value to print"
    return None

def ACCESS(node, sym_table):
    exp = node.getChild(0)
    if exp.getType() == exp.TYPE["ID"]:
        exp = exp.execute(sym_table)
        # now we have sym instance
        if exp:
            exp2 = TOVALUE(node.getChild(1), sym_table)
            exp.setRef(str(exp2.getValue()))
            return exp
        # error
        return None
    else:
        exp = exp.execute(sym_table)
        if exp:
            new_index = exp.getRef()
            exp2 = TOVALUE(node.getChild(1), sym_table)
            exp.setRef(str(new_index) + ',' + str(exp2.getValue()))
            return exp
        # error
        return None

def UNSET(node, sym_table):
    label = node.getChild(0)
    if label.getType() == label.TYPE["ACCESS"]:
        label = label.execute(sym_table)
        if label:
            index = label.getRef()
            array = label.getValue()
            array.pop(index)
            label.setValue(array)
    else:
        sym_table.remove(label.getValue())
    return None

def XOR(node, sym_table):
    return LOGIC('^', node, sym_table)

def POINT(node, sym_table):
    return node.getChild(0)

def TOINT(node, sym_table):
    return leaf(CONVERT('int', node, sym_table), "NUM")

def TOFLOAT(node, sym_table):
    return leaf(CONVERT('float', node, sym_table), "FLOAT")

def TOCHAR(node, sym_table):
    return leaf(CONVERT('char', node, sym_table), "STRING")

def READ(node, sym_table):
    # lookup the last line
    index = sym_table.terminal.search(r'\n', "insert", backwards=True, regexp=True)
    txt = sym_table.terminal.get(str(index),'end-1c')
    if txt == "":
        index ="1.0"
    index = sym_table.terminal.index("%s+1c" % index)

    # print before start waiting
    sym_table.terminal.insert(str(float(index)+1), sym_table.getLog())
    sym_table.cleanLog()
    sym_table.terminal.focus_set()

    # wait input from terminal
    x = Label()
    x.wait_variable(sym_table.read_input)
    value = sym_table.read_input.get()
    typ = ''
    try:
        try:
            value = int(value)
            typ = 'NUM'
        except:
            value = float(value)
            typ = 'FLOAT'
    except:
        typ = 'STRING'
    
    return leaf(value, typ)

def CONVERT(op, node, sym_table):
    exp = node.getChild(0)
    if exp.getType() == leaf.TYPE["ACCESS"]:
        exp = exp.execute(sym_table)
        identifier = exp.getID()
        exp = sym_table.get(identifier)
        array = exp.getValue()
        index = list(array.keys())
        exp = array[index[0]]
    else:
        exp = TOVALUE(exp, sym_table)

    value = exp.getValue()
    if value != None:
        if exp.getType() == leaf.TYPE["STRING"]:
            if op == 'char':
                return value[0]
            else:
                return OPERAND(op, OPERAND('string', value[0], None), None)
        else:
            if op == 'char':
                if value > 255 :
                    # apply mod of 255 and convert to ASCII
                    value = value % 255
                return chr(int(value))
            else:
                return OPERAND(op, value, None)
    else:
        # error handling
        return None

def MATH(op, node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp == None or exp2 == None:
            exp = None
    elif exp.getType() == node.TYPE["STRING"] and exp2.getType() == node.TYPE["STRING"] :
        if op == '+':
            exp = str(exp.getValue()) + str(exp2.getValue())
        else:
            # error handling
            exp = "Error at <" + str(exp.getValue()) + "> " + op + " <" + str(exp2.getValue()) + ">"
            sym_table.appendLog(exp)
            exp = None
    elif (exp.getType() == node.TYPE["NUM"] and exp2.getType() == node.TYPE["NUM"]):
        exp = OPERAND(op, int(exp.getValue()), int(exp2.getValue()))
        if type(exp) == str:
            sym_table.appendLog(exp)
            exp = None
    elif (exp.getType() == node.TYPE["NUM"] or exp.getType() == node.TYPE["FLOAT"]) and (exp2.getType() == node.TYPE["NUM"] or exp2.getType() == node.TYPE["FLOAT"]):
        exp = OPERAND(op, float(exp.getValue()), float(exp2.getValue()))
        if type(exp) == str:
            sym_table.appendLog(exp)
            exp = None
    else:
        # error handling
        exp = "Error at <" + str(exp.getValue()) + "> " + op + " <" + str(exp2.getValue()) + ">"
        sym_table.appendLog(exp)
        exp = None
    return exp

def LOGIC(op, node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if (exp.getValue() != 0 and exp.getValue() != 1) and (exp2.getValue() != 0 and exp2.getValue() != 1):
        # error handling
        exp = "Error at <" + str(exp.getValue()) + "> " + op + " <" + str(exp2.getValue()) + ">"
        sym_table.appendLog(exp)
        exp = None
    else:
        exp = OPERAND(op, int(exp.getValue()), int(exp2.getValue()))     
    return exp

def BITWISE(op, node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    exp2 = TOVALUE(node.getChild(1), sym_table)

    if exp == None or exp2 == None:
        return None
    elif (exp.getType() == node.TYPE["NUM"] and exp2.getType() == node.TYPE["NUM"]):
        exp = OPERAND(op, int(exp.getValue()), int(exp2.getValue()))
        if type(exp) == str:
            sym_table.appendLog(exp)
            exp = None
        return exp
    else:
        # error
        return None

def ABS(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)
    if exp.getType() == node.TYPE["NUM"]:
        value = int(exp.getValue())
        if value < 0: 
            return OPERAND('*',value, -1)
        return value
    elif exp.getType() == node.TYPE["FLOAT"]:
        value = float(exp.getValue())
        if value < 0: 
            return OPERAND('*',value, -1)
        return value
    else:
        # error handling
        return None

def NOT(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)

    if exp.getValue() != 0 and exp.getValue() != 1:
        # error handling
        exp = "Error at ! <" + str(exp.getValue()) + ">"
        sym_table.appendLog(exp)
        exp = None
    else:
        exp = OPERAND('!', int(exp.getValue()), None)
        if exp:
            exp = 1
        else:
            exp = 0     
    return exp

def BNOT(node, sym_table):
    exp = TOVALUE(node.getChild(0), sym_table)

    if exp.getType() == node.TYPE["NUM"]:
        exp = OPERAND('~', int(exp.getValue()), None)
        if type(exp) == str:
            sym_table.appendLog(exp)
            exp = None
        return exp
    else:
        # error
        return None

def OPERAND(op, val, val2):
    if op == '+':
        return val + val2
    elif op == '-':
        return val - val2
    elif op == '*':
        return val * val2
    elif op == '/':
        if val2 != 0:
            return val / val2
        else:
            return "Can't divide by zero"
    elif op == '%':
        if val2 != 0:
            return val % val2
        else:
            return "Can't divide by zero"
    # only for LOGIC
    elif op == '^':
        return val ^ val2
    # only for BITWISE
    elif op == '&':
        return val & val2
    elif op == '|':
        return val | val2
    elif op == '<<':
        return val << val2
    elif op == '>>':
        return val >> val2
    # only for UNARYOP
    elif op == '!':
        return not val
    elif op == '~':
        return ~val
    # only for CONVERT
    elif op == 'int':
        return int(val)
    elif op == 'float':
        return float(val)
    elif op == 'string':
        return ord(val)
    else:
        return "No recognized operand" + str(op)

def ASSIGN(node, sym_table):
    exp = node.getChild(0)
    TYPE = exp.TYPE
    if exp.getType() == TYPE["ACCESS"]:
        exp = exp.execute(sym_table)
    exp2 = node.getChild(1)
    if exp2.getType() == TYPE["ARRAY"]:
        exp2 = {}
    else:
        exp2 = exp2.execute(sym_table)
        try:
            if exp2.getType() == TYPE["STRUCT"]:
                identifier = exp2.getID()
                exp2 = sym_table.get(identifier)
                index = exp2.getRef()
                array = exp2.getValue()
                exp2 = array[index]
            if exp2.getType() != TYPE["ID"]:
                result = exp2.getValue()
                exp2 = result
        except:
            pass

    if exp.getType() == TYPE["ID"]:
        identifier = exp.getValue()
        exp = sym_table.get(identifier)
        exp.setValue(exp2) 
        exp.setType(TYPEOF(exp2))
    else:
        # array
        identifier = exp.getID()
        exp = sym_table.get(identifier)
        index = exp.getRef()
        array = exp.getValue()
        array[index] = exp2
        exp.setValue(array)

    sym_table.update(identifier, exp)
    return None

def TYPEOF(value):
    if type(value) == int:
        return "NUM"
    elif type(value) == float:
        return "FLOAT" 
    elif type(value) == str:
        return "STRING"
    elif type(value) == dict:
        return "STRUCT"
    else:
        try:
            value.getRef()
            return "STRUCT"
        except:
            return "ID"

def TOVALUE(value, sym_table):
    try:
        if value.getType() == leaf.TYPE["ID"]:
            return value.execute(sym_table)
        elif value.getType() == leaf.TYPE["ACCESS"]:
            result = value.execute(sym_table)
            index = result.getRef()
            array = result.getValue()
            value = array[index]
            return leaf(array[index], TYPEOF(value))
        elif type(value) == sym:
            if value.getType() == leaf.TYPE["STRUCT"]:
                index = value.getRef()
                array = value.getValue()
                return array[index]
            return value.getValue()
        elif value.getType() > 5:
            value = value.execute(sym_table)
            value = leaf(value, TYPEOF(value))
        return value
    except:
        # its the value itself 
        return value