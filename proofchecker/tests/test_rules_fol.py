from django.test import TestCase
from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj
from proofchecker.proofs.proofutils import make_tree
from proofchecker.rules.conversionofquantifiers import ConversionOfQuantifiers
from proofchecker.rules.equalityelim import EqualityElim, check_subs
from proofchecker.rules.equalityintro import EqualityIntro
from proofchecker.rules.existentialelim import ExistentialElim
from proofchecker.rules.existentialintro import ExistentialIntro
from proofchecker.rules.universalelim import UniversalElim
from proofchecker.rules.universalintro import UniversalIntro
from proofchecker.utils import folparser


class FOLRulesTests(TestCase):

    def test_equality_intro(self):
        rule = EqualityIntro()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'a=a', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        line1 = ProofLineObj('1', 'F(x, a)=F(x, a)', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        line1 = ProofLineObj('1', 'Fxa=Fxa', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where the root operand is not =
        line1 = ProofLineObj('1', 'F(x)', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 1: The root operand of the expression should be identity (=)')

        # Test where the left and right hand are not equivalent
        line1 = ProofLineObj('1', 'a=b', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 1: The left and right hand sides of the equation should be identical')

        # Test with invalid expression
        line1 = ProofLineObj('1', 'F(x, a)=a', 'Premise')
        proof = ProofObj(lines=[line1])
        result = rule.verify(line1, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 1: Error in the expression F(x, a)=a')


    def test_check_subs(self):
        """
        Test that the function check_subs (used for =E) is working correctly
        check_subs(current_tree, line_n_tree, left, right, current_line, line_n_expression)
        """
        # Test with valid input
        parser = folparser.parser
        current_tree = make_tree('F(a, b, a, b)', parser)
        line_n_tree = make_tree('F(a, a, a, a)', parser)
        left = 'a'
        right = 'b'
        current_line = ProofLineObj('3', 'F(a, b, a, b)', 'Premise')
        line_n = ProofLineObj('2', 'F(a, a, a, a)', 'Premise')
        result = check_subs(current_tree, line_n_tree, left, right, current_line, line_n)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        current_tree = make_tree('F(a) = G(a)', parser)
        line_n_tree = make_tree('F(a) = H(a)', parser)
        left = 'G(a)'
        right = 'H(a)'
        current_line = ProofLineObj('3', 'F(a)=G(a)', 'Premise')
        line_n = ProofLineObj('2', 'F(a) = H(a)', 'Premise')
        result = check_subs(current_tree, line_n_tree, left, right, current_line, line_n)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with invalid input
        parser = folparser.parser
        current_tree = make_tree('F(a, b, a, c)', parser)
        line_n_tree = make_tree('F(a, a, a, a)', parser)
        left = 'a'
        right = 'b'
        current_line = ProofLineObj('3', 'F(a, b, a, c)', 'Premise')
        line_n = ProofLineObj('2', 'F(a, a, a, a)', 'Premise')
        result = check_subs(current_tree, line_n_tree, left, right, current_line, line_n)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Expression "F(a, b, a, c)" cannot be achieved by replacing "a" with "b" (or vice versa) in the expression "F(a, a, a, a)"')


    def test_equality_elim(self):
        rule = EqualityElim()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'a=b', 'Premise')
        line2 = ProofLineObj('2', 'F(a)', 'Premise')
        line3 = ProofLineObj('3', 'F(b)', '=E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        line1 = ProofLineObj('1', 'a=b', 'Premise')
        line2 = ProofLineObj('2', 'F(a, a, a, a)', 'Premise')
        line3 = ProofLineObj('3', 'F(a, b, a, b)', '=E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with invalid input
        line1 = ProofLineObj('1', 'a=b', 'Premise')
        line2 = ProofLineObj('2', 'F(a, a, a, a)', 'Premise')
        line3 = ProofLineObj('3', 'F(a, b, a, c)', '=E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Expression "F(a, b, a, c)" cannot be achieved by replacing "a" with "b" (or vice versa) in the expression "F(a, a, a, a)"')

        line1 = ProofLineObj('1', 'a=b', 'Premise')
        line2 = ProofLineObj('2', 'F(a, a, a, a)', 'Premise')
        line3 = ProofLineObj('3', 'F(a, b, a)', '=E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Expressions on lines 2 and 3 should have similar structure')

        # Test with double swap input
        line1 = ProofLineObj('1', 'a=b', 'Premise')
        line2 = ProofLineObj('2', 'Pab', 'Premise')
        line3 = ProofLineObj('3', 'Pba', '=E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Expression "Pba" cannot be achieved by replacing "a" with "b" (or vice versa) in the expression "Pab"')
        

    def test_existential_intro(self):
        rule = ExistentialIntro()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'H(a, a)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x, a)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        # self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where root operand of line 2 is not ∃
        line1 = ProofLineObj('1', 'H(a)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The root operand of line 1 should be the existential quantifier (∃)')

        # Test where line 1 and line 2 refer to different predicates
        line1 = ProofLineObj('1', 'G(a)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The expressions on lines 1 and 2 do not refer to the same predicate')

        # Test where line 1 and 2 have different number of inputs
        line1 = ProofLineObj('1', 'H(a, b)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The predicates on lines 1 and 2 do not have the same number of inputs')

        # Test where the variable on line 2 does not replace a name on line 1
        line1 = ProofLineObj('1', 'H(y)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Instances of variable "x" on line 2 should replace a name on line 1')

        # Test where the variables on line 2 replace two different names on line 1
        line1 = ProofLineObj('1', 'H(a, b)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x, x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: All instances of variable "x" on line 2 should replace the same name on line 1')

        # Test where the variable on line 2 already appears on line 1
        line1 = ProofLineObj('1', 'H(a, x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x, x)', '∃I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Variable "x" on line 2 should not appear on line 1')

    def test_existential_elim(self):
        rule = ExistentialElim()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a, a)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        # self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where the root operand of line 1 is not ∃ 
        line1 = ProofLineObj('1', '∀x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a, a)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The root operand of line 1 should be the existential quantifier (∃)')

        # Test where lines 1 and 2.1 refer to different predicates
        line1 = ProofLineObj('1', '∃x∈S G(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a, a)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The expressions on lines 1 and 2.1 do not refer to the same predicate')

        # Test where lines 1 and 2.1 have different numbers of inputs
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The predicates on lines 1 and 2.1 do not have the same number of inputs')

        # Test where instances of bound var on line 1 are replaced by another var
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(z, z)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(y, y)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(y, y)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Instances of variable "x" on line 1 should replace a name on line 2.1')

        # Test where bound var on line 1 is replaced by different names on line 2.1
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, b)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, b)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a, b)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: All instances of variable "x" on line 1 should replace the same name on line 2.1')

        # Test where line i_x and current line have different expressions
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(b, b)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The expressions on line 2.2 and line 3 should be equivalent')

        # Test where 'c' is referenced earlier in the proof
        line1 = ProofLineObj('1', '∃x∈S F(c, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'F(a, a)', 'R 2.1')
        line4 = ProofLineObj('3', 'F(a, a)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The name "c" on line 2.1 should not appear earlier in the proof (it appears on line 1)')

        # Test where 'c' is referenced in 'B'
        line1 = ProofLineObj('1', '∃x∈S F(x, x)', 'Premise')
        line2 = ProofLineObj('2.1', 'F(c, c)', 'Assumption')
        line3 = ProofLineObj('2.2', 'B(c, c)', 'R 2.1')
        line4 = ProofLineObj('3', 'B(c, c)', '∃E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4])
        result = rule.verify(line4, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The name "c" on line 2.1 should not appear on line 3')


    def test_universal_elim(self):
        rule = UniversalElim()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈S H(x)', 'Premise')
        line2 = ProofLineObj('2', 'H(a)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈V Pxa', 'Premise')
        line2 = ProofLineObj('2', 'Paa', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈V Pxb', 'Premise')
        line2 = ProofLineObj('2', 'Pab', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where root operand of line 1 is not ∀
        line1 = ProofLineObj('1', '∃x∈S H(x)', 'Premise')
        line2 = ProofLineObj('2', 'H(a)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The root operand of line 1 should be the universal quantifier (∀)')

        # Test where line 1 and line 2 refer to different predicates
        line1 = ProofLineObj('1', '∀x∈S H(x)', 'Premise')
        line2 = ProofLineObj('2', 'G(a)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The expressions on lines 1 and 2 do not refer to the same predicate')

        # Test where line 1 and 2 have different number of inputs
        line1 = ProofLineObj('1', '∀x∈S H(x, y)', 'Premise')
        line2 = ProofLineObj('2', 'H(a)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The predicates on lines 1 and 2 do not have the same number of inputs')

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈S H(x)', 'Premise')
        line2 = ProofLineObj('2', 'H(y)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Instances of variable "x" on line 1 should replace a name on line 2')

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈S H(x, x)', 'Premise')
        line2 = ProofLineObj('2', 'H(a, b)', '∀E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: All instances of variable "x" on line 1 should replace the same name on line 2')


    def test_universal_intro(self):
        rule = UniversalIntro()
        parser = folparser.parser

        # Test with valid input
        line1 = ProofLineObj('1.1', 'P(a)', 'Assumption')
        line2 = ProofLineObj('2', 'P(a)→P(a)', '→I 1')
        line3 = ProofLineObj('3', '∀x∈U (P(x)→P(x))', '∀I 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with reference to a generic free variable
        line1 = ProofLineObj('1', 'P(a)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S P(x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The name "a" on line 1 must be a generic free variable')

        # Test where root operand of line 2 is not ∀
        line1 = ProofLineObj('1', 'H(a)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S H(x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The root operand of line 1 should be the universal quantifier (∀)')

        # Test where line 1 and line 2 refer to different predicates
        line1 = ProofLineObj('1', 'G(a)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The expressions on lines 1 and 2 do not refer to the same predicate')

        # Test where line 1 and 2 have different number of inputs
        line1 = ProofLineObj('1', 'H(a, b)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The predicates on lines 1 and 2 do not have the same number of inputs')

        # Test where the variable on line 2 does not replace a name on line 1
        line1 = ProofLineObj('1', 'H(y)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Instances of variable "x" on line 2 should replace a name on line 1')

        # Test where the variables on line 2 replace two different names on line 1
        line1 = ProofLineObj('1', 'H(a, b)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x, x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: All instances of variable "x" on line 2 should replace the same name on line 1')

        # Test where the variable on line 2 already appears on line 1
        line1 = ProofLineObj('1', 'H(a, x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x, x)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Variable "x" on line 2 should not appear on line 1')

        # Test where the variable on line 2 already appears on line 1
        line1 = ProofLineObj('1', 'H(a, a, b)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S H(x, y, b)', '∀I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        # self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: All instances of name "a" on line 1 should be replaced with the bound variable "x" on line 2')


    def test_conversion_of_quantifiers(self):
        """
        Verify that Conversion of Quantifiers (CQ) is working properly
        """
        rule = ConversionOfQuantifiers()
        parser = folparser.parser

        ### Case 1

        # Test with valid input
        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where line 1 is not a negation
        line1 = ProofLineObj('1', '∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with a universal quantifier (∀), '\
            'it should be followed by a negation (¬) when applying Conversion of Quantifiers (CQ)')

        # Test where line 2 is not the negation of an existential quantifier
        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with a universal quantifier (∀), '\
            'then line 2 should be the negation (¬) of an existential quantifier (∃) '\
            'when applying Conversion of Quantifiers (CQ)')

        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with a universal quantifier (∀), '\
            'then line 2 should be the negation (¬) of an existential quantifier (∃) '\
            'when applying Conversion of Quantifiers (CQ)')

        # Test where line 1 and line 2 refer to different predicates
        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃x∈S G(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Lines 1 and 2 should refer to the same predicate')

        # Test where line 1 and line 2 have different number of inputs
        line1 = ProofLineObj('1', '∀x∈S ¬F(x, a)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The predicates on lines 1 and 2 do not have the same number of inputs')

        # Test where line 1 and line 2 refer to different variables
        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃y∈S F(y)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same variable')

        # Test where line 1 and line 2 refer to different domains
        line1 = ProofLineObj('1', '∀x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∃x∈U F(y)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same domain')

        ### Case 3

        # Test with valid input
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where line 1 does not include a negation
        line1 = ProofLineObj('1', '∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with an existential quantifier (∃), '\
            'it should be followed by a negation (¬) when applying Conversion of Quantifiers (CQ)')

        # Test where line 2 is not the negation of a universal quantifier
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with an existential quantifier (∃), '\
            'then line 2 should be the negation (¬) of a universal quantifier (∀) '\
            'when applying Conversion of Quantifiers (CQ)')

        # Test where line 2 is not the negation of a universal quantifier
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 begins with an existential quantifier (∃), '\
            'then line 2 should be the negation (¬) of a universal quantifier (∀) '\
            'when applying Conversion of Quantifiers (CQ)')

        # Test where line 1 and line 2 refer to different predicates
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀x∈S G(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Lines 1 and 2 should refer to the same predicate')

        # Test where line 1 and line 2 have different number of inputs
        line1 = ProofLineObj('1', '∃x∈S ¬F(x, a)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The predicates on lines 1 and 2 do not have the same number of inputs')

        # Test where line 1 and 2 refer to different variables
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀y∈S F(y)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same variable')

        # Test where line 1 and 2 refer to different domains
        line1 = ProofLineObj('1', '∃x∈S ¬F(x)', 'Premise')
        line2 = ProofLineObj('2', '¬ ∀x∈U F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same domain')

        ### Case 2

        # Test with valid input
        line1 = ProofLineObj('1', '¬ ∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where line 2 does not begin with a universal quantifier
        line1 = ProofLineObj('1', '¬ ∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 is the negation of an existential quantifier, '\
            'then line 2 should begin with a universal quantifier when applying Conversion of Quantifiers (CQ)')

        # Test where the quantifier on line 2 is not followed with a negation
        line1 = ProofLineObj('1', '¬ ∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifier on line 2 should be followed by a negation (¬)')

        # Test with different variables
        line1 = ProofLineObj('1', '¬ ∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀y∈S ¬F(y)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same variable')

        # Test with different domains
        line1 = ProofLineObj('1', '¬ ∃x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈U ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same domain')

        ### Case 4

        # Test with valid input
        line1 = ProofLineObj('1', '¬ ∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where line 2 does not begin with an existential quantifier
        line1 = ProofLineObj('1', '¬ ∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∀x∈S ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: If line 1 is the negation of a universal quantifier, '\
            'then line 2 should begin with an existential quantifier when applying Conversion of Quantifiers (CQ)')

        # Test where the quantifier on line 2 is not followed by a negation
        line1 = ProofLineObj('1', '¬ ∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifier on line 2 should be followed by a negation (¬)')

        # Test where line 1 does not begin with a quantifier or a negation
        line1 = ProofLineObj('1', 'F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈S ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Line 1 must begin with either a quantifier or a negation when applying Conversion of Quantifiers (CQ)')

        # Test with different variables
        line1 = ProofLineObj('1', '¬ ∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃y∈S ¬F(y)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same variable')

        # Test with different domains
        line1 = ProofLineObj('1', '¬ ∀x∈S F(x)', 'Premise')
        line2 = ProofLineObj('2', '∃x∈U ¬F(x)', 'CQ 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The quantifiers on lines 1 and 2 do not refer to the same domain')