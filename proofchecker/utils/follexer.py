from .ply import lex

# List of token names
tokens = [
    'NAME',
    'VAR',
    'PREDICATE',
    'DOMAIN',
    'QUANTIFIER',
    'MEMBERSHIP',
    'AND',
    'OR',
    'NOT',
    'IMPLIES',
    'IFF',
    'LPAREN',
    'RPAREN',
    'BOOL',
    'EQUALS',
    'COMMA'
]

# Regular expression rules for simple tokens
t_NAME=r'[a-r]'
t_VAR=r'[s-z]'
t_PREDICATE=r'[A-R]'
t_DOMAIN=r'[S-Z]'
t_QUANTIFIER=r'(∀|∃)'
t_MEMBERSHIP=r'(∈)'
t_AND=r'(∧|\^|\&)'
t_OR=r'(∨|\|)'
t_NOT=r'(¬|~|-)'
t_IMPLIES=r'(→|>|(->))'
t_IFF=r'(↔|(<->))'
t_LPAREN=r'((\()|(\[)|(\{))'
t_RPAREN=r'((\))|(\])|(\}))'
t_BOOL=r'((True)|(TRUE)|(False)|(FALSE)|⊥)'
t_EQUALS = r'(=)'
t_COMMA = r'(,)'

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
    raise IllegalCharacterFOLError(expression, message)

# Build the lexer
lexer = lex.lex()

# Test it output
def test(data):
    lexer.input(data)
    while True:
            tok = lexer.token()
            if not tok:
                break
            #print(tok) #commented out this printline

# Illegal Character
class IllegalCharacterFOLError(Exception):
    """
    Raised when the scanner encounters an illegal character

    Attributes:
        expression -- input expression in which teh error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message