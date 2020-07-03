# pylint: disable=W,import-error
import ply.lex as lex
import ply.yacc as yacc
from syntax_tree.branch import branch as branch
from syntax_tree.leaf import leaf as leaf
from sym_table.table import table
'''
s -> code

code -> code LABEL ':' list
      | MAIN ':' list

list -> list statement ';'
      | statement ';'

statement -> is_array_term '='  expression 
            | PRINT '(' term ')'
            | UNSET '(' term ')'
            | IF '(' expression ')' GOTO LABEL
            | GOTO LABEL
            | EXIT

term -> is_array_term
        | NUMBER 
        | FLOAT 

is_array_term -> is_array_term '[' term ']'
	  	| VAR

expression -> term '+' term
            | term '-' term
            | term '*' term
            | term '/' term
            | term '%' term
            | term '&' term 
            | term '|' term
            | term '^' term
            | term '<' term
            | term '>' term
            | term XOR term

            | term '&''&' term
            | term '|''|' term
            | term '<''<' term
            | term '>''>' term
            | term '!''=' term
            | term '=''=' term
            | term '>''=' term
            | term '<''=' term
            
            | '(' INT ')' term
            | '(' FLOAT ')' term
            | '(' CHAR ')' term
            | ABS '(' term ')'
            | '~' term
            | '!' term
            | ARRAY '(' ')'
            | term
'''


