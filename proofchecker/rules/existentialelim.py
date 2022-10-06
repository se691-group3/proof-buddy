from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, find_c, get_citable_lines, get_line_nos, get_line_with_line_no, get_lines_in_subproof, \
    get_expressions, verify_line_citation, verify_line_citation, make_tree, is_name, is_var, verify_same_structure_FOL, \
    verify_var_replaces_some_name
from .rule import Rule

class ExistentialElim(Rule):

    name = "Existential Elimination"
    symbols = "∃E"
    
    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ∃E m, i
        (Existential Elimination)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find line m
        try:
            target_line_nos = get_line_nos(rule)
            line_m = get_line_with_line_no(target_line_nos[0], proof)
            lines_i = get_lines_in_subproof(target_line_nos[1], proof)
            target_lines = [line_m, lines_i[0], lines_i[1]]

            # Verify that line citations are valid
            for line_no in target_line_nos:
                result = verify_line_citation(current_line.line_no, line_no)
                if result.is_valid == False:
                    return result

            # Search for lines m, i.1, i.x
            try:
                expressions = get_expressions(target_lines)
                root_m = make_tree(expressions[0], parser)
                root_i_1 = make_tree(expressions[1], parser)
                root_i_x = make_tree(expressions[2], parser)
                root_current = make_tree(current_line.expression, parser)

                # Verify root operand of line m is ∃
                if (root_m.value[0] != '∃'):
                    response.err_msg = "Error on line {}: The root operand of line {} should be the existential quantifier (∃)"\
                        .format(str(current_line.line_no), str(target_lines[0].line_no))
                    return response
                
                # Verify that root_m.right and root_i_1 have same stucture
                result = verify_same_structure_FOL(root_m.right, root_i_1, target_line_nos[0], (target_line_nos[1] + ".1"))
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # Verify that all instances of the bound variable in root_m.right
                # are replaced by the same name in root_i_1
                var = root_m.value[1]
                result = verify_var_replaces_some_name(root_m.right, root_i_1, var, target_line_nos[0], (target_line_nos[1] + ".1"))
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # Verify that root_i_x and current are equivalent
                if not root_i_x == root_current:
                    response.err_msg = "Error on line {}: The expressions on line {} and line {} should be equivalent"\
                        .format(str(current_line.line_no), str(target_lines[2].line_no), str(current_line.line_no))
                    return response

                # Verify that 'c' (on line i_1) does not appear earlier in the proof
                c = find_c(root_m.right, root_i_1, var)
                citable_lines = get_citable_lines(lines_i[0], proof)
                for line in citable_lines:
                    if c in line.expression:
                        response.err_msg = 'Error on line {}: The name "{}" on line {} should not appear earlier in the proof (it appears on line {})'\
                            .format(current_line.line_no, c, lines_i[0].line_no, line.line_no)
                        return response

                # Verify that 'B' does not contain 'c'
                if c in current_line.expression:
                    response.err_msg = 'Error on line {}: The name "{}" on line {} should not appear on line {}'\
                        .format(current_line.line_no, c, lines_i[0].line_no, current_line.line_no)
                    return response

                response.is_valid = True
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Existential Elimination: ∃E m"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Existential Elimination: ∃E m"\
                .format(str(current_line.line_no))
            return response