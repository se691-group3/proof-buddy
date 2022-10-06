"""
NOTE: THIS FILE IS DEPRECATED
All syntax validation and proof validation is currently managed in the proof.py file.
"""   

   
# TODO: In find_main_operator(), test for multiple operators at depth 0 
# Apply standard order of operations if multiple operators at depth 0
# e.g. ¬A∨B should recognize ∨ as the main logical operator

from .constants import Constants

class Syntax:

    @staticmethod
    def is_valid_TFL(str):
        """
        Determine if a line of text represents a valid TFL statement
        """
        # Lines in a `prooftext` contain a justification after the '#' symbol
        # If the line contains a justification, remove it
        line = str
        if '#' in line:
            line = Syntax.remove_justification(line)

        # Strip all whitespace from the line
        line.replace(" ", "")

        # Verify all remaining characters are valid TFL symbols
        if Syntax.has_valid_symbols(line):

            # Check for matching parentheses
            if Syntax.has_balanced_parens(line):

                # Determine the depth of each char in the line
                depth_array = Syntax.set_depth_array(line)

                # Remove matching outermost parentheses
                if depth_array[0]==1:
                    parens_match = True
                    index = 0
                    # Depth drops to zero somewhere if outermost parentheses do not match
                    for char in line[0:len(line)-1]:
                        parens_match = (parens_match and depth_array[index]>0)
                        index += 1
                    # Strip the outermost parentheses, call function recursively
                    # Add one to the result for the leading parenthesis that was removed
                    if parens_match:
                        return (Syntax.is_valid_TFL(line[1:len(line)-1]))

                # Find the main logical operator
                if ('∧' or '∨' or '¬' or '→' or '↔') in line:
                    op_index = Syntax.find_main_operator(line)

                    # Grab the substrings around the main operator
                    left = line[0:op_index]
                    right = line[op_index+1:len(line)]

                    # There should be values on both sides unless the operator is ¬
                    if not line[op_index] == '¬':
                        if left == '':
                            return False
                        if right == '':
                            return False

                    # Determine that both substrings are valid TFL sentences (recursion)
                    left_is_valid = Syntax.is_valid_TFL(left)
                    right_is_valid = Syntax.is_valid_TFL(right)
                    
                    if not (left_is_valid and right_is_valid):
                        return False
            else:
                return False
        else:
            return False

        # If we reached this line, everything checks out
        return True

    @staticmethod
    def remove_justification(str):
        """
        Removes the justification from the line, if present
        """

        line = str
        char = '#'
        if char in line:
            index = 0
            for char in line:
                if char == '#':
                    line = line[0:index]
                    break
                else:
                    index += 1

        return line

    @staticmethod
    def has_balanced_parens(str):
        """
        Determines if a string has balanced parentheses
        """
        stack = []

        for char in str:
            if char in Constants.OPEN_PARENS:
                stack.append(char)
            elif char in Constants.CLOSED_PARENS:
                pos = Constants.CLOSED_PARENS.index(char)
                if ((len(stack) > 0) and 
                    (Constants.OPEN_PARENS[pos] == stack[len(stack)-1])):
                    stack.pop()
                else:
                    return False
        if len(stack)==0:
            return True

        return False

    @staticmethod
    def has_valid_symbols(str):
        """
        Verifies that all characters in a string are valid TFL symbols
        """
        for char in str:
            if not ((char in Constants.ATOMIC) or (char in Constants.CONNECTIVES) 
                or (char in Constants.PARENS)):
                return False

        return True

    @staticmethod
    def find_main_operator(str):
        """
        Returns the index of the main logical operator in a TFL sentence
        """

        line = str
        op_index = 0

        # Determine the depth of each char in the sentence
        depth_array = Syntax.set_depth_array(line)

        # Remove matching outermost parentheses
        if depth_array[0]==1:
            parens_match = True
            index = 0
            # Depth drops to zero somewhere if outermost parentheses do not match
            for char in line[0:len(line)-1]:
                parens_match = (parens_match and depth_array[index]>0)
                index += 1
            # Strip the outermost parentheses, call function recursively
            # Add one to the result for the leading parenthesis that was removed
            if parens_match:
                return (Syntax.find_main_operator(line[1:len(line)-1]) + 1)

        # Find the main operator
        for char in line:
            if ((char in Constants.CONNECTIVES) and (depth_array[op_index]==0)):
                return op_index
            else:
                op_index += 1

        # If no operator found, return 0
        return 0

    @staticmethod
    def set_depth_array(str):
        """
        Returns an array containing the depth of each character in a TFL sentence
        """
        depth = 0
        depth_array = []

        for char in str:
            if char in Constants.OPEN_PARENS:
                depth += 1
            elif char in Constants.CLOSED_PARENS:
                depth -= 1

            depth_array.append(depth)

        return depth_array