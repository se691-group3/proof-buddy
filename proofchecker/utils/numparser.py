from .ply import yacc
from .numlexer import tokens

def p_num_dot_num(p):
    '''
    line_no : line_no DOT line_no
    '''
    p[0] = p[1] + p[3]

def p_num(p):
    '''
    line_no : NUMBER
    '''
    p[0] = 1

# Error rule for syntax errors
def p_error(p):
    raise SyntaxError

# Build the parser
parser = yacc.yacc()