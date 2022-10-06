from django.test import TestCase
from proofchecker.utils import folparser
from proofchecker.utils import numparser
from proofchecker.utils import tflparser
from proofchecker.utils.binarytree import Node, inorder, postorder, preorder, tree_to_string, string_to_tree
from proofchecker.utils.numlexer import lexer as numlexer
from proofchecker.utils.syntax import Syntax
from proofchecker.utils.tfllexer import IllegalCharacterError, lexer as tfllexer
from proofchecker.utils.tfllexer import IllegalCharacterError as err, lexer as follexer


class BinaryTreeTests(TestCase):

    def test_node_to_str(self):
        """
        Verify that __str__ of node returns inorder walk
        """
        b = Node('∨')
        b.left = Node('∧')
        b.left.left = Node('A')
        b.left.right = Node('B')
        b.right = Node('C')
        str1 = 'A∧B∨C'
        self.assertEqual(str(b), str1)


    def test_node_equivalence(self):
        """
        Should return true when comparing two separate nodes 
        that represent binary trees with identical values
        """
        a = Node('^')
        a.left = Node('A')
        a.right = Node('B')

        b = Node('v')
        b.left = Node('^')
        b.left.left = Node('A')
        b.left.right = Node('B')
        b.right = Node('C')

        c = tflparser.parser.parse('A∧B', lexer=tfllexer)
        d = tflparser.parser.parse('(A∧B)∨[(¬C→D)∧(A↔Z)]', lexer=tfllexer)

        self.assertEqual(a, b.left)
        self.assertEqual(c, d.left)

        e = tflparser.parser.parse('A∧B', lexer=tfllexer)
        f = tflparser.parser.parse('A∧B', lexer=tfllexer)

        # FIXME: Two different characters representing same symbol cause failure
        # self.assertEqual(e, f)
    
    def test_tree_to_string(self):
        """
        Should construct an unambiguous string representation
        of the binary tree
        """
        a = tflparser.parser.parse('(A∧B)∨C', lexer=tfllexer)
        b = tflparser.parser.parse('A∧(B∨C)', lexer=tfllexer)

        c = []
        d = []

        e = tflparser.parser.parse('A ∧ B', lexer=tfllexer)
        f = []

        tree_to_string(a, c)
        tree_to_string(b, d)
        tree_to_string(e, f)

        self.assertEqual(''.join(c), '∨(∧(A)(B))(C)')
        self.assertEqual(''.join(d), '∧(A)(∨(B)(C))')
        self.assertEqual(''.join(f), '∧(A)(B)')
    
    def test_string_to_tree(self):
        """
        Should construct a binary tree from an
        unambigious string representation
        """
        a = '∨(∧(A)(B))(C)'

        b = string_to_tree(a)
        c = tflparser.parser.parse('(A∧B)∨C', lexer=tfllexer)
        
        self.assertTrue(b.value == '∨')
        self.assertEqual(b, c)

    def test_preorder(self):
        """
        Should return the correct preorder walk of a tree
        """
        str1 = '(A∧B)∨C'
        str2 = preorder(tflparser.parser.parse(str1, lexer=tfllexer))
        self.assertEqual(str2, '∨∧ABC')

    def test_inorder(self):
        """
        Should return the correct inorder walk of a tree
        """
        str1 = '(A∧B)∨C'
        str2 = inorder(tflparser.parser.parse(str1, lexer=tfllexer))
        self.assertEqual(str2, 'A∧B∨C')

    def test_postorder(self):
        """
        Should return the correct postorder walk of a tree
        """
        str1 = '(A∧B)∨C'
        str2 = postorder(tflparser.parser.parse(str1, lexer=tfllexer))
        self.assertEqual(str2, 'AB∧C∨')

