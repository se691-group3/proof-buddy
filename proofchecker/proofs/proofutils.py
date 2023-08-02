from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.utils import numparser
from proofchecker.utils.binarytree import Node, tree_to_string
from proofchecker.utils.constants import Constants
from proofchecker.utils.numlexer import lexer as numlexer
from proofchecker.utils.tfllexer import IllegalCharacterError
from proofchecker.proofs.exprMethods import OBJS, VARS, PREDS, UNASYMBOLS, BINSYMBOLS

# Parsing methods
def depth(line_no):
    """
    Calculates the depth of a line number
    """
    return numparser.parser.parse(line_no, lexer=numlexer)

def make_tree(string: str, parser):
    """
    Function to construct a binary tree
    """
    # CHANGED TO SEE HOW STRINGS STORED IN TREE (parens not part of it)
    ans = parser.parse(string, lexer=parser.lexer)
    return ans

def is_line_no(string: str):
    """
    Function to determine if a line number is valid
    """
    return numparser.parser.parse(string, lexer=numlexer)

def is_name(ch):
    """
    Function to determine if a character is an FOL name (a-r)
    """
    return (ch in Constants.NAMES)

def is_var(ch):
    """
    Function to determine if a character is an FOL variable (s-z)
    """
    return (ch in Constants.VARS)

def is_predicate(ch):
    """
    Function to determine if a character is an FOL predicate (A-R)
    """
    return (ch in Constants.PREDICATES)

def is_domain(ch):
    """
    Function to determine if a character is an FOL domain (S-Z)
    """
    return (ch in Constants.DOMAINS)

def is_quantifier(ch):
    """
    Function to determine if a character is an FOL quantifier
    """
    return (ch in Constants.QUANTIFIERS)

# Proof Verification
def is_conclusion(current_line: ProofLineObj, proof: ProofObj, parser):
    """
    Verify whether the current_line is the desired conclusion
    """
    response = ProofResponse
    try:
        current = make_tree(current_line.expression, parser)
        conclusion = make_tree(proof.conclusion, parser)

        if current == conclusion:
            return True
        
        return False
    except:
        return False

def is_valid_expression(expression: str, parser):
    """
    Verify if a string is a valid Boolean expression
    Returns a Boolean (True/False)
    """
    # Verify the expression is valid

    if expression == "":
        return False
    try:
        expression = make_tree(expression, parser)
        return True
    except:
        return False

def verify_expression(expression: str, parser):
    """
    Verify if a string is a valid boolean expression
    Returns a ProofResponse
    """
    response = ProofResponse()
    if expression == "":
        response.err_msg = "Expression cannot be an empty string"
        return response
    # Verify the expression is valid
    try:
        exp = make_tree(expression, parser)
        response.is_valid = True
        return response

    except IllegalCharacterError as char_err:
        response.err_msg = "{} in expression {}"\
            .format(char_err.message, str(expression))
        return response 
    except:
        response.err_msg = "Syntax error in expression {}"\
            .format(str(expression))
        return response
    

def get_citable_lines(current_line: ProofLineObj, proof: ProofObj):
    """
    Returns a list of all lines that are citable from the current line
    """
    citable_lines = []

    for line in proof.lines:
        if line != current_line:
            result = verify_line_citation(current_line.line_no, line.line_no)
            if result.is_valid:
                citable_lines.append(line)

    return citable_lines


