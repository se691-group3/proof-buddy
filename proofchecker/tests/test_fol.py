from django.test import TestCase
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj, ProofResponse
from proofchecker.proofs.proofchecker import verify_proof, verify_rule
from proofchecker.utils import folparser
from proofchecker.utils.follexer import IllegalCharacterFOLError, lexer


class FOLLexerTests(TestCase):
    def test_lexer_raises_IllegalCharacterError(self):
        """
        The lexer should raise an IllegalCharacterError
        if provided an invalid character
        """
        self.assertRaises(IllegalCharacterFOLError, folparser.parser.parse, 'A1', lexer=lexer)


class FOLParserTests(TestCase):

    def test_parser_tree_structure(self):
        """
        The parser should create an accurate binary tree representation
        """
        str1 = '¬((∀x∈U F(x)) ∨ (∃y∈U ¬F(y)))'
        node1 = folparser.parser.parse(str1, lexer=lexer)
        self.assertEqual(node1.value, '¬')
        self.assertEqual(node1.left, None)
        self.assertEqual(node1.right.value, '∨')
        self.assertEqual(node1.right.left.value, '∀x∈U')
        self.assertEqual(node1.right.left.right.value, 'F(x)')
        self.assertEqual(node1.right.right.value, '∃y∈U')
        self.assertEqual(node1.right.right.right.value, '¬')
        self.assertEqual(node1.right.right.right.right.value, 'F(y)')
        
        str2 = '∀x∈U Fxab ∨ Gy'
        node2 = folparser.parser.parse(str2, lexer=lexer)
        self.assertEqual(node2.value, '∀x∈U')
        self.assertEqual(node2.right.value, '∨')
        self.assertEqual(node2.right.left.value, 'Fxab')
        self.assertEqual(node2.right.right.value, 'Gy')

    def test_parser(self):
        """
        The parser should create a binary tree representing the FOL expression
        """
        str1 = 'a=b'
        str2 = 'F(x)'
        str3 = 'F(x) ∨ G(y)'
        str4 = '∀x∈S H(x)'
        str5 = 'Fabc'
        str6 = 'Fabc > Gxyz'
        str7 = 'F(x, y) ∨ G(x, y)'
        node1 = folparser.parser.parse(str1, lexer=lexer)
        node2 = folparser.parser.parse(str2, lexer=lexer)
        node3 = folparser.parser.parse(str3, lexer=lexer)
        node4 = folparser.parser.parse(str4, lexer=lexer)
        node5 = folparser.parser.parse(str5, lexer=lexer)
        node6 = folparser.parser.parse(str6, lexer=lexer)
        node7 = folparser.parser.parse(str7, lexer=lexer)
        self.assertEqual(node1.value, '=')
        self.assertEqual(node1.left.value, 'a')
        self.assertEqual(node1.right.value, 'b')
        self.assertEqual(node2.value, 'F(x)')
        self.assertEqual(node3.value, '∨')
        self.assertEqual(node3.left.value, 'F(x)')
        self.assertEqual(node3.right.value, 'G(y)')
        self.assertEqual(node4.value, '∀x∈S')
        self.assertEqual(node4.right.value, 'H(x)')
        self.assertEqual(node5.value, 'Fabc')
        self.assertEqual(node6.value, '→')
        self.assertEqual(node6.left.value, 'Fabc')
        self.assertEqual(node6.right.value, 'Gxyz')
        self.assertEqual(node7.value, '∨')
        self.assertEqual(node7.left.value, 'F(x,y)')
        self.assertEqual(node7.right.value, 'G(x,y)')

    def test_parser_reformatting_symbols(self):
        """
        The parser should reformat symbols as necessary
        """
        str1 = 'F(x)^G(y)'
        str2 = 'A(a)|B(b)'
        str3 = '~H(z)'
        str4 = 'F(x)>G(y)'
        str5 = 'H(a)->J(b)'
        str6 = 'L(i)<->M(j)'
        str7 = 'Q(s)&R(s)'
        node1 = folparser.parser.parse(str1, lexer=lexer)
        node2 = folparser.parser.parse(str2, lexer=lexer)
        node3 = folparser.parser.parse(str3, lexer=lexer)
        node4 = folparser.parser.parse(str4, lexer=lexer)
        node5 = folparser.parser.parse(str5, lexer=lexer)
        node6 = folparser.parser.parse(str6, lexer=lexer)
        node7 = folparser.parser.parse(str7, lexer=lexer)
        self.assertEqual(node1.value, '∧')
        self.assertEqual(node2.value, '∨')
        self.assertEqual(node3.value, '¬')
        self.assertEqual(node4.value, '→')
        self.assertEqual(node5.value, '→')
        self.assertEqual(node6.value, '↔')
        self.assertEqual(node7.value, '∧')

    def test_parser_raises_SyntaxError(self):
        """
        The parser should raise a SyntaxError
        if provided invalid syntax
        """
        str1='A(x)∧B'
        str2='A∧B'
        self.assertRaises(SyntaxError, folparser.parser.parse, str1, lexer=lexer)
        self.assertRaises(SyntaxError, folparser.parser.parse, str2, lexer=lexer)