class SyntaxTests(TestCase):

    def test_remove_justification_with_just(self):
        """
        remove_justification() should return the substring before the '#'
        """
        str = 'A∧B #∧I, 1,2'
        str2 = Syntax.remove_justification(str)
        self.assertEqual(str2, 'A∧B ')

    def test_remove_justification_without_just(self):
        """
        remove_justification should return the same string if there is no '#'
        """
        str = '(A∧B)∨C'
        str2 = Syntax.remove_justification(str)
        self.assertEqual(str2, '(A∧B)∨C')

    def test_has_valid_symbols_with_valid_symbols(self):
        """
        has_valid_symbols() should return True if all
        characters in the string are valid TFL symbols
        """
        str = '(A∧B)∨C'
        self.assertIs(Syntax.has_valid_symbols(str), True)

    def test_has_valid_symbols_with_invalid_symbols(self):
        """
        has_valid_symbols should return False if one or more
        characters in the string are not valid TFL symbols
        """
        str = 'A>B=C'
        self.assertIs(Syntax.has_valid_symbols(str), False)

    def test_has_balanced_parens_with_balanced_parens(self):
        """
        has_balanced_parens should return True if all parentheses
        in the string are balanced and properly matching
        """
        str = '{[]{()}}'
        self.assertIs(Syntax.has_balanced_parens(str), True)

    def test_has_balanced_parens_with_unbalanced_parens(self):
        """
        has_balanced_parens should return False if parentheses
        in the string are unbalanced or not properly matching
        """
        str = '[{}{})(]'
        str2 = '((()'
        str3 = '(]'
        self.assertIs(Syntax.has_balanced_parens(str), False)
        self.assertIs(Syntax.has_balanced_parens(str2), False)
        self.assertIs(Syntax.has_balanced_parens(str3), False)

    def test_set_depth_array(self):
        str = '(A∧B)∨C'
        str2 = '[(A∧B)∨C]'
        depth_array = Syntax.set_depth_array(str)
        depth_array_2 = Syntax.set_depth_array(str2)
        self.assertEqual(depth_array, [1, 1, 1, 1, 0, 0, 0])
        self.assertEqual(depth_array_2, [1, 2, 2, 2, 2, 1, 1, 1, 0])

    def test_find_main_operator_without_outer_parens(self):
        """
        find_main_operator should return the main logical operator
        of a TFL statement
        """
        str = '(A∧B)∨C'
        self.assertEqual(Syntax.find_main_operator(str), 5)

    def test_find_main_operator_without_outer_parens(self):
        """
        find_main_operator should return the main logical operator
        of a TFL statement
        """
        str = '[(A∧B)∨C]'
        self.assertEqual(Syntax.find_main_operator(str), 6)

    def test_is_valid_TFL_with_atomic_sentence(self):
        """
        is_valid_TFL should return true if provided an atomic sentence
        """
        str1 = 'A'
        str2 = 'Z'
        self.assertIs(Syntax.is_valid_TFL(str1), True)
        self.assertIs(Syntax.is_valid_TFL(str2), True)

    def test_is_valid_TFL_with_one_operator(self):
        """
        is_valid_TFL should return true if provided a well-formed formula (WFF)
        with one operator
        """
        str1 = 'A∧B'
        str2 = '(C∨D)'
        str3 = '¬E'
        str4 = '{X→Y}'
        str5 = 'A↔Z'
        self.assertIs(Syntax.is_valid_TFL(str1), True)
        self.assertIs(Syntax.is_valid_TFL(str2), True)
        self.assertIs(Syntax.is_valid_TFL(str3), True)
        self.assertIs(Syntax.is_valid_TFL(str4), True)
        self.assertIs(Syntax.is_valid_TFL(str5), True)

    def test_is_valid_TFL_with_multiple_operators(self):
        """
        is_valid_TFL should return true if provided a WFF with multiple operators
        """
        str1 = '(A∧B)∨C'
        str2 = '(A∧B)∨[(¬C→D)∧(A↔Z)]'
        self.assertIs(Syntax.is_valid_TFL(str1), True)
        self.assertIs(Syntax.is_valid_TFL(str2), True)

    def test_is_valid_TFL_with_invalid_input(self):
        """
        is_valid_TFL should return false if provided with a string that
        does not conform to TFL sentence rules
        """
        invalid_symbols = 'A+Z'
        unbalanced_parens = '[A∧B)]'
        self.assertIs(Syntax.is_valid_TFL(invalid_symbols), False)
        self.assertIs(Syntax.is_valid_TFL(unbalanced_parens), False)

