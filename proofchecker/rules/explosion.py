from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line, verify_line_citation, make_tree
from .rule import Rule

class Explosion(Rule):

    name = "Explosion"
    symbols = "X"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule X m
        (Explosion)
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
                root = make_tree(expression, parser)

                # Verify line j is a contradiction
                if (root.value == '⊥') or (root.value.casefold() == 'false'):
                    response.is_valid = True
                    return response
                else:
                    response.err_msg = "Error on line {}: Line {} should be '⊥' (Contradiction)"\
                        .format(str(current_line.line_no), str(target_line.line_no))
                    return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Explosion: X m"\
                    .format(str(current_line.line_no))
                return response      

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Explosion: X m"\
                .format(str(current_line.line_no))
            return response 