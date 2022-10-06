from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_lines, verify_line_citation, make_tree, get_expressions
from proofchecker.utils.binarytree import Node
from .rule import Rule

class EqualityElim(Rule):

    name = "Equality Elimination"
    symbols = "=E"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule =E m, n
        (Equality Elimination)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find lines m, n
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
                root_m = make_tree(expressions[0], parser)
                root_n = make_tree(expressions[1], parser)
                root_current = make_tree(current_line.expression, parser)

                # Verify the root operand on line m is =
                if not root_m.value == '=':
                    response.err_msg = "Error on line {}: The root operand of the expression should be identity (=)"\
                        .format(str(target_lines[0].line_no))
                    return response

                left = root_m.left.value
                right = root_m.right.value

                response = check_subs(root_current, root_n, left, right, current_line, target_lines[1])
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Equality Elimination: =E m, n"\
                    .format(str(current_line.line_no))
                return response

        except:
            response.err_msg = "Error on line {}: Error in the expression {}"\
                .format(str(current_line.line_no), str(current_line.expression))
            return response


def check_subs(current_tree: Node, line_n_tree: Node, left: str, right: str, current_line: ProofLineObj, line_n: ProofLineObj):
    """
    Test to determine that current_tree follows from line n by replacing a certian subset of a's with b's
    """
    
    # Check if the current_tree node is equivalent to the line_n tree node
    if not ((current_tree.value == line_n_tree.value) or (current_tree.value == left) or (current_tree.value == line_n_tree.right)):

        # Check whether they are equivalent length
        current_clean = current_tree.value.replace(" ", "")
        line_n_clean = line_n_tree.value.replace(" ", "")

        if not len(current_clean) == len(line_n_clean):
            response = ProofResponse()
            response.err_msg = "Error on line {}: Expressions on lines {} and {} should have similar structure"\
                .format(current_line.line_no, line_n.line_no, current_line.line_no)
            return response

        # Check whether they are equivalent by swapping 'left' with 'right'
        side = left
        x = 0
        while x < len(current_clean):
            if not ((current_clean[x] == line_n_clean[x]) or (current_clean[x] == side)):
                if side == left:
                    side = right
                    continue 
                response = ProofResponse()
                response.err_msg = 'Error on line {}: Expression "{}" cannot be achieved by replacing "{}" with "{}" (or vice versa) in the expression "{}"'\
                    .format(current_line.line_no, current_line.expression, left, right, line_n.expression)
                return response
            x += 1
    
    if current_tree.left != None:
        response = check_subs(current_tree.left, line_n_tree.left, left, right, current_line, line_n)
        if response.err_msg != None:
            return response

    if current_tree.right != None:
        response = check_subs(current_tree.right, line_n_tree.right, left, right, current_line, line_n)
        if response.err_msg != None:
            return response

    response = ProofResponse()
    response.is_valid = True
    return response