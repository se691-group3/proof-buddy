from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line_nos, make_tree,\
    get_lines_in_subproof, verify_line_citation, get_expressions
from proofchecker.utils.binarytree import Node
from .rule import Rule

class ExcludedMiddle(Rule):

    name = "Law of Excluded Middle"
    symbols = "LEM"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule LEM i, j
        (Law of Excluded Middle)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find subproofs (i, j)
        try:
            target_line_nos = get_line_nos(rule)
            lines_i = get_lines_in_subproof(target_line_nos[0], proof)
            lines_j = get_lines_in_subproof(target_line_nos[1], proof)
            target_lines = [lines_i[0], lines_i[1], lines_j[0], lines_j[1]]

            # Verify that subproof citations are valid
            for line_no in target_line_nos:
                result = verify_line_citation(current_line.line_no, line_no)
                if result.is_valid == False:
                    return result

            # Search for lines i.1, i.x, j.1, j.x in the proof
            try:
                expressions = get_expressions(target_lines)
            
                # Create trees for expressions on lines i, j, k, and l
                root_i_1 = make_tree(expressions[0], parser)
                root_i_x = make_tree(expressions[1], parser)
                root_j_1 = make_tree(expressions[2], parser)
                root_j_x = make_tree(expressions[3], parser)
                root_current = make_tree(current_line.expression, parser)

                # Verify the expression on line i.1 is the negation of line j.1
                neg_i_1 = Node('¬')
                neg_i_1.right = root_i_1
                if (neg_i_1 != root_j_1):
                    response.err_msg = "Error on line {}: The expression on line {} should be the negation of line {}"\
                        .format(str(current_line.line_no), str(target_lines[2].line_no), str(target_lines[0].line_no))
                    return response

                # Verify the expressions on lines i.x and k.x are equivalent
                if root_i_x != root_j_x:
                    response.err_msg = "Error on line {}: The expressions on lines {} and {} should be equivalent"\
                        .format(str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[3].line_no))
                    return response

                # Verify the expressions on lines i.x and k.x are equivalent to current line
                if (root_i_x != root_current) or (root_j_x != root_current):
                    response.err_msg = "Error on line {}: The expressions on lines {} and {} should be equivalent to the expression on line {}"\
                        .format(str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[3].line_no), str(current_line.line_no))
                    return response

                response.is_valid = True
                return response
    
            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Law of Excluded Middle: LEM i, j"\
                    .format(str(current_line.line_no))
                return response        
        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Law of Excluded Middle: LEM i, j"\
                .format(str(current_line.line_no))
            return response
