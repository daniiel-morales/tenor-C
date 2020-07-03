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

def SCOPE(node, sym_table):
    for index in range(node.getSize()):
        child =  node.getChild(index)
        child.execute(sym_table)
        #TODO ADD exp to SYM_TABLE semantic errors
        if child.getType() == node.TYPE["DECLARE"] and node.root == True:
            sym_table.global_code += child.get3D()
        else:
            node.append3D(child.get3D())
            # print all exit flags
            if child.getType() == node.TYPE["IF"]:
                label_list = child.getValue().split(',')
                for label in label_list:
                    node.gen3D('label', label)
    return node

def CALL(node, sym_table):
    # get function instance
    if node.getType() == node.TYPE["FUNCTION"]:
        function = sym_table.get(node.getChild(1).getValue())
    else:
        function = sym_table.get(node.getChild(0).getValue())

    if function != None:
        # extracts sub-tree saved on instance
        func_node = function.getFunction()

        # clear if its not first time calling this function
        if func_node.get3D() != '':
            func_node.clear3D()
            node.clear3D()
            function.setRef(sym_table.getLabel())

        # create function scope
        sym_table.addScope()

        # add global vars if main CALL
        if function.getID().lower() == 'main':
            # add Label function
            node.gen3D('label', function.getRef())
            node.append3D(sym_table.global_code) 
            #node.gen3D('declare', '$ra', 0)

        # create parameters in the new scope
        for index in range(function.getSize()):
            args_block = func_node.getChild(3).getChild(index)
            # just change empty ref for indicate DECLARE node this is parameter
            args_block.setRef('p')
            args_block.execute(sym_table)

            node.append3D(args_block.get3D())

            # return to last scope without eliminate this new scope
            last_scope = sym_table.getScope()

            sym_table.setScope(last_scope-1)

            # set value for new parameters in scope
            value_block = node.getChild(1).getChild(index)
            value = value_block.execute(sym_table)

            node.append3D(value_block.get3D())

            node.gen3D('declare', args_block.getRef(), value.getRef())

            # return to the actual scope
            sym_table.setScope(last_scope)

        if function.getID().lower() != 'main':
            # add Label function
            node.gen3D('label', function.getRef())

        # start execute inside function
        scope_block = func_node.getChild(2)
        for index in range(scope_block.getSize()):
            statement = scope_block.getChild(index)

            # TODO make an especific method for create new parameters and goto the same function ref
            #if statement.getType() == node.TYPE["CALL"]:
                # verify it is a recursive call
                #if statement.getChild(0).getValue() == node.getChild(0).getValue():
 
            statement.clear3D()
            statement.execute(sym_table)

            node.append3D(statement.get3D())
            # print all exit flags
            if statement.getType() == node.TYPE["IF"]:
                label_list = statement.getValue().split(',')
                for label in label_list:
                    if 'L' in label:
                        node.gen3D('label', label)

        # return function scope
        sym_table.removeScope()
        #node.gen3D('$ra', '$ra', '-', 1)

        # update function instance for no reprocess
        if func_node.get3D() == '':
            func_node.append3D(node.get3D())

    else:
        #TODO report no function found
        pass

def FUNCTION(node, sym_table):
    # return type
    typ = node.getChild(0).getType()
    # function name
    name = node.getChild(1).getValue()

    func_size = 0
    if node.getSize() > 3:
        # has parameters
        func_size = node.getChild(3).getSize()

    # verify to execute
    if name.lower() == 'main':
        sym_table.add(name, typ, func_size, 'FUNCTION', 'main')
        func = sym_table.get(name)
        func.setFunction(node)

        CALL(node, sym_table)

        #TODO make return node TYPE value for finish execution

    else:
        func_ref = sym_table.getLabel()
        sym_table.add(name, typ, func_size, 'FUNCTION', func_ref)
        func = sym_table.get(name)
        func.setFunction(node)