def verify_line_citation(current_line_no: str, cited_line_no: str):
    """
    Verify whether an individual line citation is valid
    Returns a ProofResponse with an error message if invalid
    """
    response = ProofResponse()
    
    try:
        # Calculate the depth of each line number
        #note: depth is an integer representing the number of ints. e.g. "3.4.1" has depth 3
        current_depth = depth(current_line_no)
        cited_depth = depth(cited_line_no)

        # this wasn't always being caught, so put it in as a first check
        if current_line_no == cited_line_no:
            response.err_msg = "Error on line {}: Invalid citation: a line cannot justify itself"\
                .format(current_line_no)
            return response
        
        # Check if the cited line occurs within a subproof that has not been closed
        # before the line where the rule is applied (this is a violation)
        if cited_depth > current_depth:
            response.err_msg = "Error on line {}: Invalid citation: Line {} exists within in a subproof at a lower depth than line {}"\
                .format(current_line_no, cited_line_no, current_line_no)
            return response

        # Create an array of nested line numbers
        current_nums = current_line_no.replace('.', ' ').split()
        cited_nums = cited_line_no.replace('.', ' ').split()
        x = 0
        
        # Check that the current line occurs after the cited line in the proof
        while x < cited_depth:
            if int(current_nums[x]) < int(cited_nums[x]):
                response.err_msg = "Error on line {}: Invalid citation: Line {} occurs after line {}"\
                    .format(current_line_no, cited_line_no, current_line_no)
                return response
            elif cited_nums[x] < current_nums[x]:
                if x != (cited_depth-1):
                    response.err_msg = "Error on line {}: Invalid citation: Line {} occurs in a previous subproof"\
                        .format(current_line_no, cited_line_no)
                    return response
            x += 1
        
        # If all the other checks pass, line citation is valid
        response.is_valid = True
        return response

    except:
        response.err_msg = "Error on line {}: Invalid line citations are provided on line {}.  Perhaps you're referencing the wrong rule?"\
            .format(current_line_no, current_line_no)
        return response


def get_premises(premises: str):
    """
    Take a string of comma separated-premises
    and return an array of premises
    """
    if premises == None:
        return ''
    premises = premises.replace(' ', '')
    premises = premises.replace(';', ' ')
    return premises.split()


rule_errors = ['∧ ', '∨ ', '¬ ', '→ ', '↔ ', '∀ ', '∃ ']

def fix_rule_whitespace_issues(rule):
    """
    If the user put a space between the rule symbol and I/E, fix it
    (e.g. If user entered '∧ E 1' instead of '∧E 1')
    """
    new_rule = rule
    if rule[0:2] in rule_errors:
        new_rule = rule[0] + rule[2:len(rule)]
    return new_rule

def get_line_no(rule):
    """
    Get a single line number in a TFL citation
    """
    fixed_rule = fix_rule_whitespace_issues(rule)
    target_line_no = fixed_rule[2:len(fixed_rule)]
    return target_line_no.strip()

def get_line_nos(rule):
    """
    Get multiple line numbers in a TFL citation
    """
    fixed_rule = fix_rule_whitespace_issues(rule)
    target_line_nos = fixed_rule[3:len(fixed_rule)]
    target_line_nos = target_line_nos.replace('-', ' ')
    target_line_nos = target_line_nos.replace(',', ' ')
    return target_line_nos.split()

def get_line(rule: str, proof: ProofObj):
    """
    Find a single line from a TFL rule
    """
    target_line_no = get_line_no(rule)
    target_line = None
    for line in proof.lines:
        if str(target_line_no) == str(line.line_no):
            target_line = line
            break
    return target_line

def get_line_with_line_no(line_no: str, proof: ProofObj):
    """
    Find a single line using the line number
    """
    target_line = None
    for line in proof.lines:
        if line_no == str(line.line_no):
            target_line = line
            break
    return target_line    

def get_line_DNE(rule: str, proof: ProofObj):
    """
    Find a single line for rule DNE
    """
    target_line_no = rule[3:len(rule)].strip()
    target_line = None
    for line in proof.lines:
        if str(target_line_no) == str(line.line_no):
            target_line = line
            break
    return target_line

def get_lines(rule: str, proof: ProofObj):
    """
    Find multiple lines from a TFL rule
    """
    target_line_nos = get_line_nos(rule)
    target_lines = []
    for num in target_line_nos:
        for line in proof.lines:
            if str(num) == str(line.line_no):
                target_lines.append(line)
                break
    return target_lines

def get_lines_in_subproof(line_no: str, proof: ProofObj):
    """
    Returns the first and last line of a subproof
    """
    current_depth = depth(line_no)+1
    subproof = []
    for line in proof:
        if (line.line_no.startswith(line_no) and (depth(line.line_no) == current_depth)):
            subproof.append(line)
    if len(subproof) > 1:
        return[subproof[0], subproof[len(subproof)-1]]
    elif len(subproof) == 1:
        return [subproof[0], subproof[0]]
    else:
        return None

