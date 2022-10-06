from proofchecker.utils.ply.lex import lex
from .ply import yacc 

from .binarytree import Node
from .follexer import tokens, lexer

# Ordered lowest to highest
precedence = (
    ('right', 'IMPLIES', 'IFF'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

def p_formula_binary_op(p):
    '''
    formula : formula IFF formula
            | formula IMPLIES formula
            | formula OR formula
            | formula AND formula
    '''
    # Construct tree node
    p[0] = Node(p[2])
    p[0].left = p[1]
    p[0].right = p[3]

    # Reformat symbol if necessary
    if p[0].value != ('∧' or '∨' or '→' or '↔'):
        if p[0].value == '^':
            p[0].value = '∧'
        if p[0].value == '&':
            p[0].value = '∧'
        if p[0].value == '|':
            p[0].value = '∨'
        if p[0].value == '>':
            p[0].value = '→'
        if p[0].value == '->':
            p[0].value = '→'
        if p[0].value == '<->':
            p[0].value = '↔'


def p_formula_unary_op(p):
    '''
    formula : NOT formula
    '''

    # Create tree node
    p[0] = Node(p[1])
    p[0].right = p[2]

    # Reformat symbol if necessary
    if p[0].value != '¬':
        p[0].value = '¬'


def p_formula_quanitifier(p):
    '''
    formula : QUANTIFIER VAR MEMBERSHIP DOMAIN formula
    '''
    p[0] = Node(p[1] + p[2] + p[3] + p[4])
    p[0].right = p[5]


def p_formula_parens(p):
    '''
    formula : LPAREN formula RPAREN
    '''
    p[0] = p[2]

def p_equals_formula(p):
    '''
    formula : term EQUALS term
            | atomic_formula EQUALS atomic_formula
    '''
    p[0] = Node(p[2])
    p[0].left = Node(p[1])
    p[0].right = Node(p[3])

def p_formula(p):
    '''
    formula : atomic_formula
    '''
    p[0] = Node(p[1])


def p_atomic_formula_x(p):
    '''
    atomic_formula : PREDICATE term
                   | PREDICATE term_x
    '''
    p[0] = (p[1] + p[2])


def p_atomic_formula_parens(p):
    '''
    atomic_formula : PREDICATE LPAREN term_c RPAREN
    '''
    p[0] = (p[1] + p[2] + p[3] + p[4])


def p_atomic_formula_bool(p):
    '''
    atomic_formula : BOOL
    '''
    p[0] = p[1]

def p_term_x(p):
    '''
    term_x : term term
           | term term_x
    '''
    p[0] = (p[1] + p[2])


def p_term_c_comma(p):
    '''
    term_c : term_c COMMA term_c
    '''
    p[0] = (p[1] + p[2] + p[3])


def p_term_c(p):
    '''
    term_c : term
    '''
    p[0] = p[1]


def p_term(p):
    '''
    term : VAR
         | NAME
    '''
    p[0] = p[1]


# TODO: Create more elegant error handling
#       Define additional grammar rules for errors
# Error rule for syntax errors
def p_error(p):
    raise SyntaxError

# Build the parser
parser = yacc.yacc()
parser.lexer = lexer

def test():
    while True:
        try:
            s = input('FOL > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        #print(result) #commented out this printline

# # Invalid syntax
# class TFLSyntaxError(Exception):
#     """
#     Raised when the parser determines the TFL syntax is invalid 

#     Attributes:
#         expression -- input expression in which teh error occurred
#         message -- explanation of the error
#     """

#     def __init__(self, expression, message):
#         self.expression = expression
#         self.message = message