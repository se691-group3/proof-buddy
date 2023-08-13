from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line, verify_line_citation, make_tree, verify_same_structure_FOL, \
    verify_var_replaces_some_name, nonVarFound, freeSubst
from proofchecker.utils.binarytree import tree2Str #used for testing
from .rule import Rule
from proofchecker.proofs.exprMethods import instanceOf

class UniversalElim(Rule):

    name = "Universal Elimination"
    symbols = "∀E"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ∀E m
        (Universal Elimination)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find line m
        try:
            target_line = get_line(rule, proof)

            # Verify if line citation is valid
            result = verify_line_citation(current_line.line_no, target_line.line_no)
            if result.is_valid == False:
                return result

            try: 
                root_m = make_tree(target_line.expression, parser)
                current = make_tree(current_line.expression, parser)

                # Verify root operand of line m is ∀
                if (root_m.value[0] != '∀'):
                    response.err_msg = "Error on line {}: The quantifier of line {} should be the universal quantifier (∀)"\
                        .format(str(current_line.line_no), str(target_line.line_no))
                    return response
                
                # Verify that root_m.right and current have same stucture
                result = verify_same_structure_FOL(root_m.right, current, target_line.line_no, current_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # Verify that all instances of the bound variable in root_m.right
                # are replaced by the same name in current
                var = root_m.value[1]
                result = verify_var_replaces_some_name(root_m.right, current, var, target_line.line_no, current_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # new addition goes here (this probably makes much of the checks above redundant)
                env = {} # initializing the environment of checking instances
                result = instanceOf(root_m.right, current, env, True) #taking right since just want expression underneath quantifier. note: true = FOL
                # need to check that no OTHER bound variable got replaced too, other than the desired one: [SteveE added this]
                if result[0] and nonVarFound(result[1],var):
                    response.err_msg = "Error on line {}: only the variable {} from line {} may be substituted"\
                    .format(str(current_line.line_no), var, str(target_line.line_no))
                    return response
                if result[0] and var in result[1].keys() and not freeSubst(result[1],var):
                    response.err_msg = "Error on line {}: the bound variable {} from line {} should be replaced by a free variable"\
                    .format(str(current_line.line_no), var, str(target_line.line_no))
                    return response
                if not result[0]: 
                    response.err_msg = "Error on line {}: single substitutions on line {} do not match current line"\
                    .format(str(current_line.line_no), str(target_line.line_no))
                    return response
                
                response.is_valid = True
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Universal Elimination: ∀E m"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Universal Elimination: ∀E m"\
                .format(str(current_line.line_no))
            return response