def RETURN(node, sym_table):
    if node.getSize() > 0:
        # get return node value
        return_value = node.getChild(0)
        if return_value.getType() == node.TYPE["CALL"]:
            return return_value
        node.append3D(return_value.get3D())
        node.setRef(return_value.getRef())
    # return scope
    node.gen3D('$ra', '$ra', ' - ', 1)
    sym_table.removeScope()

def GOTO(node, sym_table):
    return JMP('goto', node.getChild(0).getValue(), node, sym_table)

def LABEL(node, sym_table):
    return JMP('label', node.getChild(0).getValue(), node, sym_table)

def JMP(op, label, node, sym_table):
    # verify label ref
    exists = sym_table.get(label)

    if exists == None:
        # create label ref
        sym_table.add(label, 'LABEL', 0, 'LABEL', sym_table.getLabel())
        exists = sym_table.get(label)

    node.gen3D(op, exists.getRef())
   
    return node

def PRINT(node, sym_table):
    if node.getSize() > 1:
        # print with expressions
        string_to_print =  node.getChild(0).getValue()

        c = 0
        while '%' in string_to_print:
            index = string_to_print.find('%')
            temp = string_to_print[:index]

            node.gen3D('print', temp)

            str_value = node.getChild(1).getChild(c).execute(sym_table)
            c = c + 1
            node.append3D(str_value.get3D())
            node.append3D('print(' + str(str_value.getRef()) +');\n')

            string_to_print = string_to_print[index+2:]

        node.gen3D('print', string_to_print)

    else:
        # only print a message
        node.gen3D('print', node.getChild(0).getValue())
    return node

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

def MATH(op, node, sym_table):
    e1 = node.getChild(0).execute(sym_table)
    e2 = node.getChild(1).execute(sym_table)

    # append generated code
    node.append3D(e1.get3D())
    node.append3D(e2.get3D())

    # add new generated Line
    temp_ref = sym_table.getTemp()
    node.gen3D(temp_ref, e1.getRef(), op , e2.getRef())

    # save ref temp
    node.setRef(temp_ref)

    # add TYPE to node for future TYPE check
    primitive = ["INT", "FLOAT", "STRING"]
    if e1.getType() > e2.getType():
        try:
            node.setType(primitive[e1.getType() - 1])
        except:
            node.setType("INT")
    else:
        try:
            node.setType(primitive[e2.getType() - 1])
        except:
            node.setType("INT")

    return node

def IF(node, sym_table):
    # boolean argument
    arg = node.getChild(0).execute(sym_table)

    # append arg code
    node.append3D(arg.get3D())

    # verify its boolean_op or just NUM value
    if 'L' not in arg.getRef():
        # new true label
        true_label = sym_table.getLabel()

        node.gen3D('if', arg.getRef(), true_label)

        # new false label
        false_label = sym_table.getLabel()

        node.gen3D('goto', false_label)

        # update ref label true and false
        arg.setValue(true_label)
        arg.setRef(false_label)

    # true list 
    node.gen3D('label', arg.getValue())
    
    correct_statement = node.getChild(1).execute(sym_table)
    node.append3D(correct_statement.get3D())
    exit_ref = sym_table.getLabel()

    # goto exit flag
    node.gen3D('goto', exit_ref)

    # false list
    if ',' in arg.getRef():
        label_list = arg.getRef().split(',')
        for label in label_list:
            node.gen3D('label', label)
    else:
        node.gen3D('label', arg.getRef())

    # verify if it has elif or else
    if node.getSize() > 2:
        for elif_index in range(2, node.getSize(), 1):
            elseif = node.getChild(elif_index)
            if elseif.getType() == node.TYPE["ELSE"]:
                arg = elseif.getChild(0).execute(sym_table)
            else:
                arg = elseif.execute(sym_table)

            # append arg code
            node.append3D(arg.get3D())
            exit_ref += "," + arg.getValue()
    
    # append exit flag
    node.setValue(exit_ref)

    return node

def EQUAL(node, sym_table):
    return MATH(' == ', node, sym_table)

def NOEQUAL(node, sym_table):
    return MATH(' != ', node, sym_table)

