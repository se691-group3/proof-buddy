from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofutils import clean_rule, get_line, is_var, is_name, make_tree, verify_line_citation, verify_same_var_and_domain
from .rule import Rule

class ConversionOfQuantifiers(Rule):

    name = 'Conversion of Quantifiers'
    symbols = 'CQ'

    def verify(self, current_line: ProofLineObj, proof: ProofObj, parser):
        """
        Verify proper implementation of the rule CQ m
        (Conversion of Quantifiers)
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
                
                ### Case 1
                if root_m.value[0] == '∀':
                    
                    # Verify that the predicate is negated
                    if root_m.right.value != '¬':
                        response.err_msg = 'Error on line {}: If line {} begins with a universal quantifier (∀), it should be followed by a negation (¬) '\
                            'when applying Conversion of Quantifiers (CQ)'\
                            .format(str(current_line.line_no), str(target_line.line_no))
                        response.type = 14
                        return response
                    
                    # Verify the current line is a negation of an existential quantifier
                    if ((current.value != '¬') or (current.right.value[0] != '∃')):
                        response.err_msg = 'Error on line {}: If line {} begins with a universal quantifier (∀), then line {} should be the negation (¬) '\
                            'of an existential quantifier (∃) when applying Conversion of Quantifiers (CQ)'\
                            .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                        response.type = 15
                        return response

                    # Verify the two lines refer ot the same variable and domain
                    result = verify_same_var_and_domain(root_m, current.right, target_line.line_no, current_line.line_no)
                    if result.is_valid == False:
                        result.err_msg = "Error on line {}: ".format(current_line.line_no) + result.err_msg
                        response.type = 16
                        return result

                ### Case 3
                if root_m.value[0] == '∃':

                    # Verify that the predicate is negated
                    if root_m.right.value != '¬':
                        response.err_msg = 'Error on line {}: If line {} begins with an existential quantifier (∃), it should be followed by a negation (¬) '\
                            'when applying Conversion of Quantifiers (CQ)'\
                            .format(str(current_line.line_no), str(target_line.line_no))
                        response.type = 17
                        return response

                    # Verify the current line is a negation of a universal quantifier
                    if ((current.value != '¬') or (current.right.value[0] != '∀')):
                        response.err_msg = 'Error on line {}: If line {} begins with an existential quantifier (∃), then line {} should be the negation (¬) '\
                            'of a universal quantifier (∀) when applying Conversion of Quantifiers (CQ)'\
                            .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                        response.type = 18
                        return response

                    # Verify the two lines refer ot the same variable and domain
                    result = verify_same_var_and_domain(root_m, current.right, target_line.line_no, current_line.line_no)
                    if result.is_valid == False:
                        result.err_msg = "Error on line {}: ".format(current_line.line_no) + result.err_msg
                        response.type = 19
                        return result

                ### Cases 2 and 4
                if root_m.value == '¬':
                    if ((root_m.right.value[0] != '∃') and (root_m.right.value[0] != '∀')):
                        response.err_msg = "Error on line {}: The negation on line {} should be followed by a quantifier"\
                            .format(str(current_line.line_no), str(target_line.line_no))
                        response.type = 20
                        return response

                    ### Case 2
                    if (root_m.right.value[0] == '∃'):

                        # Verify the current line is a universal quantifier
                        if current.value[0] != '∀':
                            response.err_msg = 'Error on line {}: If line {} is the negation of an existential quantifier, then line {} should begin '\
                                'with a universal quantifier when applying Conversion of Quantifiers (CQ)'\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            response.type = 21
                            return response

                        # Verify the quantifier is followed by a negation
                        if current.right.value != '¬':
                            response.err_msg = 'Error on line {}: The quantifier on line {} should be followed by a negation (¬)'\
                                .format(str(current_line.line_no), str(current_line.line_no))
                            response.type = 22
                            return response

                        # Verify the two lines refer ot the same variable and domain
                        result = verify_same_var_and_domain(root_m.right, current, target_line.line_no, current_line.line_no)
                        if result.is_valid == False:
                            result.err_msg = "Error on line {}: ".format(current_line.line_no) + result.err_msg
                            response.type = 23
                            return result
                    
                    ### Case 4
                    if (root_m.right.value[0] == '∀'):

                        # Verify the current line is a existential quantifier
                        if current.value[0] != '∃':
                            response.err_msg = 'Error on line {}: If line {} is the negation of a universal quantifier, then line {} should begin '\
                                'with an existential quantifier when applying Conversion of Quantifiers (CQ)'\
                                .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                            response.type = 24
                            return response

                        # Verify the quantifier is followed by a negation
                        if current.right.value != '¬':
                            response.err_msg = 'Error on line {}: The quantifier on line {} should be followed by a negation (¬)'\
                                .format(str(current_line.line_no), str(current_line.line_no))
                            response.type = 25
                            return response

                        # Verify the two lines refer ot the same variable and domain
                        result = verify_same_var_and_domain(root_m.right, current, target_line.line_no, current_line.line_no)
                        if result.is_valid == False:
                            result.err_msg = "Error on line {}: ".format(current_line.line_no) + result.err_msg
                            result.type = 26
                            return result

                # Verify that line m did in fact begin with either a quantifier or a negation
                if ((root_m.value[0] != '∀') and (root_m.value[0] != '∃') and (root_m.value != '¬')):                 
                    response.err_msg = "Error on line {}: Line {} must begin with either a quantifier or a negation when applying Conversion of Quantifiers (CQ)"\
                        .format(str(current_line.line_no), str(target_line.line_no))
                    response.type = 27
                    return response

                # Verify that line m and current line refer to the same predicate
                # Note: This works the same for all four cases
                if root_m.right.right.value[0] != current.right.right.value[0]:
                    response.err_msg = "Error on line {}: Lines {} and {} should refer to the same predicate"\
                        .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                    response.type = 28
                    return response

                # Verify that line m and current line have same number of predicate inputs
                # Note: This works the same for all four cases
                count_m = 0
                count_curr = 0
                for ch in root_m.right.right.value:
                    if (is_var(ch) or is_name(ch)):
                        count_m += 1
                for ch in current.right.right.value:
                    if (is_var(ch) or is_name(ch)):
                        count_curr += 1

                if count_m != count_curr:
                    response.err_msg = "Error on line {}: The predicates on lines {} and {} do not have the same number of inputs"\
                        .format(str(current_line.line_no), str(target_line.line_no), str(current_line.line_no))
                    response.type = 29
                    return response

                # If we made it this far, it should be valid
                response.is_valid = True
                response.type = 0
                return response

            except:
                response.err_msg = "Error on line {}: Line numbers are not specified correctly.  Conversion of Quantifiers: CQ m"\
                    .format(str(current_line.line_no))
                response.type = 30
                return response

        except:
            response.err_msg = "Error on line {}: Rule not formatted properly.  Conversion of Quantifiers: CQ m"\
                .format(str(current_line.line_no))
            response.type = 31
            return response