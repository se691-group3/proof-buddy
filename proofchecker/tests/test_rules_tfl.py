from django.test import TestCase

from proofchecker.proofs.proofobjects import ProofObj, ProofLineObj
from proofchecker.rules.assumption import Assumption
from proofchecker.rules.biconditionalelim import BiconditionalElim
from proofchecker.rules.biconditionalintro import BiconditionalIntro
from proofchecker.rules.conditionalelim import ConditionalElim
from proofchecker.rules.conditionalintro import ConditionalIntro
from proofchecker.rules.conjunctionintro import ConjunctionIntro
from proofchecker.rules.conjunctionelim import ConjunctionElim
from proofchecker.rules.demorgan import DeMorgan
from proofchecker.rules.disjunctionintro import DisjunctionIntro
from proofchecker.rules.disjunctionelim import DisjunctionElim
from proofchecker.rules.dubnegintro import DubNegIntro #ADDED THIS ONE
from proofchecker.rules.disjunctivesyllogism import DisjunctiveSyllogism
from proofchecker.rules.doublenegationelim import DoubleNegationElim
from proofchecker.rules.excludedmiddle import ExcludedMiddle
from proofchecker.rules.explosion import Explosion
from proofchecker.rules.indirectproof import IndirectProof
from proofchecker.rules.modustollens import ModusTollens
from proofchecker.rules.negationelim import NegationElim
from proofchecker.rules.negationintro import NegationIntro
from proofchecker.rules.premise import Premise
from proofchecker.rules.reiteration import Reiteration

from proofchecker.rules.rulechecker import RuleChecker
from proofchecker.utils import tflparser


class RuleCheckerTests(TestCase):

    def test_get_rule(self):
        proof = ProofObj()
        checker = RuleChecker()
        str1 = '∧E'
        str2 = '∨I'
        str3 = '¬E'
        str4 = '↔I'
        str5 = '↔E'
        self.assertTrue(isinstance(checker.get_rule(str1, proof), ConjunctionElim))
        self.assertTrue(isinstance(checker.get_rule(str2, proof), DisjunctionIntro))
        self.assertTrue(isinstance(checker.get_rule(str3, proof), NegationElim))
        self.assertTrue(isinstance(checker.get_rule(str4, proof), BiconditionalIntro))
        self.assertTrue(isinstance(checker.get_rule(str5, proof), BiconditionalElim))


