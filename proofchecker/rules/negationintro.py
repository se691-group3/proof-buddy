from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, make_tree, get_line_no, get_lines_in_subproof, verify_line_citation, get_expressions
from .rule import Rule

class NegationIntro(Rule):

    name = "Negation Introduction"
    symbols = "¬I"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ¬I m
        (Negation Introduction)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find lines (i-j)
        try:
            target_line_no = get_line_no(rule)
            target_lines = get_lines_in_subproof(target_line_no, proof)

            # Verify the line citation is valid            
            result = verify_line_citation(current_line.line_no, target_line_no)
            if result.is_valid == False:
                return result

            # Search for lines i-j in the proof
            try:
                expressions = get_expressions(target_lines)

                # Create trees from the expressions on lines i-j
                root_i = make_tree(expressions[0], parser)
                root_j = make_tree(expressions[1], parser)

                # Create a tree from the expression on the current_line
                root_current = make_tree(current_line.expression, parser)

                # Verify current line is the negation of line i
                if (root_current.value == '¬') and (root_current.right == root_i):
                    
                    # Verify line j is a contradiction
                    if (root_j.value == '⊥') or (root_j.value.casefold() == 'false'):
                        response.is_valid = True
                        return response
                    else:
                        response.err_msg = "Error on line {}: Line {} should be '⊥' (Contradiction)"\
                            .format(str(current_line.line_no), str(target_lines[1].line_no))
                        return response

                else:
                    response.err_msg = "Error on line {}: Line {} is not the negation of line {}"\
                        .format(str(current_line.line_no), str(current_line.line_no),str(target_lines[0].line_no))
                    return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Negation Introduction: ¬I m"\
                    .format(str(current_line.line_no))
                return response        

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Negation Introduction: ¬I m"\
                .format(str(current_line.line_no))
            return response