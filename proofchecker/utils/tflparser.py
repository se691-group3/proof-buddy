from proofchecker.utils.ply.lex import lex #could this have been just .ply.lex   (prolly, since the . act like / for subdirs)
from .ply import yacc 

from .binarytree import Node
from .tfllexer import tokens, lexer

# Ordered lowest to highest
precedence = (
    ('right', 'IMPLIES', 'IFF'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

def p_sentence_binary_op(p):
    '''
    sentence : sentence IFF sentence
             | sentence IMPLIES sentence
             | sentence OR sentence
             | sentence AND sentence
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
        if p[0].value == 'v':
            p[0].value = '∨'
        if p[0].value == '>':
            p[0].value = '→'
        if p[0].value == '->':
            p[0].value = '→' 
        if p[0].value == '<->':
            p[0].value = '↔'


def p_sentence_unary_op(p):
    'sentence : NOT sentence'

    # Create tree node
    p[0] = Node(p[1])
    p[0].right = p[2]

    # Reformat symbol if necessary
    if p[0].value != '¬':
        p[0].value = '¬'

def p_sentence_parens(p):
    'sentence : LPAREN sentence RPAREN'
    p[0] = p[2]

def p_sentence(p):
    '''
    sentence : BOOL
             | VAR
    '''
    p[0] = Node(p[1])

# TODO: Create more elegant error handling
#       Define additional grammar rules for errors
# Error rule for syntax errors
def p_error(p):
    raise SyntaxError

# Build the parser
parser = yacc.yacc()
parser.lexer = lexer

# def test():
#     while True:
#         try:
#             s = input('TFL > ')
#         except EOFError:
#             break
#         if not s: continue
#         result = parser.parse(s)
#         print(result)

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