def get_expressions(lines):
    """
    Returns an array of expressions from an array of ProofLines
    """
    expressions = []
    for line in lines:
        expressions.append(line.expression)
    return expressions

def clean_rule(rule: str):
    """
    Replace symbols to clean the rule for rule verification
    """
    if rule[0] in '^&':
        clean_rule = '∧' + rule[1:len(rule)]
        return clean_rule
    if rule[0] == 'v':
        clean_rule = '∨' + rule[1:len(rule)]
        return clean_rule
    if rule[0] == '>':
        clean_rule = '→' + rule[1:len(rule)]
        return clean_rule
    if rule[0:2] == '->':
        clean_rule = '→' + rule[2:len(rule)]
        return clean_rule
    if rule[0] in '~-':
        clean_rule = '¬' + rule[1:len(rule)]
        return clean_rule

    return rule


# FOL Methods

def count_inputs(expression: str):
    """
    Count the number of inputs to a predicate
    (More accurately, counts the number of FOL variables and names in a string)
    """
    x = 0
    for ch in expression:
        if is_name(ch) or is_var(ch):
            x += 1

    return x


def verify_same_var_and_domain(tree_1: Node, tree_2: Node, line_no_1: str, line_no_2: str):
    """
    Check that two quantifiers refer to the same variable and domain
    """
    # If the expressions refer to quantifiers but reference different variables, return error message:
    if is_quantifier(tree_1.value[0]):

        # Check they refer to same variable
        if tree_1.value[1] != tree_2.value[1]:
            response = ProofResponse()
            response.err_msg = "The quantifiers on lines {} and {} do not refer to the same variable"\
                .format(line_no_1, line_no_2)
            return response

        # Check they refer to the same domain
        if tree_1.value[3] != tree_2.value[3]:
            response = ProofResponse()
            response.err_msg = "The quantifiers on lines {} and {} do not refer to the same domain"\
                .format(line_no_1, line_no_2)
            return response

    response = ProofResponse()
    response.is_valid = True
    return response


def find_c(var_tree: Node, name_tree: Node, var: str):
    """
    Find the name ("c") in name_tree that replaces the var in var_tree
    (Used for ∃E and ∀I validation)
    """
    # If either node is empty, return None
    if (var_tree == None or name_tree == None):
        return None

    if not is_predicate(var_tree.value[0]):
        if (var_tree.left != None) and (name_tree.left != None):
            result = find_c(var_tree.left, name_tree.left, var)
            if result != None:
                return result
        if (var_tree.right != None) and (name_tree.right != None):
            result = find_c(var_tree.right, name_tree.right, var)
            if result != None:
                return result

    index = 0
    var_indexes = []

    # Eliminate whitespace to make sure indexes match
    expression_with_vars = var_tree.value.replace(' ', '')
    expression_with_names = name_tree.value.replace(' ', '')

    # Keep track of the locations (indexes) of the bound variable on current line
    for ch in expression_with_vars:
        if ch == var:
            var_indexes.append(index)
        index += 1

    # If there are no variables, return None
    if len(var_indexes) == 0:
        return None

    # Get the values at these locations in line m
    names = []
    for i in var_indexes:
        names.append(expression_with_names[i])    

    # If there are no names, return None
    if len(names) == 0:
        return None
        
    return names[0]


