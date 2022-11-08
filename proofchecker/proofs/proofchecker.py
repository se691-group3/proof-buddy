from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse, loadJson
from proofchecker.proofs.proofutils import fix_rule_whitespace_issues, make_tree, is_conclusion, depth, clean_rule
from proofchecker.rules.rulechecker import RuleChecker
from proofchecker.utils.binarytree import tree2Str #only used for testing
from proofchecker.utils.constants import Constants
from proofchecker.utils.tfllexer import IllegalCharacterError
from proofchecker.proofs.exprMethods import myMakeTree, instanceOf #no longer needed for this file
from proofchecker.rules.newrule import NewRule #purely for testing

# print(loadJson("ds")) ; used for demo

def verify_proof(proof: ProofObj, parser):
    '''
    ****  FOR DEMO: PUT IN THE NAME OF THE RULE/PROOF HERE:
    
    proof.name = "example1" # example#1 will be for Disjunctive Syllogism

    
    Verify if a proof is valid, line by line.  
    Returns a ProofResponse, which contains an error message if invalid
    '''
    response = ProofResponse()

    #want to test FOL trees
    # print("as string:", tree2Str(myMakeTree(proof.lines[-1].getExpr(),1)))


    if proof.complete: # checking if proof has already been validated previously. Note: as soon as ANY edits made, must change this to False!
        response.is_valid=True
        return response

    if len(proof.lines) == 0:
        response.err_msg = "Cannot validate a proof with no lines"
        return response

    for line in proof.lines:

        # Verify the line has a line number
        if not line.line_no:
            response.err_msg = "One or more lines is missing a line number"
            return response

        # Verify the line has an expression
        if (not line.expression) or (line.expression == ''):
            response.err_msg = "No expression on line {}"\
                .format(str(line.line_no))
            return response

        # Verify the expression is valid
        try:
            make_tree(line.expression, parser)
        except IllegalCharacterError as char_err:
            response.err_msg = "{} on line {}"\
                .format(char_err.message, str(line.line_no))
            return response 
        except:
            response.err_msg = 'Syntax error on line {}.  Expression "{}" does not conform to ruleset "{}"'\
                .format(str(line.line_no), line.expression, Constants.RULES_CHOICES.get(proof.rules))
            return response

        # Verify the rule is valid
        response = verify_rule(line, proof, parser) #BUG = this is returning None
        if not response.is_valid:
            return response

### adding prints here
        #print(line.line_no, tree2Str(make_tree(line.expression, parser)))

    last_line = proof.lines[len(proof.lines)-1]
    conclusion = is_conclusion(last_line, proof, parser)
    response.is_valid = True

    # If the last line is the desired conclusion, it is a full and complete proof
    if conclusion:
        if (last_line.rule.casefold() == 'assumption') or (last_line.rule.casefold() == 'assumpt'):
            response.err_msg = "Proof cannot be concluded with an assumption"
            return response            
        elif depth(last_line.line_no) > 1:
            response.err_msg = "Proof cannot be concluded within a subproof"
            return response
        else: # DO THIS NEXT BLOCK ONLY WHEN PROOF IS FULLY COMPLETE
            response.is_valid = True
            proof.complete = True      # new attrib to save time of rechecking (hopefully this is the only case of a completed proof!)
            proof.saveJson()
            return response

    # If not, the proof is incomplete
    else:
        response.is_valid = True
        response.err_msg = "All lines are valid, but the proof is incomplete"
        return response


def verify_rule(current_line: ProofLineObj, proof: ProofObj, parser):
    """
    Determines what rule is being applied, then calls the appropriate
    function to verify the rule is applied correctly
    """
    proof.complete = False # since they must have made a change, resetting to the default (also done in newrule.py)
    rule_str = clean_rule(current_line.rule)
    fixed_rule = fix_rule_whitespace_issues(rule_str)
    rule_symbols = fixed_rule.split()[0]
    rule_checker = RuleChecker()
    rule = rule_checker.get_rule(rule_symbols, proof)

    if rule == None:
        response = ProofResponse()
        response.err_msg = 'Rule "{}" on line {} not found in ruleset "{}"'\
            .format(rule_symbols, str(current_line.line_no), Constants.RULES_CHOICES.get(proof.rules))
        return response     
    else:
        return rule.verify(current_line, proof, parser)