class ProofCheckerTests(TestCase):
    def test_verify_rule(self):
        """
        Test that the verify_rule function is working properly
        """
        # Test and_intro
        line1 = ProofLineObj('1', 'A(x)', 'Premise')
        line2 = ProofLineObj('2', 'B(x)', 'Premise')
        line3 = ProofLineObj('3', 'A(x)∧B(x)', '∧I 1, 2')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

    
        # Test and_elim
        line1 = ProofLineObj('1', 'A(x)∧B(x)', 'Premise')
        line2 = ProofLineObj('2', 'A(x)', '∧E 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2])
        parser = folparser.parser
        result = verify_rule(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test or_intro
        line1 = ProofLineObj('1', 'A(x)', 'Premise')
        line2 = ProofLineObj('2', 'A(x)∨B(x)', '∨I 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2])
        parser = folparser.parser
        result = verify_rule(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test or_elim
        line1 = ProofLineObj('1', 'A(x)∨B(x)', 'Premise')
        line2 = ProofLineObj('2.1', 'A(x)', 'Assumption')
        line3 = ProofLineObj('2.2', 'C(x)', 'Assumption')
        line4 = ProofLineObj('3.1', 'B(x)', 'Assumption')
        line5 = ProofLineObj('3.2', 'C(x)', 'Assumption')
        line6 = ProofLineObj('4', 'C(x)', '∨E 1, 2, 3')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3, line4, line5, line6])
        parser = folparser.parser
        result = verify_rule(line6, proof, parser)
        self.assertTrue(result.is_valid)

        # Test not_intro
        line1 = ProofLineObj('1.1', 'A(x)', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'Premise')
        line3 = ProofLineObj('2', '¬A(x)', '¬I 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test not_elim
        line1 = ProofLineObj('1', '¬A(x)', 'Premise')
        line2 = ProofLineObj('2', 'A(x)', 'Premise')
        line3 = ProofLineObj('3', '⊥', '¬E 1, 2')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test implies_intro
        line1 = ProofLineObj('1.1', 'A(x)', 'Assumption')
        line2 = ProofLineObj('1.2', 'B(x)', 'Assumption')
        line3 = ProofLineObj('2', 'A(x)→B(x)', '→I 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test implies_elim
        line1 = ProofLineObj('1', 'A(x)→B(x)', 'Premise')
        line2 = ProofLineObj('2', 'A(x)', 'Premise')
        line3 = ProofLineObj('3', 'B(x)', '→E 1, 2')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test indirect_proof
        line1 = ProofLineObj('1.1', '¬A(x)', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'Premise')
        line3 = ProofLineObj('2', 'A(x)', 'IP 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test explosion
        line1 = ProofLineObj('1', '⊥', 'Premise')
        line2 = ProofLineObj('2', 'B(x)', 'X 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2])
        parser = folparser.parser
        result = verify_rule(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test iff intro
        line1 = ProofLineObj('1.1', 'A(x)', 'Assumption')
        line2 = ProofLineObj('1.2', 'B(x)', 'Assumption')
        line3 = ProofLineObj('2.1', 'B(x)', 'Assumption')
        line4 = ProofLineObj('2.2', 'A(x)', 'Assumption')
        line5 = ProofLineObj('3', 'A(x)↔B(x)', '↔I 1, 2')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3, line4, line5])
        parser = folparser.parser
        result = verify_rule(line5, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test iff elim
        line1 = ProofLineObj('1', 'A(x)↔B(x)', 'Assumption')
        line2 = ProofLineObj('2', 'A(x)', 'Assumption')
        line3 = ProofLineObj('3', 'B(x)', '↔E 1, 2')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_rule(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test reiteration
        line1 = ProofLineObj('1', 'A(x)', 'Premise')
        line2 = ProofLineObj('2', 'A(x)', 'R 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2])
        parser = folparser.parser
        result = verify_rule(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test double not elim
        line1 = ProofLineObj('1', '¬¬A(x)', 'Assumption')
        line2 = ProofLineObj('2', 'A(x)', 'DNE 1')
        proof = ProofObj(rules='fol_derived', lines=[line1, line2])
        parser = folparser.parser
        result = verify_rule(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

    def test_verify_proof_with_valid_proof(self):
        """
        Test that the verify_proof function returns is_valid == True
        when provided with a valid proof
        """
        # And Intro
        line1 = ProofLineObj('1', 'A(x)', 'Premise')
        line2 = ProofLineObj('2', 'B(x)', 'Premise')
        line3 = ProofLineObj('3', 'A(x)∧B(x)', '∧I 1, 2')
        proof = ProofObj(rules='fol_derived', premises=['A(x)', 'B(x)'], conclusion='A(x)∧B(x)', lines=[line1, line2, line3])
        parser = folparser.parser
        result = verify_proof(proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)