def verify_same_structure_FOL(tree_1: Node, tree_2: Node, line_no_1: str, line_no_2: str):
    """
    Test to determine that two trees have the same structure
    """
    # If both nodes are empty, they have same structure
    if (tree_1.value == None and tree_2.value == None):
        response = ProofResponse()
        response.is_valid = True
        return response

    # If one node is empty and the other is not, return error message
    if (tree_1 == None and tree_2 != None) or (tree_1 != None and tree_2 == None):
        response = ProofResponse()
        response.err_msg = "Lines {} and {} do not have similar structure"\
            .format(line_no_1, line_no_2)
        return response         

    # If both nodes have values, continue
    if (tree_1 != None) and (tree_2 != None):

        # If one node has a left or right child where the other does not, return error message
        if (tree_1.left == None and tree_2.left != None) or (tree_2.left == None and tree_1.left != None) \
            or (tree_1.right == None and tree_2.left != None) or (tree_1.right == None and tree_2.right != None):
                response = ProofResponse()
                response.err_msg = "Lines {} and {} do not have similar structure"\
                    .format(line_no_1, line_no_2)
                return response

        # If both trees have a left node, check the left nodes for equivalent structure (recursive)
        if (tree_1.left != None) and (tree_2.left != None):
            response = verify_same_structure_FOL(tree_1.left, tree_2.left, line_no_1, line_no_2)
            if response.is_valid == False:
                return response

        # If both trees have a right node, check the right node for equivalent structure (recursive)
        if (tree_1.right != None) and (tree_2.right != None):
            response = verify_same_structure_FOL(tree_1.right, tree_2.right, line_no_1, line_no_2)
            if response.is_valid == False:
                return response

        # If the values of the nodes are equivalent, return valid
        if tree_1.value == tree_2.value:
            response = ProofResponse()
            response.is_valid = True
            return response
        
        # If one node is a predicate and the other is not, return error message
        if (is_predicate(tree_1.value[0]) and not is_predicate(tree_2.value[0]))\
            or (is_predicate(tree_2.value[0]) and not is_predicate(tree_1.value[0])):
                response = ProofResponse()
                response.err_msg = "Lines {} and {} do not have similar structure"\
                    .format(line_no_1, line_no_2)
                return response            

        # If the expressions refer to different predicates, return error message
        if is_predicate(tree_1.value[0]) and is_predicate(tree_2.value[0]):
            if tree_1.value[0] != tree_2.value[0]:
                response = ProofResponse()
                response.err_msg = "The expressions on lines {} and {} do not refer to the same predicate"\
                    .format(line_no_1, line_no_2)
                return response
            else:
                # If the predicates do not have the same number of inputs, return error message
                inputs_1 = count_inputs(tree_1.value)
                inputs_2 = count_inputs(tree_2.value)
                response = ProofResponse()
                if inputs_1 != inputs_2:
                    response.err_msg = "The predicates on lines {} and {} do not have the same number of inputs"\
                        .format(line_no_1, line_no_2)
                    return response
                else:
                    response.is_valid = True
                    return response
            
        # If the expressions refer to quantifiers but reference different variables, return error message:
        if is_quantifier(tree_1.value[0]):

            # Check they refer to same quantifier
            if tree_1.value[0] != tree_2.value[0]:
                response = ProofResponse()
                response.err_msg = "The expressions on lines {} and {} do not refer to the same quantifier"\
                    .format(line_no_1, line_no_2)
                return response

            # Check they refer to the same variable and domain
            result = verify_same_var_and_domain(tree_1, tree_2, line_no_1, line_no_2)
            if result.is_valid == False:
                return result
        
    # If we reached this point without returning a response, return valid
    response = ProofResponse()
    response.is_valid = True
    return response

# returns T or F if a non "x" is found as a key in a given dictionary (used in instanceOf)
# writing as a function so we can use returns instead of breaks
def nonVarFound(mydict:dict,var:str)->bool:
    for key in mydict: #note that iterating through a dictionary only goes through the keys by default
        if key != var:
            return True
    return False

# this was done as a separate function to avoid importing OBJS into universalelim.py
# this checks to make sure that if an x is getting replaced, then it's by a free var
def freeSubst(mydict:dict,var:str)->bool:
    return not (var in mydict.keys() and mydict[var] not in OBJS)


# finds the parent of myNode in MyTree (returns None if Root)
# note: in the future, the parent attribute should have been created at construction
def findParent(myTree:Node, targetNode:Node, parent=None)->Node:
    if myTree==None or targetNode==None:
        return None #technically a violation of the output type, so warning
    if myTree==targetNode:
        return parent #note, this will be None if target was root
    rightSearch = findParent(myTree.right, targetNode, myTree)
    leftSearch = findParent(myTree.left, targetNode, myTree)
    return leftSearch if leftSearch is not None else rightSearch

