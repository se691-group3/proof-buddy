from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import make_tree
from .rule import Rule

class EqualityIntro(Rule):

    name = "Equality Introduction"
    symbols = "=I"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule =I
        (Equality Introduction)
        """
        response = ProofResponse()

        try:

            root_current = make_tree(current_line.expression, parser)

            # Verify the root operand is =
            if not root_current.value == '=':
                response.err_msg = "Error on line {}: The root operand of the expression should be identity (=)"\
                    .format(str(current_line.line_no))
                return response
            
            # Verify the left and right hand sides of the operand are equivalent
            if not root_current.left == root_current.right:
                response.err_msg = "Error on line {}: The left and right hand sides of the equation should be identical"\
                    .format(str(current_line.line_no))
                return response
            
            response.is_valid = True
            return response

        except:
            response.err_msg = "Error on line {}: Error in the expression {}"\
                .format(str(current_line.line_no), str(current_line.expression))
            return response
