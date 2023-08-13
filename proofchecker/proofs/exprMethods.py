from proofchecker.utils import tflparser, folparser, binarytree #parser needed to create tree, binarytree for Node methods (needed for tree equality)
from proofchecker.utils.binarytree import tree2Str #used for testing

# new global variable necessary to distinguish variables in expressions
# uncertain about constants so be sure to test those. what about parens?
ZERSYMBOLS = ['⊥']  # also need booleans?  t_BOOL=r'((True)|(TRUE)|(False)|(FALSE)|⊥)'
UNASYMBOLS = ['¬','∀', '∃'] # quantifiers are stored in a single node as "∃x∈V" with scope as its single right child. 
BINSYMBOLS = ['∧', '∨', '→', '↔'] 
ASSOCS = ['∧', '∨', '↔'] #list of nonunary operations that are associative (and therefore don't require parens in monolithic multiples. e.g A∧B∧C)
PREDS = list("ABCDEFGHIJKLMNOPQR")
SETS = list("STUVWXYZ")
OBJS = [s.lower() for s in PREDS]
VARS = [s.lower() for s in SETS]
SYMBOLS =  ZERSYMBOLS + UNASYMBOLS + BINSYMBOLS

# takes general expressiontree and a specific expressiontree and a dictionary of already known vars, and returns [boolean, updated env]

# expr is a string expression, n=0 TFL, n=1 FOL.  TODO will need a better system for a general parser (table lookup or class attribute?)
def myMakeTree(expr:str, n:int)->binarytree.Node: 
    if n==0:
        return tflparser.parser.parse(expr, lexer=tflparser.parser.lexer)
    if n==1:
        return folparser.parser.parse(expr, lexer=folparser.parser.lexer)
    
# gen is the expression in general (i.e. from the new rule), where spec is the specific case we want to check validity on
# need to do parameters as trees rather than strings, so can recurse on children!
# returns [boolean err flag, updated env], env meaningless if flag=False
#added optional parameter (to be consistent with older TFL calls) that handles FOL
def instanceOf(genTree:binarytree.Node, specTree:binarytree.Node, env:dict,fol=False): #env["A"]=exprTree for TFL, and env["x"]="a" for FOL
    # in final version: number of parameters will be determined as an attribute to the operator, not by adhoc lists above
    if genTree==None: #just doing some error catching (hopefully this case shouldn't happen)
        return [specTree==None, env]
    if specTree==None:
        return [False, env]
    genVal = genTree.value
    specVal = specTree.value
    if genVal in ZERSYMBOLS:
        return [genVal == specVal, env]  # must match exactly, no parameters to check
    if (genVal in UNASYMBOLS) or genVal[0] in UNASYMBOLS: # e.g. ¬(A∧B) or it's a quantifier like 
        if specVal  != genVal: #gen was a ¬ but spec wasn't. or for fol, if any part of quants, domains, or bound variable names don't match
            return [False, env]
        return instanceOf(genTree.right, specTree.right, env, fol) # checks what comes after the ¬, which weirdly Colton put in right rather than left
        
    if fol and genVal[0] in PREDS: 
        genVar = genVal[1]
        if specVal[0] != genVal[0]: #predicates must match
            return [False,env]
        freeVar = specVal[1] # at this stage, we know both general and specific are the same preds
        if freeVar in VARS and freeVar != genVar: #can't change a bound var to a different bound variable (could it even be bound at all?)
            return [False, env]
        if genVar in OBJS:
            return [genVar == freeVar, env] #checks if both the free vars were the same or not
        if genVar in env.keys(): #note: cannot use the later copy of being the keys, since needs [1] here not whole thing
            return [env[genVar]==freeVar, env] #checks if the previously seen bound var matches to previous seen free var
        if freeVar in OBJS: #originally inadvertently omitted, which caused error for other bound vars besides current one being instantiated
            env[genVar]=freeVar #increase enviroment to include new member. 
        return [True, env]

    if genVal in BINSYMBOLS:
        if specVal != genVal: #gen was a ∧ but spec wasn't
            return [False, env]
        #must check here that both left and right work out but NOT independentally, must be done sequentially!!
        resR = instanceOf(genTree.right, specTree.right, env, fol)
        if resR[0]: #both gen and spec are the same bin operation
            return instanceOf(genTree.left, specTree.left, resR[1],fol) #if right part matches, then check the left
        return [False, resR[1]] # if righthalf part of operation didn't match, no need to check lefthand operand
    #at this stage genTree is a variable
    if genVal in env.keys():
        if env[genVal] == specTree: # apparently __eq__ in binarytree overrides ==, so it does do a proper check. unlike saying "x is y". need binarytree file here!!
            return [True,env] # okay if it matches binding
        return [False, env]   # didn't match binding
    # the only remaining case is that gen is heretofore unseen var, so we set a new binding for it
    env[genVal]=specTree
    return [True,env]