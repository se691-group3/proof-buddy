
from xml.dom import NAMESPACE_ERR


class Constants:
    ATOMIC = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
        'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    CONNECTIVES = ['∧', '∨', '¬', '→', '↔']
    PARENS = ['(', '[', '{', ')', ']', '}']
    OPEN_PARENS=['(', '[', '{']
    CLOSED_PARENS=[')', ']', '}']
    TFL_BASIC_RULES = ['∧I','∧E','∨I','∨E','¬I','¬E','→I','→E','X','IP',]
    TFL_DERIVED_RULES = ['⊥I','⊥E','TND','↔I','↔E','DS','R','MT','DNE','DeM','Pr','Hyp','LEM']
    QUANTIFIERS = ['∀', '∃']

    # FOL
    NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', \
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']
    VARS = ['s', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    PREDICATES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', \
        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
    DOMAINS = ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    # Rules
    RULES_CHOICES= {
    'tfl_basic': 'TFL - Basic Rules Only',
    'tfl_derived': 'TFL - Basic & Derived Rules',
    'fol_basic': 'FOL - Basic Rules Only',
    'fol_derived': 'FOL - Basic & Derived Rules',
    }