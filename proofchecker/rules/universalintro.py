from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, find_c, get_citable_lines, get_line, verify_line_citation, \
    make_tree, verify_same_structure_FOL, verify_var_replaces_every_name
from .rule import Rule

class UniversalIntro(Rule):

    name = "Universal Introduction"
    symbols = "∀I"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule ∀I m
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

                # Verify root operand of current line is ∀
                if (current.value[0] != '∀'):
                    response.err_msg = "Error on line {}: The root operand of line {} should be the universal quantifier (∀)"\
                        .format(str(current_line.line_no), str(target_line.line_no))
                    return response
                
                # Verify that line m and current.right have same stucture
                result = verify_same_structure_FOL(root_m, current.right, target_line.line_no, current_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # Verify that all instances of the bound variable in currnent.right
                # are replaced by the same name in line m
                var = current.value[1]
                result = verify_var_replaces_every_name(current.right, root_m, var, current_line.line_no, target_line.line_no)
                if result.is_valid == False:
                    result.err_msg = 'Error on line {}: '.format(current_line.line_no) + result.err_msg
                    return result

                # TODO: Verify that the name represents a "generic free variable"
                c = find_c(current.right, root_m, var)
                citable_lines = get_citable_lines(current_line, proof)
                if len(citable_lines) > 0:
                    citable_lines_with_c = []
                    for line in citable_lines:
                        if c in line.expression:
                            citable_lines_with_c.append(line)
                    if len(citable_lines_with_c) > 0:
                        if (citable_lines_with_c[0].rule.casefold() == 'Premise'.casefold()) or \
                            (citable_lines_with_c[0].rule.casefold() == 'Assumption'.casefold()) or \
                            (citable_lines_with_c[0].rule.casefold() == 'Assumpt'.casefold()):
                            response.err_msg = 'Error on line {}: The name "{}" on line {} must be a generic free variable'\
                                .format(current_line.line_no, c, target_line.line_no)
                            return response

                response.is_valid = True
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Universal Introduction: ∀I m"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Universal Introduction: ∀I m"\
                .format(str(current_line.line_no))
            return response
            