class BasicRuleTests(TestCase):

    def test_premise(self):
        rule = Premise()
        parser = tflparser.parser

        # Test with proper input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(premises=['A', 'B'], lines=[line1, line2, line3])
        result1 = rule.verify(line1, proof, parser)
        result2 = rule.verify(line2, proof, parser)
        self.assertTrue(result1.is_valid)
        self.assertTrue(result2.is_valid)
    
        # Test with a line not in premises    
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(premises='A', lines=[line1, line2, line3])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Expression on line 2 is not a premise")

        # Test with a line not found in multiple premises input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'C', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(premises=['A', 'B'], lines=[line1, line2, line3])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Expression on line 2 not found in premises")

        # Test with an invalid premise    
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B∧', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(premises='A', lines=[line1, line2, line3])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: One or more premises is invalid")

    def test_assumption(self):
        """
        Test that the function verify_assumption is working properly
        """
        rule = Assumption()
        parser = tflparser.parser
        
        # Test with valid input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2.1', 'B', 'Assumption')
        line3 = ProofLineObj('2.2', 'A∧B', '∧I 1, 2')
        proof = ProofObj(premises='A', lines=[line1, line2, line3])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with invalid input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2.1', 'B', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        proof = ProofObj(premises='A', lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2.2: Assumptions can only exist at the start of a subproof')

        # Test with assumption on line 1
        line1 = ProofLineObj('1', 'A', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'R 1')
        proof = ProofObj(premises='A', lines=[line1, line2])
        result = rule.verify(line1, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 1: Assumptions can only exist at the start of a subproof')

    def test_conjunction_intro(self):
        rule = ConjunctionIntro()
        parser = tflparser.parser
        
        # Test with proper input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with invalid conjunction
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'C', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: The conjunction of lines 1 and 2 does not equal line 3")

        # Test with invalid line specification
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', 'A∧B', '∧I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: Line numbers are not specified correctly.  Conjunction Introduction: ∧I m, n")    
    
    def test_conjunction_elim(self):
        rule = ConjunctionElim()
        parser = tflparser.parser

        # Test with proper input
        line1 = ProofLineObj('1', 'A∧B', 'Premise')
        line2 = ProofLineObj('2', 'A', '∧E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)

        line1 = ProofLineObj('1', '(A∧C)∨(B∧C)', 'Premise')
        line2 = ProofLineObj('2.1', 'A∧C', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', '∧E 2.1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with wrong symbol on line 1
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2', 'A', '∧E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 1: The root operand should be ∧ when applying ∧E "\
                        + "(currently the root operand is ∨)")

        # Test with invalid conclusion
        line1 = ProofLineObj('1', 'A∧B', 'Premise')
        line2 = ProofLineObj('2', 'C', '∧E 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Line 2 does not follow from line 1")

    def test_disjunction_intro(self):
        rule = DisjunctionIntro()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'A∨B', '∨I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with invalid conclusion
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B∨C', '∨I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Line 2 does not follow from line 1")

        # Test with invalid line citation
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'A∨B', '∨I 3')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)

#***ADDED THIS ONE:
    def test_doubleNegIntro(self): 
        rule = DubNegIntro()
        parser = tflparser.parser
        # Test with valid input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', '¬¬A', '¬¬I 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
#***ALSO TEST SOME INVALID CASES LATER

    def test_disjunction_elim(self): 
        rule = DisjunctionElim()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2.1', 'A', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'B', 'Assumption')
        line5 = ProofLineObj('3.2', 'C', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertTrue(result.is_valid)

        # Test where root value is not ∨
        line1 = ProofLineObj('1', 'A∧B', 'Premise')
        line2 = ProofLineObj('2.1', 'A', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'B', 'Assumption')
        line5 = ProofLineObj('3.2', 'C', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 1: The root operand should be ∨ when applying ∨E (currently the root operand is ∧)")

        # Test with unequivalent expressions
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2.1', 'A', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'B', 'Assumption')
        line5 = ProofLineObj('3.2', 'D', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 4: The expressions on lines 2.2, 3.2 and 4 are not equivalent")

        # Test with improper disjunction
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2.1', 'A', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'D', 'Assumption')
        line5 = ProofLineObj('3.2', 'C', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 4: The expression on line 3.1 is not part of the disjunction on line 1")

        # Test with improper disjunction
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2.1', 'D', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'B', 'Assumption')
        line5 = ProofLineObj('3.2', 'C', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 4: The expression on line 2.1 is not part of the disjunction on line 1")

        # Test with only one half of disjunction
        line1 = ProofLineObj('1', 'A∨B', 'Premise')
        line2 = ProofLineObj('2.1', 'A', 'Assumption')
        line3 = ProofLineObj('2.2', 'C', 'Assumption')
        line4 = ProofLineObj('3.1', 'A', 'Assumption')
        line5 = ProofLineObj('3.2', 'C', 'Assumption')
        line6 = ProofLineObj('4', 'C', '∨E 1, 2, 3')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5, line6])
        result = rule.verify(line6, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 4: The expressions on lines 2.1 and 3.1 should be different")


    def test_negation_intro(self):
        rule = NegationIntro()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1.1', 'A', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'Premise')
        line3 = ProofLineObj('2', '¬A', '¬I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test without contradiction
        line1 = ProofLineObj('1.1', 'A', 'Premise')
        line2 = ProofLineObj('1.2', 'B', 'Premise')
        line3 = ProofLineObj('2', '¬A', '¬I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)   
        self.assertEqual(result.err_msg, "Error on line 2: Line 1.2 should be '⊥' (Contradiction)")

        # Test without proper negation
        line1 = ProofLineObj('1.1', 'A', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'Premise')
        line3 = ProofLineObj('2', '¬B', '¬I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)   
        self.assertEqual(result.err_msg, "Error on line 2: Line 2 is not the negation of line 1.1")


    def test_negation_elim(self):
        rule = NegationElim()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', '¬A', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', '⊥', '¬E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test without contradiction
        line1 = ProofLineObj('1', '¬A', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'B', '¬E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: Line 3 should be '⊥' (Contradiction)")

        # Test without proper contradiction
        line1 = ProofLineObj('1', '¬A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', '⊥', '¬E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: Line 1 is not the negation of line 2")

        # Test with improper line specification
        line1 = ProofLineObj('1', '¬A', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', '⊥', '¬E 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: Line numbers are not specified correctly.  Negation Elimination: ¬E m, n")


    def test_conditional_intro(self):
        rule = ConditionalIntro()
        parser = tflparser.parser
        
        # Test with valid input
        line1 = ProofLineObj('1.1', 'A∧B', 'Premise')
        line2 = ProofLineObj('1.2', 'B', '∧E 1.1')
        line3 = ProofLineObj('2', '(A∧B)→B', '→I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with invalid input
        line1 = ProofLineObj('1.1', 'A∧B', 'Premise')
        line2 = ProofLineObj('1.2', 'B', '∧E 1.1')
        line3 = ProofLineObj('2', '(A∧B)→C', '→I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: The expressions on lines 1.1 and 1.2 do not match the implication on line 2')

        # Test with invalid citation
        line1 = ProofLineObj('1.1', 'A∧B', 'Premise')
        line2 = ProofLineObj('1.2', 'B', '∧E 1.1')
        line3 = ProofLineObj('2', '(A∧B)→B', '→I 3')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)

        # Test with subproof ending with another subproof
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2.1', 'B', 'Assumption')
        line3 = ProofLineObj('2', 'A→B', '→I 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertEqual(result.err_msg, 'Error on line 2: The expressions on lines 1.1 and 1.1 do not match the implication on line 2')


    def test_conditional_elim(self):
        rule = ConditionalElim()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'A∧B', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'B', '→E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 1: The root operand should be → when applying →E (currently the root operand is ∧)")

        # Test where root is not →
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'B', '→E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with invalid elimination
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'C', '→E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The expressions on lines 2 and 3 do not match the implication on line 1')

        # Test with improper line specification
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'B', '→E 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Line numbers are not specified correctly.  Conditional Elimination (Modus Ponens): →E m, n')


    def test_biconditional_intro(self):
        rule = BiconditionalIntro()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔B', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with valid input (all equiv)
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'A', 'Assumption')
        line3 = ProofLineObj('2.1', 'A', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔A', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with unequivalent expressions
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'C', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔B', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The expressions on lines 1.2 and 2.1 are not equivalent')

        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'C', 'Assumption')
        line5 = ProofLineObj('3', 'A↔B', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: The expressions on lines 1.1 and 2.2 are not equivalent')

        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'C↔B', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Left side of line 3 does not equal either of the expressions on lines 1.2 and 2.2')

        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔C', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Right side of line 3 does not equal either of the expressions on lines 1.2 and 2.2')

        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'A', 'Assumption')
        line3 = ProofLineObj('2.1', 'A', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔B', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 3: Invalid introduction on line 3')

        # Test with invalid conclusion
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'B', 'Assumption')
        line4 = ProofLineObj('2.2', 'A', 'Assumption')
        line5 = ProofLineObj('3', 'A↔A', '↔I 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, \
            'Error on line 3: Left side and right side of line 3 are equivalent, but lines 1.1 and 1.2 are not equivalent')


    def test_biconditional_elim(self):
        rule = BiconditionalElim()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'A↔B', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'Assumption')
        line3 = ProofLineObj('3', 'B', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        line1 = ProofLineObj('1', 'A↔B', 'Assumption')
        line2 = ProofLineObj('2', 'B', 'Assumption')
        line3 = ProofLineObj('3', 'A', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test where root of line m is not ↔ 
        line1 = ProofLineObj('1', 'A∧B', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'Assumption')
        line3 = ProofLineObj('3', 'B', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 1: The root operand should be ↔ when applying ↔E (currently the root operand is ∧)")

        # Test with invalid input
        line1 = ProofLineObj('1', 'A↔B', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'Assumption')
        line3 = ProofLineObj('3', 'A', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: The expressions on lines 2 and 3 do not represent both the left and right side of the expression on line 1")

        # Test with invalid input
        line1 = ProofLineObj('1', 'A↔B', 'Assumption')
        line2 = ProofLineObj('2', 'C', 'Assumption')
        line3 = ProofLineObj('3', 'A', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: The expression on line 2 does not represent the left or right side of the expression on line 1")

        # Test with invalid input
        line1 = ProofLineObj('1', 'A↔B', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'Assumption')
        line3 = ProofLineObj('3', 'C', '↔E 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 3: The expression on line 3 does not represent the left or right side of the expression on line 1")


    def test_indirect_proof(self):
        rule = IndirectProof()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1.1', '¬A', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'X')
        line3 = ProofLineObj('2', 'A', 'IP 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)

        # Test without contradition
        line1 = ProofLineObj('1.1', '¬A', 'Premise')
        line2 = ProofLineObj('1.2', 'B', 'Premise')
        line3 = ProofLineObj('2', 'A', 'IP 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Line 1.2 should be '⊥' (Contradiction)")

        # Test with improper negation
        line1 = ProofLineObj('1.1', '¬A', 'Premise')
        line2 = ProofLineObj('1.2', '⊥', 'Premise')
        line3 = ProofLineObj('2', 'B', 'IP 1')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Line 1.1 is not the negation of line 2")


    def test_explosion(self):
        rule = Explosion()
        parser = tflparser.parser

        # Test with proper input
        line1 = ProofLineObj('1', '⊥', 'Premise')
        line2 = ProofLineObj('2', 'B', 'X 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test without contradiction
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'X 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: Line 1 should be '⊥' (Contradiction)")

        # Test with invalid line citation
        line1 = ProofLineObj('1', '⊥', 'Premise')
        line2 = ProofLineObj('2', 'B', 'X 3')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)


class DerivedRuleTests(TestCase):

    def test_reiteration(self):
        rule = Reiteration()
        parser = tflparser.parser

        # Test with proper input
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'A', 'R 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)

        # Test with unequivalent expressions
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'B', 'R 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Lines 1 and 2 are not equivalent')

        # Test with invalid line citation
        line1 = ProofLineObj('1', 'A', 'Premise')
        line2 = ProofLineObj('2', 'A', 'R 3')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)


    def test_double_negation_elim(self):
        rule = DoubleNegationElim()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', '¬¬A', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'DNE 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.err_msg, None)

        # Test with invalid input
        line1 = ProofLineObj('1', '¬¬A', 'Assumption')
        line2 = ProofLineObj('2', 'B', 'DNE 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Lines 1 and 2 are not equivalent')

        # Test with invalid input
        line1 = ProofLineObj('1', '¬A', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'DNE 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, 'Error on line 2: Line 1 is not an instance of double-not operators')

        # Test with invalid input
        line1 = ProofLineObj('1', 'A^B', 'Assumption')
        line2 = ProofLineObj('2', 'A', 'DNE 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.err_msg, "Error on line 2: The main logical operator on line 1 is not '¬'")


    def test_disjunctive_syllogism(self):
        rule = DisjunctiveSyllogism()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', '~A', 'Premise')
        line3 = ProofLineObj('3', 'B', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', '~B', 'Premise')
        line3 = ProofLineObj('3', 'A', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test with line 1 not representing a disjunction
        line1 = ProofLineObj('1', 'A^B', 'Premise')
        line2 = ProofLineObj('2', '~A', 'Premise')
        line3 = ProofLineObj('3', 'B', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The root of line 1 should be a disjunction (∨) when applying disjunctive syllogism')

        # Test with line 2 not representing a negation
        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', 'A', 'Premise')
        line3 = ProofLineObj('3', 'B', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The root of line 2 should be a negation (¬) when applying disjunctive syllogism')

        # Test with line 2 representing a negation, but not of the left or right of line 1
        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', '~C', 'Premise')
        line3 = ProofLineObj('3', 'B', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: Line 2 should be the negation of either the left or right half of line 1')

        # Test with line 3 not representing the left or right of line 1
        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', '~A', 'Premise')
        line3 = ProofLineObj('3', 'C', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: Line 3 should be equivalent to either the left or right half of line 1')

        # Test with lines 2 and 3 representing same atomic sentence
        line1 = ProofLineObj('1', 'AvB', 'Premise')
        line2 = ProofLineObj('2', '~A', 'Premise')
        line3 = ProofLineObj('3', 'A', 'DS 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: Line 2 and line 3 should not represent the same half of the disjunction on line 1')


    def test_modus_tollens(self):
        rule = ModusTollens()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', '~B', 'Premise')
        line3 = ProofLineObj('3', '~A', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test with line 1 not representing an implication
        line1 = ProofLineObj('1', 'A^B', 'Premise')
        line2 = ProofLineObj('2', '~B', 'Premise')
        line3 = ProofLineObj('3', '~A', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The root of line 1 should be an implication (→) when applying modus tollens')

        # Test with line 2 not representing a negation
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', 'B', 'Premise')
        line3 = ProofLineObj('3', '~A', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The root of line 2 should be a negation (¬) when applying modus tollens')

        # Test with line 3 not representing a negation
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', '~B', 'Premise')
        line3 = ProofLineObj('3', 'A', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The root of line 3 should be a negation (¬) when applying modus tollens')

        # Test with line 2 representing negation of wrong half (left) of line 1
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', '~A', 'Premise')
        line3 = ProofLineObj('3', '~A', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: Line 2 should be the negation of the right half of line 1')

        # Test with line 3 representing negation of wrong half (right) of line 1
        line1 = ProofLineObj('1', 'A→B', 'Premise')
        line2 = ProofLineObj('2', '~B', 'Premise')
        line3 = ProofLineObj('3', '~B', 'MT 1, 2')
        proof = ProofObj(lines=[line1, line2, line3])
        result = rule.verify(line3, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: Line 3 should be the negation of the left half of line 1')


    def test_excluded_middle(self):
        rule = ExcludedMiddle()
        parser = tflparser.parser

        # Test with valid input
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', '¬A', 'Assumption')
        line4 = ProofLineObj('2.2', 'B', 'Assumption')
        line5 = ProofLineObj('3', 'B', 'LEM 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        
        # Test where line j.1 does not negate i.1 input
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', '¬B', 'Assumption')
        line4 = ProofLineObj('2.2', 'B', 'Assumption')
        line5 = ProofLineObj('3', 'B', 'LEM 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The expression on line 2.1 should be the negation of line 1.1')

        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', 'C', 'Assumption')
        line4 = ProofLineObj('2.2', 'B', 'Assumption')
        line5 = ProofLineObj('3', 'B', 'LEM 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The expression on line 2.1 should be the negation of line 1.1')

        # Test where lines i.x and j.x are not equivalent
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', '¬A', 'Assumption')
        line4 = ProofLineObj('2.2', 'C', 'Assumption')
        line5 = ProofLineObj('3', 'B', 'LEM 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The expressions on lines 1.2 and 2.2 should be equivalent')

        # Test where lines i.x and j.x are not equivalent to current line
        line1 = ProofLineObj('1.1', 'A', 'Assumption')
        line2 = ProofLineObj('1.2', 'B', 'Assumption')
        line3 = ProofLineObj('2.1', '¬A', 'Assumption')
        line4 = ProofLineObj('2.2', 'B', 'Assumption')
        line5 = ProofLineObj('3', 'C', 'LEM 1, 2')
        proof = ProofObj(lines=[line1, line2, line3, line4, line5])
        result = rule.verify(line5, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 3: The expressions on lines 1.2 and 2.2 should be equivalent to the expression on line 3')

    def test_de_morgan(self):
        rule = DeMorgan()
        parser = tflparser.parser

        ### Case 1
        # Test with valid input
        line1 = ProofLineObj('1', '¬(A∧B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∨¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test where line 2 is not a disjunction
        line1 = ProofLineObj('1', '¬(A∧B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∧¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: If line 1 is the negation of a conjuction, line 2 should be a disjunction (∨) when applying the first De Morgan rule.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬(A∧B)', 'Assumption')
        line2 = ProofLineObj('2', '¬C∨¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 2 should be negations of the atomic sentences on line 1.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬(A∧B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∨¬C', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 2 should be negations of the atomic sentences on line 1.')


        ### Case 2
        # Test with valid input
        line1 = ProofLineObj('1', '¬A∨¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∧B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test where line 2 is not the negation of a conjunction
        line1 = ProofLineObj('1', '¬A∨¬B', 'Assumption')
        line2 = ProofLineObj('2', 'A∧B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: If line 1 is a disjunction, line 2 should be the negation of a conjunction (∧) when applying the second De Morgan rule.')

        # Test where line 2 is not the negation of a conjunction
        line1 = ProofLineObj('1', '¬A∨¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∨B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: If line 1 is a disjunction, line 2 should be the negation of a conjunction (∧) when applying the second De Morgan rule.')

        # Test where the sentences on line 1 are not negations of the sentences on line 2 
        line1 = ProofLineObj('1', '¬A∨¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(C∧B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 1 should be negations of the atomic sentences on line 2.')

        # Test where the sentences on line 1 are not negations of the sentences on line 2 
        line1 = ProofLineObj('1', '¬A∨¬C', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∧B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 1 should be negations of the atomic sentences on line 2.')


        ### Case 3
        # Test with valid input
        line1 = ProofLineObj('1', '¬(A∨B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∧¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test where line 2 is not a conjunction
        line1 = ProofLineObj('1', '¬(A∨B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∨¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: If line 1 is the negation of a disjunction, line 2 should be a conjunction (∧) when applying the third De Morgan rule.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬(A∨B)', 'Assumption')
        line2 = ProofLineObj('2', '¬C∧¬B', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 2 should be negations of the atomic sentences on line 1.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬(A∨B)', 'Assumption')
        line2 = ProofLineObj('2', '¬A∧¬C', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 2 should be negations of the atomic sentences on line 1.')


        ### Case 4
        # Test with valid input
        line1 = ProofLineObj('1', '¬A∧¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∨B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertTrue(result.is_valid)
        self.assertEquals(result.err_msg, None)

        # Test where line 2 is not a disjunction
        line1 = ProofLineObj('1', '¬A∧¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∧B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: If line 1 is a conjunction, line 2 should be the negation of a disjunction (∨) when applying the fourth De Morgan rule.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬A∧¬B', 'Assumption')
        line2 = ProofLineObj('2', '¬(C∨B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 1 should be negations of the atomic sentences on line 2.')

        # Test where the sentences on line 2 are not negations of the sentences on line 1
        line1 = ProofLineObj('1', '¬A∧¬C', 'Assumption')
        line2 = ProofLineObj('2', '¬(A∨B)', 'DeM 1')
        proof = ProofObj(lines=[line1, line2])
        result = rule.verify(line2, proof, parser)
        self.assertFalse(result.is_valid)
        self.assertEquals(result.err_msg, 'Error on line 2: The atomic sentences on line 1 should be negations of the atomic sentences on line 2.')