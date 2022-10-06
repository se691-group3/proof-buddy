from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import make_tree
from .rule import Rule

class Premise(Rule):

    name = "Premise"
    symbols = "Premise"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify that "premise" is valid justification for a line
        """
        response = ProofResponse()
        try:
            current_exp = current_line.expression
            current = make_tree(current_exp, parser)

            # If there is only one premise
            if isinstance(proof.premises, str):
                if make_tree(proof.premises, parser) == current:
                    response.is_valid = True
                    return response
                else:
                    response.err_msg = "Error on line {}: Expression on line {} is not a premise"\
                        .format(str(current_line.line_no), str(current_line.line_no))
                    return response                

            # If multiple expressions, search for the premise
            for premise in proof.premises:
                if make_tree(premise, parser) == current:
                    response.is_valid = True
                    return response
        
            # If not found, invalid
            response.err_msg = "Error on line {}: Expression on line {} not found in premises"\
                .format(str(current_line.line_no), str(current_line.line_no))
            return response

        except:
            response.err_msg = "Error on line {}: One or more premises is invalid"\
                .format(str(current_line.line_no))
            return response