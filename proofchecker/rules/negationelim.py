from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, make_tree, get_lines, verify_line_citation, get_expressions
from .rule import Rule

class NegationElim(Rule):

    name = "Negation Elimination"
    symbols = "¬E"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ¬E m, n
        (Negation Elimination)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find lines (m, n)
        try:
            target_lines = get_lines(rule, proof)

            # Verify that line citations are valid
            for line in target_lines:
                result = verify_line_citation(current_line.line_no, line.line_no)
                if result.is_valid == False:
                    return result

            # Search for lines (m, n) in the proof
            try:
                expressions = get_expressions(target_lines)

                # Create trees from the expressions on lines (m, n)
                root_m = make_tree(expressions[0], parser)
                root_n = make_tree(expressions[1], parser)

                # Create a tree from the expression on the current_line
                root_current = make_tree(current_line.expression, parser)

                # Verify m is the negation of n
                if (root_m.value == '¬') and (root_m.right == root_n):
                    
                    # Verify current line is a contradiction
                    if (root_current.value == '⊥') or (root_current.value.casefold() == 'false'):
                        response.is_valid = True
                        return response
                    else:
                        response.err_msg = "Error on line {}: Line {} should be '⊥' (Contradiction)"\
                            .format(str(current_line.line_no), str(current_line.line_no))
                        return response

                else:
                    response.err_msg = "Error on line {}: Line {} is not the negation of line {}"\
                        .format(str(current_line.line_no), str(target_lines[0].line_no),str(target_lines[1].line_no))
                    return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Negation Elimination: ¬E m, n"\
                    .format(str(current_line.line_no))
                return response        

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Negation Elimination: ¬E m, n"\
                .format(str(current_line.line_no))
            return response