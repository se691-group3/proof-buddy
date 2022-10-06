from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line_DNE, verify_line_citation, make_tree
from proofchecker.utils.binarytree import Node
from .rule import Rule

class DeMorgan(Rule):

    name = "De Morgan"
    symbols = "DeM"

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule DeM m
        (De Morgan Rules)
        """
        rule = clean_rule(current_line.rule)
        response = ProofResponse()

        # Attempt to find line m
        try:
            target_line = get_line_DNE(rule, proof)

            # Verify if line citation is valid
            result = verify_line_citation(current_line.line_no, target_line.line_no)
            if result.is_valid == False:
                return result

            try: 
                expression = target_line.expression
                root_m = make_tree(expression, parser)
                current = make_tree(current_line.expression, parser)

                if root_m.value == '¬':
                    
                    ### Case 1: 
                    if root_m.right.value == '∧':

                        if current.value != '∨':
                            response.err_msg = "Error on line {}: If line {} is the negation of a conjuction, line {} should be a disjunction (∨) when applying the first De Morgan rule."\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            return response

                        try:
                            neg_left = Node('¬')
                            neg_right = Node('¬')
                            neg_left.right = root_m.right.left
                            neg_right.right = root_m.right.right
                            
                            if (neg_left != current.left) or (neg_right != current.right):
                                response.err_msg = "Error on line {}: The atomic sentences on line {} should be negations of the atomic sentences on line {}."\
                                    .format(str(current_line.line_no), str(current_line.line_no), str(target_line.line_no))
                                return response
                            else:
                                response.is_valid = True
                                return response

                        except:
                            response.err_msg = "Error on line {}: Line {} does not conform to any of De Morgan's rules."\
                                .format(str(current_line.line_no), str(target_line.line_no))
                            return response

                    ### Case 3:
                    if root_m.right.value == '∨':

                        if current.value != '∧':
                            response.err_msg = "Error on line {}: If line {} is the negation of a disjunction, line {} should be a conjunction (∧) when applying the third De Morgan rule."\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            return response

                        try:
                            neg_left = Node('¬')
                            neg_right = Node('¬')
                            neg_left.right = root_m.right.left
                            neg_right.right = root_m.right.right
                            
                            if (neg_left != current.left) or (neg_right != current.right):
                                response.err_msg = "Error on line {}: The atomic sentences on line {} should be negations of the atomic sentences on line {}."\
                                    .format(str(current_line.line_no), str(current_line.line_no), str(target_line.line_no))
                                return response
                            else:
                                response.is_valid = True
                                return response

                        except:
                            response.err_msg = "Error on line {}: Line {} does not conform to any of De Morgan's rules."\
                                .format(str(current_line.line_no), str(target_line.line_no))
                            return response


                ### Case 2
                if root_m.value == '∨':

                    if (current.value != '¬') or (current.right.value != '∧'):
                        response.err_msg = "Error on line {}: If line {} is a disjunction, line {} should be the negation of a conjunction (∧) when applying the second De Morgan rule."\
                            .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                        return response

                    try:
                        neg_left = Node('¬')
                        neg_right = Node('¬')
                        neg_left.right = current.right.left
                        neg_right.right = current.right.right
                        
                        if (neg_left != root_m.left) or (neg_right != root_m.right):
                            response.err_msg = "Error on line {}: The atomic sentences on line {} should be negations of the atomic sentences on line {}."\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            return response
                        else:
                            response.is_valid = True
                            return response

                    except:
                        response.err_msg = "Error on line {}: Line {} does not conform to any of De Morgans rules."\
                            .format(str(current_line.line_no), str(target_line.line_no))
                        return response


                ### Case 4
                if root_m.value == '∧':

                    if (current.value != '¬') or (current.right.value != '∨'):
                        response.err_msg = "Error on line {}: If line {} is a conjunction, line {} should be the negation of a disjunction (∨) when applying the fourth De Morgan rule."\
                            .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                        return response

                    try:
                        neg_left = Node('¬')
                        neg_right = Node('¬')
                        neg_left.right = current.right.left
                        neg_right.right = current.right.right
                        
                        if (neg_left != root_m.left) or (neg_right != root_m.right):
                            response.err_msg = "Error on line {}: The atomic sentences on line {} should be negations of the atomic sentences on line {}."\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            return response
                        else:
                            response.is_valid = True
                            return response

                    except:
                        response.err_msg = "Error on line {}: Line {} does not conform to any of De Morgans rules."\
                            .format(str(current_line.line_no), str(target_line.line_no))
                        return response

                # If we reached this point, we did not encounter a valid application of DeM
                response.err_msg = "Error on line {}: Line {} does not conform to any of De Morgans rules."\
                    .format(str(current_line.line_no), str(target_line.line_no))
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  De Morgan: DeM m"\
                    .format(str(current_line.line_no))
                return response      

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  De Morgan: DeM m"\
                .format(str(current_line.line_no))
            return response 