#returns T/F if var is bound in the scope of startNode
# e.g.  (∀x∈V (Px ∧ Qx)) ∧ Rx. the x in Qx is bound, but not the x in Rx
def varInScope(expr:Node, startNode:Node, var:str)->bool:
    if startNode == None:
        return False #wasn't found
    if (startNode.value[0]=='∀' or startNode.value[0]=='∃') and startNode.value[1]==var:
        return True
    return varInScope(expr, findParent(expr, startNode),var)

# the following new functions by Steve, checks via trees rather than strings
def noBadVars(myTree: Node, currNode=None) -> ProofResponse:
    if currNode==None:
        currNode = myTree # starting at root
    response = ProofResponse(is_valid=True) #default is True (i.e. no errs)
    leftResp = ProofResponse(is_valid=True) 
    rightResp = ProofResponse(is_valid=True) 
    if myTree==None or myTree.value=="": 
        return response
    if ((currNode.value[0]=='∀' or currNode.value[0]=='∃')  and (currNode.value[1] in OBJS)):
        response.is_valid=False
        response.err_msg = currNode.value[1]+" should not be quantified"
        return response
    if currNode.value[0] in PREDS and currNode.value[1] in VARS \
        and not varInScope(myTree, currNode, currNode.value[1]):
        response.is_valid=False
        response.err_msg = currNode.value[1]+" cannot be a free variable"
        return response
    if currNode.right !=None: #need to say this to prevent resetting to root
        rightResp = noBadVars(myTree,currNode.right)
    if currNode.left != None:
        leftResp = noBadVars(myTree, currNode.left )
    return rightResp if not rightResp.is_valid else leftResp

# this had flaws due to be string based, so much of it was cut
'''1
this section is INTENDED to prevent ∀x∈V(Px∧Qx) from becoming Pa∧Qx by ∀E.
HOWEVER, it is actually stopping ∀x∈V ∀x∈V Px from becoming ∀x∈V Px 
    # Make sure the bound variable does not appear in the expression with names
    for ch in expression_with_names:
        if ch == var:
            response = ProofResponse()
            response.err_msg = 'Variable "{}" on line {} should not appear on line {}'\
                .format(var, var_line_no, name_line_no)
            return response
2
    # Make sure the bound variable does not appear in the expression with names
    for ch in expression_with_names:
        if ch == var:
            response = ProofResponse()
            response.err_msg = 'Variable "{}" on line {} should not appear on line {}'\
                .format(var, var_line_no, name_line_no)
            return response

3
                # Make sure they all use the same name
    if len(names) > 1:
        for ch in names:
            if not ch == names[0]:
                response = ProofResponse()
                response.err_msg = 'All instances of variable "{}" on line {} should replace the same name on line {}'\
                    .format(var, var_line_no, name_line_no)
                return response
4
                    for ch in names:
        if not is_name(ch):
            response = ProofResponse()
            response.err_msg = 'Instances of variable "{}" on line {} should replace a name on line {}'\
                .format(var, var_line_no, name_line_no)
            return response

5-6
 for ch in names:
        if not is_name(ch):
            response = ProofResponse()
            response.err_msg = 'Instances of variable "{}" on line {} should replace a name on line {}'\
                .format(var, var_line_no, name_line_no)
            return response
    
    # Make sure they all use the same name
    if len(names) > 1:
        for ch in names:
            if not ch == names[0]:
                response = ProofResponse()
                response.err_msg = 'All instances of variable "{}" on line {} should replace the same name on line {}'\
                    .format(var, var_line_no, name_line_no)
                return response

7
                    for ch in vars:
        if not (ch == var):
            response = ProofResponse()
            response.err_msg = 'All instances of name "{}" on line {} should be replaced with the bound variable "{}" on line {}'\
                .format(name, name_line_no, var, var_line_no)
            return response
            '''
