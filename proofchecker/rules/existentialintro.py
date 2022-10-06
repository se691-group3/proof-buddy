from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line, verify_line_citation, make_tree, \
    verify_same_structure_FOL, verify_var_replaces_some_name
from .rule import Rule

class ExistentialIntro(Rule):

    name = "Existential Introduction"
    symbols = "∃I"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ∃I m
        (Existential Introduction)
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
                expression = target_line.expression
                root_m = make_tree(expression, parser)
                current = make_tree(current_line.expression, parser)

                # Verify root operand of current line is ∃
                if (current.value[0] != '∃'):
                    response.err_msg = "Error on line {}: The root operand of line {} should be the existential quantifier (∃)"\
                        .format(str(current_line.line_no), str(target_line.line_no))
                    return response
                
                # Verify that root_m and current.right have same stucture
                result = verify_same_structure_FOL(root_m, current.right, target_line.line_no, current_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # Verify that all instances of the bound variable in current.right
                # are replaced by the same name in root_m
                var = current.value[1]
                result = verify_var_replaces_some_name(current.right, root_m, var, current_line.line_no, target_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                response.is_valid = True
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Existential Introduction: ∃I m"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Existential Introduction: ∃I m"\
                .format(str(current_line.line_no))
            return response