def GTHAN(node, sym_table):
    return MATH(' > ', node, sym_table)

def GE_OP(node, sym_table):
    return MATH(' >= ', node, sym_table)

def LTHAN(node, sym_table):
    return MATH(' < ', node, sym_table)

def LE_OP(node, sym_table):
    return MATH(' <= ', node, sym_table)

def LOGIC(op, node, sym_table):
    e1 = node.getChild(0).execute(sym_table)
    e2 = node.getChild(1).execute(sym_table)

    true_ref = sym_table.getLabel()
    false_ref = sym_table.getLabel()

    # append code for first argument value
    node.append3D(e1.get3D())

    # append code for second argument value
    node.append3D(e2.get3D())

    bool_arg = str(e1.getRef()) + op +  str(e2.getRef())
    node.gen3D('if', bool_arg, true_ref)
    node.gen3D('goto', false_ref)

    node.setValue(true_ref)
    node.setRef(false_ref)
    return node

# BITWISE translate like MATH

def BAND(node, sym_table):
    return MATH('&', node, sym_table)

def BOR(node, sym_table):
    return MATH('|', node, sym_table)

def BXOR(node, sym_table):
    return MATH('^', node, sym_table)

def SLEFT(node, sym_table):
    return MATH('<<', node, sym_table)

def SRIGHT(node, sym_table):
    return MATH('>>', node, sym_table)

#################################


# LOGIC 

def AND(node, sym_table):
    return MATH('&&', node, sym_table)

def OR(node, sym_table):
    return MATH('||', node, sym_table)

def XOR(node, sym_table):
    return MATH('xor', node, sym_table)

def BACKPATCH(op, node, sym_table):
    e1 = node.getChild(0).execute(sym_table)
    e2 = node.getChild(1).execute(sym_table)

    # append generated code
    node.append3D(e1.get3D())

    # decide by op how to manage true and false labels
    if op == '&&':
        # print TRUE list of first argument
        node.gen3D('label', e1.getValue())
        
        # now TRUE list is from sencond argument
        node.setValue(e2.getValue())

        # append FALSE list of second argument
        node.setRef(e1.getRef() + ',' + e2.getRef())

    elif op == '||':
        # print FALSE list of first argument
        node.gen3D('label', e1.getRef())
        
        # append TRUE list of second argument
        node.setValue(e1.getValue() + ',' + e2.getValue())

        # now FALSE list of second argument
        node.setRef(e2.getRef())
    else:
        # print TRUE list of first argument
        node.gen3D('label', e1.getValue())

        # now TRUE list is FALSE list from sencond argument
        node.setValue(e2.getRef())
        
        # now FALSE list is TRUE list from sencond argument
        node.setRef(e2.getValue())

    node.append3D(e2.get3D())

    return node

#################################

# UNARY operator

def BNOT(node, sym_table):
    e = node.getChild(0).execute(sym_table)

    node.append3D(e.get3D())
    ref = sym_table.getTemp()
    node.gen3D('declare', ref, '~' + str(e.getRef()))

    node.setRef(ref)

    return node

def NOT(node, sym_table):
    e = node.getChild(0).execute(sym_table)

    node.append3D(e.get3D())
    ref = sym_table.getTemp()
    node.gen3D('declare', ref, '!' + str(e.getRef()))

    node.setRef(ref)

    return node 

def POINT(node, sym_table):
    e = node.getChild(0).execute(sym_table)

    node.append3D(e.get3D())
    ref = sym_table.getTemp()
    node.gen3D('declare', ref, '&' + str(e.getRef()))

    node.setRef(ref)

    return node 

################################

# TODO merge with DECLARE
def ASSIGN(node, sym_table):
    e1 = node.getChild(0).execute(sym_table)
    e2 = node.getChild(1).execute(sym_table)

    if e1 != None:
        node.append3D(e1.get3D())

        node.append3D(e2.get3D())

        node.gen3D('declare', e1.getRef(), e2.getRef())
    else:
        # error no variable
        pass

