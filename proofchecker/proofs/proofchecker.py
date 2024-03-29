from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse, loadJson
from proofchecker.proofs.proofutils import fix_rule_whitespace_issues, make_tree, is_conclusion, depth, clean_rule
from proofchecker.rules.rulechecker import RuleChecker
#from proofchecker.utils.binarytree import tree2Str #only used for testing
from proofchecker.utils.constants import Constants
from proofchecker.utils.tfllexer import IllegalCharacterError
#from proofchecker.proofs.exprMethods import myMakeTree, instanceOf #no longer needed for this file
from proofchecker.rules.newrule import NewRule #purely for testing
from proofchecker.models import Proof
from proofchecker.proofs.ERtests import * # for testing
# testing git
# print(loadJson("ds")) ; used for demo

TESTCOUNT, TREELIST = -1, [] #just for testing

def verify_proof(proof: ProofObj, parser):
    global TESTCOUNT, TREELIST

    if TESTCOUNT==-2: #i.e. skipping this for now
        #the lines below are just for testing
        
        TESTCOUNT += 1
        testNodes = [[0],[]]
        TREELIST = treeTest2(TREELIST, testNodes[TESTCOUNT])
        print(TESTCOUNT)
        for x in TREELIST:
            print(x)
    else:
        replaceTest()

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
        response = verify_rule(line, proof, parser) 
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
   
    elif isinstance(rule, NewRule): #only runs if the newRule is returned
        #check to see if database has lemma saved for this user
        try:
            lemmaObjectFromDatabase = Proof.objects.get(created_by = proof.created_by, name = rule_symbols)
            
            if (not lemmaObjectFromDatabase.complete):
                response = ProofResponse()
                response.err_msg = 'Rule "{}" on line {} not valid since it has not yet been proven.'\
                    .format(rule_symbols, str(current_line.line_no))
                return response
            if ('derived' in lemmaObjectFromDatabase.rules) and ('derived' not in proof.rules):
                response = ProofResponse()
                response.err_msg = 'Rule "{}" on line {} not valid since since it was proven using derived rules. Derived are not allowed in current proof.'\
                    .format(rule_symbols, str(current_line.line_no))
                return response
            else:
                return rule.verify(current_line, proof, parser)
        except Proof.DoesNotExist:
            response = ProofResponse()
            response.err_msg = 'Rule "{}" on line {} not valid since it has not yet been proven and/or saved.'\
                .format(rule_symbols, str(current_line.line_no))
            return response   
        except Proof.MultipleObjectsReturned:
            response = ProofResponse()
            response.err_msg = 'There is more than 1 version of rule "{}" on line {} currenly saved in your profile. Please ensure there is only 1 valid and complete proof saved.'\
                .format(rule_symbols, str(current_line.line_no))
            return response  

    else:
        return rule.verify(current_line, proof, parser)