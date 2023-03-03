# will change all these to be instances of "ProofRule.verify()" after creating "FIAT" justification and saving all these rules as proofs

from proofchecker.rules.dubnegintro import DubNegIntro #added these two!
from proofchecker.rules.newrule import NewRule

from proofchecker.proofs.proofobjects import ProofObj
from proofchecker.rules.assumption import Assumption
from proofchecker.rules.biconditionalelim import BiconditionalElim
from proofchecker.rules.biconditionalintro import BiconditionalIntro
from proofchecker.rules.conditionalelim import ConditionalElim
from proofchecker.rules.conditionalintro import ConditionalIntro
from proofchecker.rules.conjunctionelim import ConjunctionElim
from proofchecker.rules.conjunctionintro import ConjunctionIntro
from proofchecker.rules.conversionofquantifiers import ConversionOfQuantifiers
from proofchecker.rules.demorgan import DeMorgan
from proofchecker.rules.disjunctionelim import DisjunctionElim
from proofchecker.rules.disjunctionintro import DisjunctionIntro
from proofchecker.rules.disjunctivesyllogism import DisjunctiveSyllogism
from proofchecker.rules.doublenegationelim import DoubleNegationElim
from proofchecker.rules.equalityelim import EqualityElim
from proofchecker.rules.equalityintro import EqualityIntro
from proofchecker.rules.excludedmiddle import ExcludedMiddle
from proofchecker.rules.existentialelim import ExistentialElim
from proofchecker.rules.existentialintro import ExistentialIntro
from proofchecker.rules.explosion import Explosion
from proofchecker.rules.indirectproof import IndirectProof
from proofchecker.rules.modustollens import ModusTollens
from proofchecker.rules.negationelim import NegationElim
from proofchecker.rules.negationintro import NegationIntro
from proofchecker.rules.premise import Premise
from proofchecker.rules.reiteration import Reiteration
from proofchecker.rules.universalelim import UniversalElim
from proofchecker.rules.universalintro import UniversalIntro
from .rule import Rule


TFL_BASIC_RULES = [Premise(), Assumption(), ConjunctionIntro(), ConjunctionElim(), DisjunctionIntro(), DisjunctionElim(), \
    ConditionalIntro(), ConditionalElim(), BiconditionalIntro(), BiconditionalElim(), NegationIntro(), NegationElim(), \
    Explosion(), IndirectProof(), DubNegIntro()] #added these two last members!!

TFL_DERIVED_RULES = [DisjunctiveSyllogism(), ModusTollens(), DoubleNegationElim(), Reiteration(), ExcludedMiddle(), DeMorgan()]

FOL_BASIC_RULES = [ExistentialElim(), ExistentialIntro(), UniversalElim(), UniversalIntro(), EqualityIntro(), EqualityElim()]

FOL_DERIVED_RULES = [ConversionOfQuantifiers()]

class RuleChecker:

    def get_rule(self, rule: str, proof: ProofObj):
        """
        Determine which rule is being applied
        """
        if rule.casefold() in [x.casefold() for x in proof.getRuleList()]:
            #print("found rule!")
            return NewRule()

        if proof.rules == 'fol_derived':
            for derived_fol_rule in FOL_DERIVED_RULES:
                if rule.casefold() == derived_fol_rule.symbols.casefold():
                    return derived_fol_rule

        if ((proof.rules == 'fol_derived') or (proof.rules == 'fol_basic')):
            for basic_fol_rule in FOL_BASIC_RULES:
                if rule.casefold() == basic_fol_rule.symbols.casefold():
                    return basic_fol_rule

        if ((proof.rules == 'fol_derived') or (proof.rules == 'tfl_derived')):
            for derived_rule in TFL_DERIVED_RULES:
                if rule.casefold() == derived_rule.symbols.casefold():
                    return derived_rule

        for basic_rule in TFL_BASIC_RULES:
            #print("Basic rule for-loop output - ",basic_rule.symbols.casefold())
            if rule.casefold() == basic_rule.symbols.casefold():
                print("entered basic rule conditional with the rule - ",rule.casefold())
                return basic_rule
        # at this point-  the rule is not in any of the above lists so it may be a lemma so will need newRule (further logic to be added)
        if (proof.lemmas_allowed):
            print("entered newRule triggering section with the rule - ",rule.casefold())
            return NewRule()

                
        return None