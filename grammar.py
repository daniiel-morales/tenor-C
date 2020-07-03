# pylint: disable=W,import-error
import ply.lex as lex
import ply.yacc as yacc
from syntax_tree.branch import branch as branch
from syntax_tree.leaf import leaf as leaf
'''
s : code

code : code block
	| block


block : function
    |  struct
    |  declaration

function: type ID '(' argument_list  '{' compound_stament

type : INT
    | CHAR
    | DOUBLE
    | FLOAT

argument_list : arguments ')'
            | ')'

arguments : arguments ',' arg 
        | arg
    
arg : type ID
    | type '&' ID
   
struct : STRUCT ID '{' assigment_list '}' ';'

assigment_list : assigment_list declaration ';'
            | declaration ';'
    
compound_stament : statement_list '}'
                | '}'

statement_list : statement_list statement
        | statement

statement : selection_statement
        | iteration_statement
        | declaration ';'
        | function_call ';'
        | jump_statement ';'

selection_statement : labeled_statement DEFAULT ':' statement_list "}"
                    | selection_if_has_more ELSE "{" compound_statement
                    | selection_if_has_more 

selection_if_has_more : selection_if ELSE selection_if
                    |  selection_if

selection_if : IF "(" expression ")" "{" compound_statement

labeled_statement : labeled_statement CASE expression ':' statement_list 
                | selection_switch  

selection_switch : SWITCH "(" expression ")" "{"

iteration_statement : WHILE '(' expression ')' '{' compound_statement
                    | DO OCUR compound_statement WHILE '(' bool_expression ')' ';'
                    | FOR '(' declaration ';' expression ';' unary_expr ')' '{' compound_statement


jump_statement : CONTINUE
                | BREAK
                | RETURN expression
                | RETURN

declaration : type declaration_list 
			 | unary_expr

declaration_list : declaration_list ',' sub_decl
		    | sub_decl

sub_decl : ID "=" expression
        | ID
    
assign_op : '='
        | '+' '='
        | '-' '='
        | '*' '='
        | '/' '='
        | '%' '='
        | '<' '<' '='
        | '>' '>' '='
        | '&' '='
        | '^' '='
        | '|' '='

unary_expr : '+' '+' is_array_term
        | '-' '-' is_array_term
        | is_array_term '+' '+' 
        | is_array_term '-' '-' 

is_array_term : is_array_term '[' term ']'
        | is_array_term '.' ID
	  	| ID

expression : expression '+' expression
        | expression '-' expression
        | expression '*' expression
        | expression '/' expression
        | expression '%' expression
        | expression '<' expression
        | expression '>' expression
        | expression '&' expression 
        | expression '|' expression
        | expression '^' expression
        | expression XOR expression

expression : '(' INT ')' expression
        | '(' FLOAT ')' expression
        | '(' CHAR ')' expression
        | '(' ID ')' expression
        | '(' expression ')'
        | '~' term	 			  	 				
        | '!' expression
        | '-' expression
        | expression '?' expression ':' expression
        | ID '(' parentheses_expression
        | term 
        | assigment_exp

expression : expression '=' '=' expression
        | expression '!' '=' expression
        | expression '&' '&' expression
        | expression '|' '|' expression
        | expression '<' '=' expression
        | expression '>' '=' expression
        | expression '<' '<' expression
        | expression '>' '>' expression

term : STRING
    | NUMBER
    | NUMBER '.' NUMBER
    | is_array_term

'''