####################################

def ARRAY(node, sym_table):
    typ = node.getChild(0).getType()
    for index in range(1, node.getSize(), 1):
        e = node.getChild(index)
        ref = sym_table.getTemp()
        node.setRef(ref)
        e.setRef(ref)
        node.gen3D('declare', ref,'array()')
        sym_table.add(e.getValue(), typ, 0, 'ID',ref)

    return node

def ACCESS(node, sym_table):
    e = node.getChild(0).execute(sym_table)
    pos = ''
    for index in range(1, node.getSize(), 1):
        attrib = node.getChild(index)
        if attrib.getType() != node.TYPE["STRING"]:
            attrib = node.getChild(index).execute(sym_table)
        pos = pos + '[' + str(attrib.getRef()) + ']'

    node.setRef(str(e.getRef()) + pos)
    return node

def STRUCT(node, sym_table):
    name = node.getChild(0).getValue()
    attribs = node.getChild(1).getSize()

    sym_table.add(name, 'STRUCT', attribs, 'STRUCT', 'GLOBAL')

    node.clear3D()
    node.setRef('')
    node.setValue('')

    return node

#################

# LOOPS

def FOR(node, sym_table):
    init = node.getChild(0)
    init.execute(sym_table)
    node.append3D(init.get3D())

    # FOR loop label
    for_label = sym_table.getLabel()
    node.gen3D('label', for_label)

    condition = node.getChild(1)
    condition.execute(sym_table)
    node.append3D(condition.get3D())

    true_list = sym_table.getLabel()
    false_list = sym_table.getLabel()
    node.gen3D('if', condition.getRef(), true_list)
    node.gen3D('goto', false_list)

    node.gen3D('label', true_list)

    if node.getSize()>2:
        execute_scope = node.getChild(3)
        execute_scope.execute(sym_table)
        node.append3D(execute_scope.get3D())
    
    counter = node.getChild(2)
    counter.execute(sym_table)
    node.append3D(counter.get3D())

    # generate loop
    node.gen3D('goto', for_label)

    # exit label
    node.gen3D('label', false_list)

    return node


#################

def TOINT(node, sym_table):
    return CONVERT('int', node, sym_table)

def TOFLOAT(node, sym_table):
    return CONVERT('float', node, sym_table)

def TOCHAR(node, sym_table):
    return CONVERT('char', node, sym_table)

def CONVERT(op, node, sym_table):
    value = node.getChild(0).execute(sym_table)
   
    node.append3D(value.get3D())
   
    ref = sym_table.getTemp()

    node.gen3D('declare', ref, '(' + op + ') ' + value.getRef())

    node.setRef(ref)
    return node

def DECLARE(node, sym_table):
    typ = node.getChild(0).getType()
    for index in range(1, node.getSize(), 1):
        e = node.getChild(index)
        # verify it has init value
        if e.getType() == node.TYPE['ASSIGN']:
            e1 = e.getChild(0) 
            e2 = e.getChild(1).execute(sym_table)

            # add value code
            value_code_gen = e2.get3D()
            node.append3D(value_code_gen)
            if e1.getType() == node.TYPE['ID']:
                #if typ >= e2.getType() or e2.getType() == node.TYPE['READ']:
                    # generate code only when value is a leaf
                    if value_code_gen == '':
                        value_ref = sym_table.getTemp()
                        node.gen3D('declare', value_ref, e2.getRef())
                        e2.setRef(value_ref)
                        node.setRef(value_ref)

                    # add assign value ref to the id ref
                    sym_table.add(e1.getValue(), typ, 0, 'ID', e2.getRef())
                    node.setRef(e2.getRef())
            else:
                #TODO create reference to array
                pass
        else:
            if node.getRef() == '':
                ref = sym_table.getTemp()
            else:
                ref = sym_table.getParameter()
            node.setRef(ref)
            e.setRef(ref)
            node.gen3D('declare', ref, 0)
            sym_table.add(e.getValue(), typ, 0, 'ID',ref)