def parse():
    # tokenizing rules
    reserved = {
                'main'  : 'MAIN',
                'if'    : 'IF',
                'print' : 'PRINT',
                'abs'   : 'ABS',
                'goto'  : 'GOTO',
                'xor'   : 'XOR',
                'read'  : 'READ',
                'unset' : 'UNSET',
                'array' : 'ARRAY',
                'int'   : 'INT',
                'float' : 'FLOAT',
                'char'  : 'CHAR',
                'exit'  : 'EXIT'
                }

    tokens = [
                'VAR',
                'NUMBER',
                'STRING',
                'LABEL'
            ] + list(reserved.values())

    literals = ['=', '\'', '"', '+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '!', '~', '(', ')', '[', ']', ';', ':', '.'] 

    t_ignore = " \t"

    def t_VAR(t):
        r'[$] ( [tavTAV][0-9]*| s(p|[0-9]*) | ra)'
        global sym_table
        # add var to symbol table
        if t.value[1] == 't':
            sym_table.add(str(t.value), 'TEMPORAL', 0, None, sym_table.getScope())
        elif t.value[1] == 'a':
            sym_table.add(str(t.value), 'PARAMETER', 0, None, sym_table.getScope())
        elif t.value[1] == 'v':
            sym_table.add(str(t.value), 'RETURNEDVALUE', 0, None, sym_table.getScope())
        elif t.value[1] == 'r':
            sym_table.add(str(t.value), 'RETURNPOINTER', 0, None, sym_table.getScope())
        elif t.value[1] == 's':
            if t.value[2] == 'p':
                sym_table.add(str(t.value), 'STACKPOINTER', 0, None, sym_table.getScope())
            else:
                sym_table.add(str(t.value), 'STACK', 0, None, sym_table.getScope())
        return t

    t_ignore_COMMENT = r'[#].*'

    def t_STRING(t):
        r'( \"([^\\\n]|(\\.))*?\"  | \'([^\\\n]|(\\.))*?\' )'
        t.value = str(t.value).replace("\"","")
        t.value = str(t.value).replace("\'","")
        return t

    def t_NUMBER(t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_LABEL(t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        global sym_table
        # check if reserved word
        if t.value in reserved:
            t.type = reserved.get(t.value)
            if t.value == 'main':
                # add MAIN label to symbol table
                sym_table.add('MAIN', 'LABEL', 0, None, 'GLOBAL')
                sym_table.setScope('MAIN')
        else:
            # add label to symbol table
            sym_table.add(str(t.value), 'LABEL', 0, None, 'GLOBAL')
            sym_table.setScope(str(t.value))
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
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS')
    )

    def p_start(p):
        'start : code'
        global __ast
        global sym_table
        sym_table.appendGrammar(0, 's -> code')
        p[0] = [__ast, sym_table]

    def p_code(p):
        '''code : code LABEL ":" list
                | code LABEL ":"
                | MAIN ":"
                | MAIN ":" list '''
        global __ast
        global sym_table
        if len(p) == 4:
            if p[3] != ':':
                p[3].setType("LABEL")
                p[3].setValue("MAIN")
                __ast.add(p[3])
                sym_table.appendGrammar(1, 'code -> MAIN : list')
            else:
                new_branch= branch()
                new_branch.setType("LABEL")
                new_branch.setValue(str(p[2]))
                __ast.add(new_branch)
                sym_table.appendGrammar(2.1, 'code -> code LABEL :')
        elif len(p) == 3:
            new_branch = branch()
            new_branch.setType("LABEL")
            new_branch.setValue("MAIN")
            __ast.add(new_branch)
            sym_table.appendGrammar(1.1, 'code -> MAIN :')
        else:
            p[4].setType("LABEL")
            p[4].setValue(str(p[2]))
            __ast.add(p[4])
            sym_table.appendGrammar(2, 'code -> code LABEL : list')
        p[0] = __ast

    # syntax error recovery
    def p_statement_error(p):
        '''list : list error ";" 
                | error ";" '''
        if len(p) > 3:
            p[0] = p[1]
        else:
            p[0] = None

    def p_statement_list(p):
        '''list : list statement ";" 
                | statement  ";" '''
        global sym_table
        if len(p) == 3:
            new_branch = branch()
            new_branch.add(p[1])
            p[0] = new_branch
            sym_table.appendGrammar(3, 'list -> statement ;')
        else:
            if p[1] != None: 
                p[1].add(p[2])
                p[0] = p[1]
                sym_table.appendGrammar(4, 'list -> list statement ;')
            else:
                new_branch = branch()
                new_branch.add(p[2])
                p[0] = new_branch
                sym_table.appendGrammar(3, 'list -> statement ;')

    def p_statement_assign(p):
        'statement : is_array_term "=" expression'
        global sym_table
        l_leaf = p[1]
        r_leaf = p[3]

        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)
        new_branch.setType("ASSIGN")

        p[0] = new_branch
        sym_table.appendGrammar(5, 'statement -> is_array_term = expression')

    def p_statement_expr(p):
        'statement : PRINT "(" term  ")" '
        global sym_table
        leaf = p[3]
        new_branch = branch()
        new_branch.add(leaf)
        new_branch.setType("PRINT")

        p[0] = new_branch
        sym_table.appendGrammar(6, 'statement -> PRINT ( term  ) ')

    def p_statement_group(p):
        '''statement : IF '(' expression ')' GOTO LABEL
                     | UNSET '(' term ')'
                     | GOTO LABEL
                     | EXIT                          '''
        global sym_table
        new_branch = branch()
        if len(p) > 5:
            new_branch.add(p[3])
            r_leaf = leaf(p[6], "LABEL")
            new_branch.add(r_leaf)
            new_branch.setType("IF")
            sym_table.appendGrammar(7, 'statement -> IF ( expression ) GOTO LABEL ')
        elif len(p) > 3:
            new_branch.add(p[3])
            new_branch.setType("UNSET")
            sym_table.appendGrammar(8, 'statement -> UNSET ( term ) ')
        elif len(p) > 2:
            r_leaf = leaf(p[2], "LABEL")
            new_branch.add(r_leaf)
            new_branch.setType("GOTO")
            sym_table.appendGrammar(9, 'statement -> GOTO LABEL ')
        else:
            new_branch.setType("EXIT")
            sym_table.appendGrammar(10, 'statement -> EXIT ')
        p[0] = new_branch

    def p_expression_binop(p):
        '''expression : term '+' term
                      | term '-' term
                      | term '*' term
                      | term '/' term
                      | term '%' term
                      | term '&' term
                      | term '|' term
                      | term '^' term
                      | term '<' term
                      | term '>' term
                      | term XOR term
                      '''
        l_leaf = p[1]
        r_leaf = p[3]
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)

        if p[2] == '+':
            new_branch.setType("ADD")
            sym_table.appendGrammar(11, 'expression -> term + term')
        elif p[2] == '-':
            new_branch.setType("SUB")
            sym_table.appendGrammar(12, 'expression -> term - term')
        elif p[2] == '*':
            new_branch.setType("MUL")
            sym_table.appendGrammar(13, 'expression -> term * term')
        elif p[2] == '/':
            new_branch.setType("DIV")
            sym_table.appendGrammar(14, 'expression -> term / term')
        elif p[2] == '%':
            new_branch.setType("MOD")
            sym_table.appendGrammar(15, 'expression -> term % term')
        elif p[2] == '&':
            new_branch.setType("BAND")
            sym_table.appendGrammar(16, 'expression -> term & term')
        elif p[2] == '|':
            new_branch.setType("BOR")
            sym_table.appendGrammar(17, 'expression -> term | term')
        elif p[2] == '^':
            new_branch.setType("BXOR")
            sym_table.appendGrammar(18, 'expression -> term ^ term')
        elif p[2] == '<':
            new_branch.setType("LTHAN")
            sym_table.appendGrammar(19, 'expression -> term < term')
        elif p[2] == '>':
            new_branch.setType("GTHAN")
            sym_table.appendGrammar(20, 'expression -> term > term')
        else:
            new_branch.setType("XOR")
            sym_table.appendGrammar(21, 'expression -> term XOR term')
        p[0] = new_branch

    def p_expression_binop2(p):
        '''expression : term '&' '&' term
                      | term '|' '|' term
                      | term '<' '<' term
                      | term '>' '>' term
                      | term '!' '=' term
                      | term '=' '=' term
                      | term '<' '=' term
                      | term '>' '=' term
                                    '''
        l_leaf = p[1]
        r_leaf = p[4]
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)

        if p[2] == '&':
            new_branch.setType("AND")
            sym_table.appendGrammar(22, 'expression -> term && term')
        elif p[2] == '|':
            new_branch.setType("OR")
            sym_table.appendGrammar(23, 'expression -> term || term')
        elif p[2] == '<' and p[3] == '<':
            new_branch.setType("SLEFT")
            sym_table.appendGrammar(24, 'expression -> term << term')
        elif p[2] == '>' and p[3] == '>':
            new_branch.setType("SRIGHT")
            sym_table.appendGrammar(25, 'expression -> term >> term')
        elif p[2] == '!':
            new_branch.setType("NOEQUAL")
            sym_table.appendGrammar(26, 'expression -> term != term')
        elif p[2] == '=':
            new_branch.setType("EQUAL")
            sym_table.appendGrammar(27, 'expression -> term == term')
        elif p[2] == '<' and p[3] == '=':
            new_branch.setType("LE_OP")
            sym_table.appendGrammar(28, 'expression -> term <= term')
        elif p[2] == '>' and p[3] == '=':
            new_branch.setType("GE_OP")
            sym_table.appendGrammar(29, 'expression -> term >= term')
        p[0] = new_branch

    def p_expression(p):
        'expression : term '
        p[0] = p[1]
        global sym_table
        sym_table.appendGrammar(30, 'expression -> term ')

    def p_term_uminus(p):
        "term : '-' factor %prec UMINUS"
        l_leaf = p[2]
        r_leaf = leaf(-1, "NUM")
        global sym_table
        new_branch = branch()
        new_branch.add(l_leaf)
        new_branch.add(r_leaf)
        new_branch.setType("MUL")
        sym_table.appendGrammar(31, 'term -> - factor')
        p[0] = new_branch

    
    def p_term_group(p):
        '''expression : '(' INT ')' factor
                    | '(' FLOAT ')' factor
                    | '(' CHAR ')' factor
                    | '(' factor ')'
                    | '~' factor
                    | '!' factor
                    | '&' VAR
                    | ABS '(' factor ')'
                    | ARRAY '(' ')'
                    | READ '(' ')'           
                                '''
        global sym_table
        new_branch = branch()
        if p[1] == '(':
            l_leaf = p[4]
            new_branch.add(l_leaf)
            if p[2] == 'int':
                new_branch.setType("TOINT")
                sym_table.appendGrammar(32, 'expression -> ( INT ) factor')
            elif p[2] == 'float':
                new_branch.setType("TOFLOAT")
                sym_table.appendGrammar(33, 'expression -> ( FLOAT ) factor')
            elif p[2] == 'char':
                new_branch.setType("TOCHAR")
                sym_table.appendGrammar(34, 'expression -> ( CHAR ) factor')
            else:
                new_branch = p[2]
                sym_table.appendGrammar(35, 'expression -> ( factor )')
        elif p[1] == '~':
            l_leaf = p[2]
            new_branch.add(l_leaf)
            new_branch.setType("BNOT")
            sym_table.appendGrammar(36, 'expression -> ~ factor')
        elif p[1] == '!':
            l_leaf = p[2]
            new_branch.add(l_leaf)
            new_branch.setType("NOT")
            sym_table.appendGrammar(37, 'expression -> ! factor')
        elif p[1] == '&':
            l_leaf = leaf(p[2], "ID")
            new_branch.add(l_leaf)
            new_branch.setType("POINT")
            sym_table.appendGrammar(38, 'expression -> & factor')
        elif p[1] == 'abs':
            l_leaf = p[3]
            new_branch.add(l_leaf)
            new_branch.setType("ABS")
            sym_table.appendGrammar(39, 'expression -> ABS ( factor )')
        elif p[1] == 'array':
            new_branch.setType("ARRAY")
            sym_table.appendGrammar(40, 'expression -> ARRAY ( )')
        elif p[1] == 'read':
            new_branch.setType("READ")
            sym_table.appendGrammar(41, 'expression -> READ ( )')

        p[0] = new_branch

    def p_expression_number(p):
        'factor : NUMBER'
        l_leaf = leaf(p[1], "NUM")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(42, 'factor -> NUMBER')

    def p_expression_decimal(p):
        'factor : NUMBER "." NUMBER'
        powder = p[3]
        for i in range(len(str(p[3]))):
            powder = powder/10
        double = float(p[1]) + powder
        l_leaf = leaf(double, "FLOAT")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(43, 'factor -> DECIMAL')

    def p_expression_string(p):
        'factor : STRING'
        l_leaf = leaf(p[1], "STRING")
        p[0] = l_leaf
        global sym_table
        sym_table.appendGrammar(44, 'factor -> STRING')

    def p_term_array(p):
        '''is_array_term : is_array_term '[' factor ']'
	  	                | VAR
                                                '''
        global sym_table
        if len(p) > 2:
            new_branch = branch()
            new_branch.add(p[1])
            new_branch.add(p[3])
            new_branch.setType("ACCESS")
            p[0] = new_branch
            sym_table.appendGrammar(45, 'is_array_term -> is_array_term [ factor ]')
        else:
            l_leaf = leaf(p[1], "ID")
            p[0] = l_leaf
            sym_table.appendGrammar(46, 'is_array_term -> VAR')

    def p_factor_id(p):
        'factor : is_array_term'
        p[0] = p[1]
        global sym_table
        sym_table.appendGrammar(47, 'factor -> is_array_term')

    def p_term_factor(p):
        'term : factor'
        p[0] = p[1]
        global sym_table
        sym_table.appendGrammar(48, 'term -> factor')

    def p_error(p):
        global sym_table
        if p:
            global __text
            sym_table.error += "Syntax error at line:" + str(p.lineno) + ", column:" + str(find_column(__text, p)) + "\n"
        else:
            print("Syntax error at EOF")

    # build the parser
    parser = yacc.yacc()

    # called when send param to parser function
    def input(self, text):
        global __ast
        global __text
        global sym_table
        __ast = branch()
        __text = text
        sym_table = table()
        sym_table.setMode(1)
        result = parser.parse(text, lexer=lexer)
        return result

    return input