def parse():
    # tokenizing rules
    reserved = {
                'if'    : 'IF',
                'else'  : 'ELSE',
                'printf': 'PRINT',
                'switch': 'SWITCH',
                'goto'  : 'GOTO',
                'xor'   : 'XOR',
                #'sizeof': 'SIZE',
                'for'   : 'FOR',
                'case'  : 'CASE',
                'int'   : 'INT',
                'double': 'DOUBLE',
                'float' : 'FLOAT',
                'char'  : 'CHAR',
                'return': 'RETURN',
                'do'    : 'DO',
                'while' : 'WHILE',
                'struct': 'STRUCT',
                'break' : 'BREAK',
                'continue':'CONTINUE',
                'default': 'DEFAULT',
                'void'  : 'VOID',
                'scanf' : 'READ'
                }

    tokens = [
                'ID',
                'NUMBER',
                'STRING'
            ] + list(reserved.values())

    literals = ['=', '\'', '"', '+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '!', '~', '(', ')', '[', ']', '{', '}', ';', ':', '.', ',', '?'] 

    t_ignore = " \t"

    t_ignore_COMMENT = r'[/] ( [/].* | [*].*[*][/] )'

    def t_STRING(t):
        r'( \"([^\\\n]|(\\.))*?\"  | \'([^\\\n]|(\\.))*?\' )'
        t.value = str(t.value).replace("\"","")
        t.value = str(t.value).replace("\'","")
        return t

    def t_NUMBER(t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(t):
        r'[a-zA-Z][a-zA-Z_0-9]*'
        global sym_table
        # check if reserved word
        if t.value in reserved:
            t.type = reserved.get(t.value)
        #else:
            # add ID to symbol table
            #sym_table.add(str(t.value), 'ID', 0, None, 'GLOBAL')
            #sym_table.setScope(str(t.value))
        return t

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(t):
        global sym_table
        global __text
        sym_table.error += "Lexical error <" + str(t.value[0]) + "> at line:" + str(t.lineno) + ", column:" + str(find_column(__text, t)) + "\n"
        t.lexer.skip(1)

    def find_column(input, token):
        line_start = input.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    # build the lexer
    lexer = lex.lex()

    # parsing rules

    precedence = (
        ('left', ','),
        ('left', 'ASSIGN'),
        ('left', '?'),
        ('left', 'XOR'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', '|'),
        ('left', '^'),
        ('left', '&'),
        ('left', '='),
        ('left', '<', '>', 'GREATEREQ', 'LESSEQ'),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('right', 'UMINUS', '~', 'POINT', 'PRE', 'CAST', 'NOT_PRE'),
        ('left', 'POST', '(', ')')
    )

    def p_start(p):
        's : code'
        global sym_table
        sym_table.appendGrammar(0, 's -> code')
        
        p[1].root = True
        p[0] = p[1]
        print('good job')

    def p_code(p):
        '''code : code block
	            | block '''
        global sym_table
        if len(p) > 2:
            p[1].add(p[2])
            p[0] = p[1]
        else:
            newbranch = branch()
            newbranch.add(p[1])
            newbranch.setType("SCOPE")
            newbranch.setValue("S")

            p[0] = newbranch
        
    def p_block(p):
        '''block : function
                |  struct
                |  declaration ";" '''
        p[0] = p[1]


    def p_function(p):
        '''function : type ID "(" argument_list  "{" compound_statement
                    | VOID ID "(" argument_list  "{" compound_statement'''
        new_branch = branch()
        new_branch.setType("FUNCTION")
        # add type
        new_branch.add(leaf(p[1], p[1].upper()))
        # add ID
        new_branch.add(leaf(p[2], "ID"))
        # add new scope
        new_branch.add(p[6])
        # if has add arguments
        if p[4] != None:
            new_branch.add(p[4])
        
        p[0] = new_branch

    def p_type(p):
        '''type : INT
                | CHAR
                | DOUBLE
                | FLOAT'''
        p[0] = str(p[1]).upper()

    def p_argument_list(p):
        '''argument_list : arguments ")"
                        | ")" '''
        new_branch = None
        if len(p) > 2:
            new_branch = p[1]

        p[0] = new_branch

    def p_arguments(p):
        '''arguments : arguments "," arg 
                    | arg '''
        new_branch = None
        if len(p) > 2 :
            new_branch = p[1]
            new_branch.add(p[3])
        else:
            new_branch = branch()
            new_branch.setType("SCOPE")
            new_branch.setValue("ARGUMENTS")
            new_branch.add(p[1])

        p[0] = new_branch

    def p_arg(p):
        ''' arg : type ID
                | type "&" ID '''

        new_branch = branch()
        new_branch.add(leaf(p[1], p[1]))
        if len(p) == 3:
            new_branch.add(leaf(p[2], "ID"))
        else:
            new_branch.add(leaf(p[3], "ID"))
            new_branch.add(leaf("&", "POINT"))
        
        new_branch.setType("DECLARE")
        p[0] = new_branch

    def p_struct(p):
        'struct : STRUCT ID "{" assigment_list "}" ";" '
        new_branch = branch()
        new_branch.setType("STRUCT")

        new_branch.add(leaf(p[2], "ID"))
        new_branch.add(p[4])
        p[0] = new_branch

    def p_assigment_list(p):
        ''' assigment_list : assigment_list declaration ";"
                        | declaration ";" '''
        new_branch = None
        if len(p) > 3 :
            new_branch = p[1]
            new_branch.add(p[2])
        else:
            new_branch = branch()
            new_branch.setType("SCOPE")
            new_branch.setValue("ATTRIBS")
            new_branch.add(p[1])

        p[0] = new_branch

    def p_compound_stament(p):
        '''compound_statement : statement_list "}"
                            | "}" '''
        new_branch = None
        if len(p) > 2:
            new_branch = p[1]
        else:
            new_branch = branch()
            new_branch.setType("SCOPE")
            new_branch.setValue("S")

        p[0] = new_branch

    def p_statement_list(p):
        ''' statement_list : statement_list statement
                        | statement '''
        new_branch = None
        if len(p) > 2 :
            new_branch = p[1]
            new_branch.add(p[2])
        else:
            new_branch = branch()
            new_branch.setType("SCOPE")
            new_branch.setValue("S")
            new_branch.add(p[1])

        p[0] = new_branch

    def p_statement(p):
        ''' statement : selection_statement
                    | iteration_statement
                    | native_statement
                    | unary_expr ";"
                    | declaration ";"
                    | assigment ";"
                    | function_call ";"
                    | jump_statement ";" ''' 
        p[0] = p[1]

    def p_assigment(p):
        'assigment : is_array_term assign_op expression %prec ASSIGN'
        new_branch = branch()
        new_branch.add(p[1])

        if p[2] != '=':
            assign_branch = branch()
            assign_branch.add(p[1])
            assign_branch.add(p[3])
            assign_branch.setType(p[2])

            new_branch.add(assign_branch)
        else:
            new_branch.setType("ASSIGN")
            new_branch.add(p[3])

        p[0] = new_branch

    def p_selection_stament(p):
        '''selection_statement : labeled_statement DEFAULT ':' statement_list "}"
                                | selection_if_has_more ELSE "{" compound_statement
                                | selection_if_has_more '''
        if len(p) > 5:
            pass
        elif len(p) > 2:
            else_branch = branch()
            else_branch.setType("ELSE")
            else_branch.add(p[4])
            p[1].add(else_branch)
        
        p[0] = p[1]

    def p_selection_if_has_more(p):
        '''selection_if_has_more : selection_if_has_more ELSE selection_if
                        |  selection_if'''
        if len(p) > 2:
            p[1].add(p[3])

        p[0] = p[1]

    def p_selection_if(p):
        'selection_if : IF "(" expression ")" "{" compound_statement'
        new_branch = branch()
        new_branch.setType("IF")

        new_branch.add(p[3])
        new_branch.add(p[6])

        p[0] = new_branch

    def p_labeled_statement(p):
        '''labeled_statement : labeled_statement CASE expression ':' statement_list 
                            | selection_switch  '''
        pass

    def p_selection_switch(p):
        'selection_switch : SWITCH "(" expression ")" "{"'
        pass

    def p_iteration_statement(p):
        '''iteration_statement : WHILE "(" expression ")" "{" compound_statement
                                | DO "{" compound_statement WHILE "(" expression ")" ";"
                                | FOR "(" declaration ";" expression ";" unary_expr ")" "{" compound_statement
                                | FOR "(" sub_decl ";" expression ";" unary_expr ")" "{" compound_statement '''
        pass

    def p_jump_stament(p):
        '''jump_statement : CONTINUE
                        | BREAK
                        | RETURN expression
                        | RETURN '''
        new_branch = branch()
        if len(p) > 2:
            new_branch.add(p[2])
        new_branch.setType(p[1].upper())

        p[0] = new_branch        

    def p_declaration_statement(p):
        '''declaration : declaration "," sub_decl
		            | type sub_decl '''
        if len(p) == 3:
            new_branch = branch()
            new_branch.add(leaf(p[1],p[1]))
            new_branch.add(p[2])
            new_branch.setType("DECLARE")
            p[0] = new_branch
        else:
            new_branch = p[1]
            new_branch.add(p[3])
            p[0] = new_branch

    def p_sub_decl(p):
        '''sub_decl : ID "=" expression
                    | ID "=" READ "(" ")"
                    | decl_array "=" "{" expression_list "}"
                    | decl_index "=" "{" expression_list "}"
                    | decl_index "=" expression
                    | decl_index "=" READ "(" ")"
                    | decl_index
                    | ID '''
        global sym_table
        new_branch = branch()
        if len(p) == 4:
            if type(p[1]) == branch:
                #TODO assign to index of array
                pass
            else:
                l_leaf = leaf(p[1], "ID")
                r_leaf = p[3]

                new_branch.add(l_leaf)
                new_branch.add(r_leaf)
                new_branch.setType("ASSIGN")

                sym_table.appendGrammar(5, 'statement -> is_array_term = expression')
        elif len(p) > 3:
            if p[4] == '(':
                l_leaf = leaf(p[1], "ID")
                r_leaf = leaf("read()", "READ")

                new_branch.add(l_leaf)
                new_branch.add(r_leaf)
                new_branch.setType("ASSIGN")
            else:
                #TODO assign array values
                pass
        else:
            if type(p[1]) == branch:
                #TODO assign to index of array
                pass
            else:
                new_branch = leaf(p[1], "ID")

        p[0] = new_branch

    def p_decl_index(p):
        '''decl_index : decl_index "[" term "]"
                    | ID "[" term "]" '''
        pass

    def p_decl_array(p):
        '''decl_array : decl_array "[" "]"
                    | ID "[" "]" '''
        pass

    def p_assing_op(p):
        '''assign_op : "="
                    | "+" "="
                    | "-" "="
                    | "*" "="
                    | "/" "="
                    | "%" "="
                    | "<" "<" "="
                    | ">" ">" "="
                    | "&" "="
                    | "^" "="
                    | "|" "=" '''

        if p[1] == "=":
            p[0] = "="
        elif p[1] == "+":
            p[0] = "ADD"
        elif p[1] == "-":
            p[0] = "SUB"
        elif p[1] == "*":
            p[0] = "MUL"
        elif p[1] == "/":
            p[0] = "DIV"
        elif p[1] == "%":
            p[0] = "MOD"
        elif p[1] == "<":
            p[0] = "SLEFT"
        elif p[1] == ">":
            p[0] = "SRIGHT"
        elif p[1] == "&":
            p[0] = "AND"
        elif p[1] == "^":
            p[0] = "XOR"
        elif p[1] == "|":
            p[0] = "OR"

    def p_unary_exp(p):
        '''unary_expr : "+" "+" is_array_term %prec PRE
                    | "-" "-" is_array_term %prec PRE
                    | is_array_term "+" "+" %prec POST
                    | is_array_term "-" "-" %prec POST '''
        l_leaf = p[1]
        r_leaf = leaf("1", "INT")
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)
        if p[1] == '+':
            new_branch.setType("ADD")
            sym_table.appendGrammar(12, 'unary_expr -> ++ is_array_term')
        elif p[1] == '-':
            new_branch.setType("SUB")
            sym_table.appendGrammar(12, 'unary_expr -> -- is_array_term')
        # TODO create an special node type that indicates ADD and SUB will occur in the next block
        elif p[2] == '+':
            new_branch.setType("ADD")
            sym_table.appendGrammar(12, 'unary_expr -> is_array_term ++')
        elif p[2] == '-':
            new_branch.setType("SUB")
            sym_table.appendGrammar(12, 'unary_expr -> is_array_term --')

    def p_is_array_term(p):
        '''is_array_term : is_array_term '[' expression ']'
                        | is_array_term '.' ID
                        | ID '''
        if len(p) > 4:
            pass
        elif len(p) > 2:
            pass
        else:
            p[0] = leaf(p[1], "ID")

    def p_native_statement(p):
        '''native_statement : PRINT "(" STRING "," expression_list ")" ";"
                            | PRINT "(" STRING ")" ";"
                            | GOTO ID ";"
                            | ID ":"  '''
        new_branch = branch()
        if len(p) > 6:
            new_branch.setType("PRINT")
            new_branch.add(leaf(p[3], "STRING"))
            p[5].setType("SCOPE")
            p[5].setValue("EXPS")
            new_branch.add(p[5])
        elif len(p) > 4:
            new_branch.setType("PRINT")
            new_branch.add(leaf(p[3], "STRING"))
        elif len(p) > 3:
            new_branch.setType("GOTO")
            new_branch.add(leaf(p[2], "ID"))
        else:
            new_branch.setType("LABEL")
            new_branch.add(leaf(p[1], "ID"))

        p[0] = new_branch

    def p_expression_binop(p):
        '''expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression
                      | expression '&' expression
                      | expression '|' expression
                      | expression '^' expression
                      | expression '<' expression
                      | expression '>' expression
                      | expression XOR expression
                      '''
        l_leaf = p[1]
        r_leaf = p[3]
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)

        if p[2] == '+':
            new_branch.setType("ADD")
            sym_table.appendGrammar(11, 'expression -> expression + expression')
        elif p[2] == '-':
            new_branch.setType("SUB")
            sym_table.appendGrammar(12, 'expression -> expression - expression')
        elif p[2] == '*':
            new_branch.setType("MUL")
            sym_table.appendGrammar(13, 'expression -> expression * expression')
        elif p[2] == '/':
            new_branch.setType("DIV")
            sym_table.appendGrammar(14, 'expression -> expression / expression')
        elif p[2] == '%':
            new_branch.setType("MOD")
            sym_table.appendGrammar(15, 'expression -> expression %, expression')
        elif p[2] == '&':
            new_branch.setType("BAND")
            sym_table.appendGrammar(16, 'expression -> expression & expression')
        elif p[2] == '|':
            new_branch.setType("BOR")
            sym_table.appendGrammar(17, 'expression -> expression | expression')
        elif p[2] == '^':
            new_branch.setType("BXOR")
            sym_table.appendGrammar(18, 'expression -> expression ^ expression')
        elif p[2] == '<':
            new_branch.setType("LTHAN")
            sym_table.appendGrammar(19, 'expression -> expression < expression')
        elif p[2] == '>':
            new_branch.setType("GTHAN")
            sym_table.appendGrammar(20, 'expression -> expression > expression')
        else:
            new_branch.setType("XOR")
            sym_table.appendGrammar(21, 'expression -> expression XOR expression')
        p[0] = new_branch

    def p_expression_binop2(p):
        '''expression : expression '&' '&' expression %prec AND
                      | expression '|' '|' expression %prec OR
                      | expression '<' '<' expression
                      | expression '>' '>' expression
                      | expression '!' '=' expression 
                      | expression '=' '=' expression 
                      | expression '<' '=' expression %prec LESSEQ
                      | expression '>' '=' expression %prec GREATEREQ
                                    '''
        l_leaf = p[1]
        r_leaf = p[4]
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)

        if p[2] == '&':
            new_branch.setType("AND")
            sym_table.appendGrammar(22, 'expression -> expression && expression')
        elif p[2] == '|':
            new_branch.setType("OR")
            sym_table.appendGrammar(23, 'expression -> expression || expression')
        elif p[2] == '<' and p[3] == '<':
            new_branch.setType("SLEFT")
            sym_table.appendGrammar(24, 'expression -> expression << expression')
        elif p[2] == '>' and p[3] == '>':
            new_branch.setType("SRIGHT")
            sym_table.appendGrammar(25, 'expression -> expression >> expression')
        elif p[2] == '!':
            new_branch.setType("NOEQUAL")
            sym_table.appendGrammar(26, 'expression -> expression != expression')
        elif p[2] == '=':
            new_branch.setType("EQUAL")
            sym_table.appendGrammar(27, 'expression -> expression == expression')
        elif p[2] == '<' and p[3] == '=':
            new_branch.setType("LE_OP")
            sym_table.appendGrammar(28, 'expression -> expression <= expression')
        elif p[2] == '>' and p[3] == '=':
            new_branch.setType("GE_OP")
            sym_table.appendGrammar(29, 'expression -> expression >= expression')
        p[0] = new_branch

    def p_expression(p):
        'expression : term '
        p[0] = p[1]
        global sym_table
        sym_table.appendGrammar(30, 'expression -> term ')

    def p_expression_uminus(p):
        "expression : '-' expression %prec UMINUS"
        l_leaf = p[2]
        r_leaf = leaf(-1, "INT")
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)
        new_branch.setType("MUL")
        sym_table.appendGrammar(31, 'term -> - expression')
        p[0] = new_branch


    def p_function_call(p):
        'function_call : ID "(" parentheses_expression'
        new_branch = branch()
        new_branch.setType("CALL")
        new_branch.add(leaf(p[1], "ID"))
        if p[3] != None:
            new_branch.add(p[3])

        p[0] = new_branch

    def p_parentheses_expression(p):
        '''parentheses_expression : expression_list ")" 
                                |   ")" '''
        if len(p) > 2:
            p[0] = p[1]

    def p_expression_list(p):
        '''expression_list : expression_list "," expression
                        |   expression '''
        if len(p) == 2:
            new_branch = branch()
            new_branch.add(p[1])
            new_branch.setType("SCOPE")
            new_branch.setValue("ARGS")
            p[0] = new_branch
        else:
            new_branch = p[1]
            new_branch.add(p[3])
            p[0] = new_branch

    def p_term_group(p):
        '''expression : '(' INT ')' expression %prec CAST
                    | '(' FLOAT ')' expression %prec CAST
                    | '(' CHAR ')' expression %prec CAST
                    | '(' ID ')' expression %prec CAST
                    | '(' expression ')'
                    | '~' expression
                    | '!' expression %prec NOT_PRE
                    | '&' ID %prec POINT
                    | expression '?' expression ':' expression
                    | function_call '''

        global sym_table
        new_branch = branch()
        if p[1] == '(':
            if len(p) > 4: 
                l_leaf = p[4]
                new_branch.add(l_leaf)
                if p[2] == 'int':
                    new_branch.setType("TOINT")
                    sym_table.appendGrammar(32, 'expression -> ( INT ) expression')
                elif p[2] == 'float':
                    new_branch.setType("TOFLOAT")
                    sym_table.appendGrammar(33, 'expression -> ( FLOAT ) expression')
                elif p[2] == 'char':
                    new_branch.setType("TOCHAR")
                    sym_table.appendGrammar(34, 'expression -> ( CHAR ) expression')
                else:
                    new_branch.setType("TOID")
                    sym_table.appendGrammar(34, 'expression -> ( ID ) expression')          
            else:
                new_branch = p[2]
                sym_table.appendGrammar(35, 'expression -> ( expression )')
        elif p[1] == '~':
            l_leaf = p[2]
            new_branch.add(l_leaf)
            new_branch.setType("BNOT")
            sym_table.appendGrammar(36, 'expression -> ~ expression')
        elif p[1] == '!':
            l_leaf = p[2]
            new_branch.add(l_leaf)
            new_branch.setType("NOT")
            sym_table.appendGrammar(37, 'expression -> ! expression')
        elif p[1] == '&':
            l_leaf = leaf(p[2], "ID")
            new_branch.add(l_leaf)
            new_branch.setType("POINT")
            sym_table.appendGrammar(38, 'expression -> & ID')
        else:
            new_branch = p[1]
            sym_table.appendGrammar(38.1, 'expression -> function_call')

        p[0] = new_branch

    def p_term_number(p):
        'term : NUMBER'
        l_leaf = leaf(p[1], "INT")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(42, 'term -> NUMBER')

    def p_term_decimal(p):
        'term : NUMBER "." NUMBER '
        powder = p[3]
        for i in range(len(str(p[3]))):
            powder = powder/10
        double = float(p[1]) + powder
        l_leaf = leaf(double, "FLOAT")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(43, 'term -> NUMBER "." NUMBER')

    def p_term_string(p):
        'term : STRING'
        l_leaf = leaf(p[1], "STRING")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(44, 'factor -> STRING')

    def p_term_id(p):
        'term : is_array_term'
        p[0] = p[1]
        global sym_table
        sym_table.appendGrammar(47, 'factor -> is_array_term')

    def p_error(p):
        global sym_table
        if p:
            global __text
            sym_table.error += "Syntax error at line:" + str(p.lineno) + ", column:" + str(find_column(__text, p)) + "\n"
            print(sym_table.error)
        else:
            print("Syntax error at EOF")

    # build the parser
    parser = yacc.yacc()

    # called when send param to parser function
    def input(self, text, new_sym_table):
        global __text
        global sym_table
        __text = text
        sym_table = new_sym_table
        result = parser.parse(text, lexer=lexer)
        return result

    return input
