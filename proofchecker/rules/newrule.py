import copy
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse, loadJson #yellow=static method, blue is class
from proofchecker.proofs.exprMethods import instanceOf #no longer need myMakeTree
from proofchecker.proofs.proofutils import clean_rule, fix_rule_whitespace_issues, get_lines, get_premises, verify_line_citation, make_tree, get_expressions, get_line_nos
from proofchecker.utils.binarytree import Node #no longer need tree2Str
# from proofchecker.proofs.proofchecker import verify_proof #CIRCULAR = verifying a rule requires verifying a proof but verifying a proof must verify rules
# from proofchecker.utils import tflparser # no longer need parser?
from .rule import Rule
from proofchecker.models import Proof

 # in next version, this will look for a file in the student or teacher directory named "new rule" (or with the given name),
 # but instead of loading it from the database and/or a parsed JSON file, for this version we will hardcode in the rule
 # note that due to the current non-recursive implementation of verify_proof (which depends on verify_rule), we must assume this proof is valid

''' UNCOMMENT THIS FOR DEMO PART1
this section correctly creates a proof object and saves it as a json file
rawProof = [['1', 'A', 'Premise'], ['2.1', '¬A', 'Assumption'], ['2.2', '⊥', '¬E 2.1, 1'], ['3', '¬¬A', '¬I 2']]
myLines = [ProofLineObj(x[0],x[1],x[2]) for x in rawProof]
myProof = ProofObj(rules='tfl_basic', lines=myLines, conclusion = myLines[-1], created_by='Steve', name="New Rule") #will have to read in permitted rules list
myProof.complete = True
for x in range(myProof.numPremises()):
    myProof.premises.append(myLines[x]) #just needed since we are hard-coding this. normally this would be read from file
myProof.saveJson() # this correctly made a json file!
'''

''' UNCOMMENT THIS FOR DEMO PART2
this section correctly imports a json file to a proof object
testProof = loadJson("NewRule")
print(testProof) #testing if dictionary was created properly. note that it does the unicode correctly!
'''

class NewRule(Rule):

    #name = "New Rule" # this would be the name of the proof
    #symbols = "NR"    # most likely a name of the proof without spaces? 

    #def test():  #just for testing
     #   global myProof
      #  return myProof.numPremises()

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        #global myProof # in future version, this will be read-in as the appropriate new rule proof

        """
        Verify proper implementation of the new rule
        (assumes it has read in a name of "new rule") 
        """
        rule_str = clean_rule(current_line.rule)
        fixed_rule = fix_rule_whitespace_issues(rule_str)
        rule_symbols = fixed_rule.split()[0]
        

        response = ProofResponse() #default .isvalid=False
        proof.complete = False # since they must have made a change, resetting to the default (also done in old proofchecker.py/verify_rule)

        #retrives proof refernced by user as lemma from user's saved proofs in the database, by querying based on the "created_by" and "name" field. 
        # Current proof has the user listed in the created_by field
        
        current_user = proof.created_by

        query_set_return = Proof.objects.filter(created_by = current_user, name = rule_symbols)
       

        for element in query_set_return:
            userProofToBeUsedAsLemma = element


        lemmaProof = ProofObj()
        lemmaProof.name = userProofToBeUsedAsLemma.name
        lemmaProof.premises = userProofToBeUsedAsLemma.premises
        lemmaProof.conclusion = userProofToBeUsedAsLemma.conclusion

        #at this point, lemmaProof object should contain name, presmises and conclusion field, which shoudld allow below code to execute

        
        #myProof = loadJson(rule[:rule.find(" ")].casefold()) #commenting out local referene and replacing below with proof obj created from database info
        
        
        myProof = copy.copy(lemmaProof)

        # testing print(current_line.line_no, current_line.expression,current_line.rule, response.err_msg, response.is_valid)   
        #cannot do: result = verify_proof(proof, tflparser.parser) because of dependency issues

        # Attempt to find line m
        target_line_nos = get_line_nos(rule_str) #this gets a list of strings of the cited lines for the rule
        #print("target line nos= ",target_line_nos)
        n, m  = len(target_line_nos), len(get_premises(myProof.premises)) #numPremises() function won't work since we aren't brining in the entire proof line by line. We are only brining in the premises comma or colon separated
    
        if n != m:
            response.err_msg = "Error on line {}: {} requires {} citation(s), but you provided {}"\
                    .format(str(current_line.line_no), myProof.name, str(m), str(n))
            return response
        target_lines = get_lines(rule_str, proof) #this gets their corresponding lineObjects
    
        # from this point on, we know # premises in myProof.premises = # citations in target_lines

        # Verify that line citations are valid
        for line_no in target_line_nos:
            result = verify_line_citation(current_line.line_no, line_no)
            if result.is_valid == False:
                return result

            # Search for line m in the proof
        expressions = get_expressions(target_lines) # gets list of expressions of target lines  
        

        trees_cited = [make_tree(x, parser) for x in expressions] # gets list of trees of those expressions, needed for instanceOf
        
        trees_orig = [make_tree(x,parser) for x in get_premises(myProof.premises)] # gets list of trees of representing premises of new rule
        env = {} # initializing the environment of checking instances
        for i in range(n): # this is the number of premises/citations (already verified to be equal) to check pattern matching of each
            result = instanceOf(trees_orig[i], trees_cited[i], env)
            if result[0]: 
                env = result[1] #updating the environment between premises
            else:
                response.err_msg = "Error on line {}: citation of line {} does not match premise #{} for rule {}"\
                .format(str(current_line.line_no), target_line_nos[i], str(n+1), myProof.name)
                return response
        result = instanceOf(make_tree(myProof.conclusion, parser), make_tree(current_line.expression, parser), env) # checking application of rule
        if result[0]: 
            response.is_valid = True 
        else:
            response.err_msg = "Error on line {}: this expression does not match conclusion for rule {}"\
            .format(str(current_line.line_no), myProof.name)
        return response
            
            # TODO: still need to check if new rule is permitted in current proof through ruleList