from .ply import lex

# List of token names
tokens = [
    'NUMBER',
    'DOT'
]

# Regular expression rules for tokens
t_NUMBER = r'\d+'
t_DOT = '\.'

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    expression = t
    message = "Illegal character '%s'" % t.value[0]
    raise IllegalCharacterError(expression, message)

# Build the lexer
lexer = lex.lex()

# Illegal Character
class IllegalCharacterError(Exception):
    """
    Raised when the scanner encounters an illegal character

    Attributes:
        expression -- input expression in which teh error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message