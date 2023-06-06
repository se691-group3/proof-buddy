from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line_nos, get_lines_in_subproof, verify_line_citation, make_tree, get_expressions
from .rule import Rule

class BiconditionalIntro(Rule):

    name = "Biconditional Introduction"
    symbols = "↔I"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify the rule ↔I i, j
        (Biconditional Introduction)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find lines in subproofs i and j
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

            # Search for lines i.1, i.x, j.1, and j.x in the proof
            try:
                expressions = get_expressions(target_lines)

                # Create trees for expressions on lines i.1, i.x, j.1, and j.x
                root_i_1 = make_tree(expressions[0], parser)
                root_i_x = make_tree(expressions[1], parser)
                root_j_1 = make_tree(expressions[2], parser)
                root_j_x = make_tree(expressions[3], parser)
                root_current = make_tree(current_line.expression, parser)

                # make sure it has proper connective (this was missing originally!)
                if root_current==None or root_current.value==None or root_current.value=="" or root_current.value[0]!="↔":
                      response.err_msg = "Error on line {}: the given expression was not an implication"\
                    .format(str(current_line.line_no))
                      return response
                
                # this True check is premature! needed to check connective first (inserted above)
                # Verify lines i.1 and j.x are equivalent
                if root_i_1 == root_j_x:
                    # Verify that lines i.x and j.1 are equivalent
                    if root_i_x == root_j_1:
                        # If i.1 and i.x are equivalent, the left and right hand sides
                        # of the biconditional on the current line should also be equivalent
                        if root_i_1==root_i_x:
                            if (root_current.left == root_i_1) and (root_current.left == root_current.right):
                                response.is_valid = True
                                return response
                            else:
                                response.err_msg = "Error on line {}: Invalid introduction on line {}"\
                                    .format(str(current_line.line_no), str(current_line.line_no))
                                return response

                        else:
                            # If i.1 and i.x are not equivalent, the left side of the current line should equal i.1 or i.x,
                            # and the right side of the current line should equal i.1 or i.x,
                            # and the left side should not be the same as the right side
                            if (root_current.left == root_i_1) or (root_current.left == root_i_x):
                                if (root_current.right == root_i_1) or (root_current.right == root_i_x):
                                    if root_current.left != root_current.right:
                                        response.is_valid = True
                                        return response
                                    else:
                                        response.err_msg = "Error on line {}: Left side and right side of line {} are equivalent, but lines {} and {} are not equivalent"\
                                            .format(str(current_line.line_no), str(current_line.line_no), str(target_lines[0].line_no), str(target_lines[1].line_no))
                                        return response
                                else:
                                        response.err_msg = "Error on line {}: Right side of line {} does not equal either of the expressions on lines {} and {}"\
                                            .format(str(current_line.line_no), str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[3].line_no))
                                        return response
                            else:
                                    response.err_msg = "Error on line {}: Left side of line {} does not equal either of the expressions on lines {} and {}"\
                                        .format(str(current_line.line_no), str(current_line.line_no), str(target_lines[1].line_no), str(target_lines[3].line_no))
                                    return response
                    else:
                        response.err_msg = "Error on line {}: The expressions on lines {} and {} are not equivalent"\
                            .format(str(current_line.line_no), str(target_lines[1].line_no),str(target_lines[2].line_no))
                        return response
                else:
                    response.err_msg = "Error on line {}: The expressions on lines {} and {} are not equivalent"\
                        .format(str(current_line.line_no), str(target_lines[0].line_no),str(target_lines[3].line_no))
                    return response
            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  ↔I i, j"\
                    .format(str(current_line.line_no))
                return response        
        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  ↔I i, j"\
                .format(str(current_line.line_no))
            return response
