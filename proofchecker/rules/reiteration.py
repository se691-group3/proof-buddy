from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line, verify_line_citation, make_tree
from .rule import Rule

class Reiteration(Rule):

    name = "Reiteration"
    symbols = "R"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule R m
        (Reiteration)
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

                # Verify line m and current line are equivalent
                if (root_m == current):
                    response.is_valid = True
                    return response
                else:
                    response.err_msg = "Error on line {}: Lines {} and {} are not equivalent"\
                        .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                    return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Reiteration: R m"\
                    .format(str(current_line.line_no))
                return response      

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Reiteration: R m"\
                .format(str(current_line.line_no))
            return response 