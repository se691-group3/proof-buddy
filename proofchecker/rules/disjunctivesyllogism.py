from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_lines, verify_line_citation, \
    make_tree, get_expressions
from .rule import Rule

class DisjunctiveSyllogism(Rule):

    name = "Disjunctive Syllogism"
    symbols = "DS"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule DS m, n
        (Disjunctive Syllogism)
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
                
                # Create trees for lines m and n
                root_m = make_tree(expressions[0], parser)
                root_n = make_tree(expressions[1], parser)

                # Create a tree for current line
                root_current = make_tree(current_line.expression, parser)

                # Line m should be a disjunction
                if root_m.value != '∨':
                    response.err_msg = "Error on line {}: The root of line {} should be a disjunction (∨) when applying disjunctive syllogism"\
                        .format(str(current_line.line_no), str(target_lines[0].line_no))
                    return response

                # Line n should be a negation
                if root_n.value != '¬':
                    response.err_msg = "Error on line {}: The root of line {} should be a negation (¬) when applying disjunctive syllogism"\
                        .format(str(current_line.line_no), str(target_lines[1].line_no))
                    return response

                try:
                    # Line n should be the negation of the left or right of line m
                    if (root_n.right != root_m.left) and (root_n.right != root_m.right):
                        response.err_msg = "Error on line {}: Line {} should be the negation of either the left or right half of line {}"\
                            .format(str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[0].line_no))
                        return response
                    
                    # The current line should be equivalent to either the left or right of line m
                    if (root_current != root_m.left) and (root_current != root_m.right):
                        response.err_msg = "Error on line {}: Line {} should be equivalent to either the left or right half of line {}"\
                            .format(str(current_line.line_no), str(current_line.line_no), str(target_lines[0].line_no))
                        return response

                    # The atomic sentence on the current line should not be the same as line n
                    if (root_current == root_n.right):
                        response.err_msg = "Error on line {}: Line {} and line {} should not represent the same half of the disjunction on line {}"\
                            .format(str(current_line.line_no), str(target_lines[1].line_no), str(current_line.line_no), str(target_lines[0].line_no))
                        return response

                except: 
                    response.err_msg = "Error on line {}: Atomic sentences are not specified correctly on line {} or line {}"\
                        .format(str(current_line.line_no), str(target_lines[0].line_no), str(target_lines[1].line_no))
                    return response

                response.is_valid = True
                return response
            
            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Disjunctive Syllogism: DS m, n"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Disjunctive Syllogism: DS m, n"\
                .format(str(current_line.line_no))
            return response