class TflParseTests(TestCase):

    def test_parser_puts_main_op_in_root_node(self):
        """
        The parser should return a binary tree
        with the main operator as the root node
        """
        str1 = '(A∧B)∨C'
        str2 = '(A∨B)∧[(¬C→D)∧(A↔Z)]'
        node1 = tflparser.parser.parse(str1, lexer=tfllexer)
        node2 = tflparser.parser.parse(str2, lexer=tfllexer)
        self.assertEqual(node1.value, '∨')
        self.assertEqual(node2.value, '∧')

    def test_parser_reformatting_symbols(self):
        """
        The parser should reformat symbols as necessary
        """
        str1 = 'A^B'
        str2 = 'CvD'
        str3 = '~E'
        str4 = 'F>G'
        str5 = 'H->J'
        str6 = 'L<->M'
        str7 = 'N&O'
        node1 = tflparser.parser.parse(str1, lexer=tfllexer)
        node2 = tflparser.parser.parse(str2, lexer=tfllexer)
        node3 = tflparser.parser.parse(str3, lexer=tfllexer)
        node4 = tflparser.parser.parse(str4, lexer=tfllexer)
        node5 = tflparser.parser.parse(str5, lexer=tfllexer)
        node6 = tflparser.parser.parse(str6, lexer=tfllexer)
        node7 = tflparser.parser.parse(str7, lexer=tfllexer)
        self.assertEqual(node1.value, '∧')
        self.assertEqual(node2.value, '∨')
        self.assertEqual(node3.value, '¬')
        self.assertEqual(node4.value, '→')
        self.assertEqual(node5.value, '→')
        self.assertEqual(node6.value, '↔')
        self.assertEqual(node7.value, '∧')

    def test_parser_raises_SyntaxError(self):
        """
        The parser should raise a TFLSyntaxError
        if provided invalid syntax
        """
        str1='A∧'
        self.assertRaises(SyntaxError, tflparser.parser.parse, str1, lexer=tfllexer)

class TFLLexerTests(TestCase):
    def test_lexer_raises_IllegalCharacterError(self):
        """
        The lexer should raise an IllegalCharacterError
        if provided an invalid character
        """
        self.assertRaises(IllegalCharacterError, tflparser.parser.parse, 'A1', lexer=tfllexer)


class NumParseTests(TestCase):

    def test_num_parser(self):
        """
        The parser should return the depth of the line number
        (i.e. the amount of numbers separated by dots)
        """
        str1 = '3'
        str2 = '3.12.4'
        str3 = '3.12.4.66666.7.16.5'
        a = numparser.parser.parse(str1, lexer=numlexer)
        b = numparser.parser.parse(str2, lexer=numlexer)
        c = numparser.parser.parse(str3, lexer=numlexer)
        self.assertEqual(a, 1)
        self.assertEqual(b, 3)
        self.assertEqual(c, 7)

    def test_parser_raises_SyntaxError(self):
        """
        The parser should raise a TFLSyntaxError
        if provided invalid syntax
        """
        str1='3..12'
        self.assertRaises(SyntaxError, numparser.parser.parse, str1, lexer=numlexer)

class NumLexerTests(TestCase):
    def test_lexer_raises_IllegalCharacterError(self):
        """
        The lexer should raise an IllegalCharacterError
        if provided an invalid character
        """
        self.assertRaises(IllegalCharacterError, tflparser.parser.parse, '3.a', lexer=tfllexer)