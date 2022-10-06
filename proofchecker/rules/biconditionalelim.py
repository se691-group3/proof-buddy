from email import parser
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_lines, verify_line_citation, make_tree, get_expressions
from .rule import Rule

class BiconditionalElim(Rule):

    name = "Biconditional Elimination"
    symbols = "↔E"


    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify the rule ↔E m, n
        (Biconditional Elimination)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find lines (m, n) 
        try:
            target_lines = get_lines(rule, proof)

            # Verify that the line citations are valid
            for line in target_lines:
                result = verify_line_citation(current_line.line_no, line.line_no)
                if result.is_valid == False:
                    return result

            # Search for lines (m, n) in the proof
            try:
                expressions = get_expressions(target_lines)
                
                # Join the two expressions in a tree
                root_m = make_tree(expressions[0], parser)
                root_n = make_tree(expressions[1], parser)
                root_current = make_tree(current_line.expression, parser)

                # Confirm the root value of line m is ∧
                if (root_m.value != '↔'):
                    response.err_msg = "Error on line {}: The root operand should be ↔ when applying ↔E (currently the root operand is {})"\
                        .format(str(target_lines[0].line_no), str(root_m.value))
                    return response

                # Compare the trees
                if (root_n == root_m.left) or (root_n == root_m.right):
                    if (root_current == root_m.left) or (root_current == root_m.right):
                        if (root_m.left == root_m.right) or (root_n != root_current):
                            response.is_valid = True
                            return response
                        else:
                            response.err_msg = "Error on line {}: The expressions on lines {} and {} do not represent both the left and right side of the expression on line {}"\
                                .format(str(current_line.line_no), str(target_lines[1].line_no), str(current_line.line_no), str(target_lines[0].line_no))
                            return response
                    else:
                        response.err_msg = "Error on line {}: The expression on line {} does not represent the left or right side of the expression on line {}"\
                            .format(str(current_line.line_no), str(current_line.line_no), str(target_lines[0].line_no))
                        return response
                else:
                    response.err_msg = "Error on line {}: The expression on line {} does not represent the left or right side of the expression on line {}"\
                        .format(str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[0].line_no))
                    return response
            
            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Biconditional Elimination: ↔E m, n"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule is not formatted properly.  Biconditional Elimination: ↔E m, n"\
                .format(str(current_line.line_no))
            return response