def verify_var_replaces_every_name(var_tree: Node, name_tree: Node, var: str, var_line_no: str, name_line_no: str):
    """
    Verify all instances of var in var_tree are replaced by a single name in name_tree AND
    that all instances of name in name_tree are replaced by var in var_tree
    """
    # If either node is empty, return valid

    if (var_tree == None or name_tree == None):
        response = ProofResponse
        response.is_valid = True
        return response

    # If both trees have a left node, check the left nodes (recursive)
    if (var_tree.left != None) and (name_tree.left != None):
        response = verify_var_replaces_every_name(var_tree.left, name_tree.left, var, var_line_no, name_line_no)
        if response.is_valid == False:
            return response

    # If both trees have a right node, check the right nodes (recursive)
    if (var_tree.right != None) and (name_tree.right != None):
        response = verify_var_replaces_every_name(var_tree.right, name_tree.right, var, var_line_no, name_line_no)
        if response.is_valid == False:
            return response

    index = 0
    var_indexes = []

    # Eliminate whitespace to make sure indexes match
    expression_with_vars = var_tree.value.replace(' ', '')
    expression_with_names = name_tree.value.replace(' ', '')

    # cut part goes here

     # Keep track of the locations (indexes) of the bound variable on current line
    for ch in expression_with_vars:
        if ch == var:
            var_indexes.append(index)
        index += 1

    # If there are no variables, stop here
    if len(var_indexes) == 0:
        response = ProofResponse()
        response.is_valid = True
        return response

    # Get the values at these locations in line m
    # Make sure they all represent names
    names = []
    for i in var_indexes:
        names.append(expression_with_names[i])
    
    # fourth cut goes here

    
    #third cut goes here


    
    # If there are no names, stop here
    if len(names) == 0:
        response = ProofResponse()
        response.is_valid = True
        return response        

    # Now, check that all instances of this name in line_m are replaced by the same (bound) var in current line
    name = names[0]
    index = 0
    name_indexes = []

    # Keep track of the locations (indexes) of the bound variable on current line
    for ch in expression_with_names:
        if ch == name:
            name_indexes.append(index)
        index += 1

    # Get the values at these locations in the current line
    # Make sure they all are replaced by the bound variable
    vars = []
    for i in name_indexes:
        vars.append(expression_with_vars[i])

#cut 7

    # TODO: use these instead of all those cuts which were based on Strings
    response = noBadVars(name_tree)
    return response

def verify_var_replaces_some_name(var_tree: Node, name_tree: Node, var: str, var_line_no: str, name_line_no: str, big=None):
    if big==None:
        big=name_tree
    """
    Verify that all instances of var in var_tree are replaced by a single name in name_tree
    """
    # If either node is empty, return valid
    if (var_tree == None or name_tree == None):
        response = ProofResponse
        response.is_valid = True
        return response

    # If both trees have a left node, check the left nodes (recursive)
    if (var_tree.left != None) and (name_tree.left != None):
        response = verify_var_replaces_some_name(var_tree.left, name_tree.left, var, var_line_no, name_line_no, big)
        if response.is_valid == False:
            return response

    # If both trees have a right node, check the right nodes (recursive)
    if (var_tree.right != None) and (name_tree.right != None):
        response = verify_var_replaces_some_name(var_tree.right, name_tree.right, var, var_line_no, name_line_no,big)
        if response.is_valid == False:
            return response

    index = 0
    var_indexes = []

    # Eliminate whitespace to make sure indexes match
    expression_with_vars = var_tree.value.replace(' ', '')
    expression_with_names = name_tree.value.replace(' ', '')

#2nd cut put goes here


    # Keep track of the locations (indexes) of the bound variable on current line
    for ch in expression_with_vars:
        if ch == var:
            var_indexes.append(index)
        index += 1

    # If there are no variables, stop here
    if len(var_indexes) == 0:
        response = ProofResponse()
        response.is_valid = True
        return response

    # Get the values at these locations in line m
    # Make sure they all represent names
    names = []
    for i in var_indexes:
        names.append(expression_with_names[i])
    
   # fifth/sixth cut here

    # If we reach this point, do Steve's new check
    response = noBadVars(big)
    return response