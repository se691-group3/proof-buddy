from proofchecker.utils import tflparser, folparser, binarytree #parser needed to create tree, binarytree for Node methods (needed for tree equality)

# new global variable necessary to distinguish variables in expressions
# uncertain about constants so be sure to test those. what about parens?
ZERSYMBOLS = ['⊥']  # also need booleans?  t_BOOL=r'((True)|(TRUE)|(False)|(FALSE)|⊥)'
UNASYMBOLS = ['¬']
BINSYMBOLS = ['∧', '∨', '→', '↔', '∀', '∃'] # not sure how quantifiers are stored in tree. possibly as binary. 
ASSOCS = ['∧', '∨', '↔'] #list of nonunary operations that are associative (and therefore don't require parens in monolithic multiples. e.g A∧B∧C)
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
def instanceOf(genTree:binarytree.Node, specTree:binarytree.Node, env:dict): #env["A"]=exprTree
    # in final version: number of parameters will be determined as an attribute to the operator, not by adhoc lists above
    #TODO still need to append to the environment!  maybe generate separate err msg if doesn't check out
    if genTree==None: #just doing some error catching (hopefully this case shouldn't happen)
        return [specTree==None, env]
    if specTree==None:
        return [False, env]
    genVal = genTree.value
    specVal = specTree.value
    if genVal in ZERSYMBOLS:
        return [genVal == specVal, env]  # must match exactly, no parameters to check
    if genVal in UNASYMBOLS: # e.g. ¬(A∧B)
        if specVal  != genVal: #gen was a ¬ but spec wasn't
            return [False, env]
        return instanceOf(genTree.right, specTree.right, env) # checks what comes after the ¬, which weirdly Colton put in right rather than left
    if genVal in BINSYMBOLS:
        if specVal != genVal: #gen was a ∧ but spec wasn't
            return [False, env]
        #must check here that both left and right work out but NOT independentally, must be done sequentially!!
        resR = instanceOf(genTree.right, specTree.right, env)
        if resR[0]: #both gen and spec are the same bin operation
            return instanceOf(genTree.left, specTree.left, resR[1]) #if right part matches, then check the left
        return [False, resR[1]] # if righthalf part of operation didn't match, no need to check lefthand operand
    #at this stage genTree is a variable
    if genVal in env.keys():
        if env[genVal] == specTree: # apparently __eq__ in binarytree overrides ==, so it does do a proper check. unlike saying "x is y". need binarytree file here!!
            return [True,env] # okay if it matches binding
        return [False, env]   # didn't match binding
    # the only remaining case is that gen is heretofore unseen var, so we set a new binding for it
    env[genVal]=specTree
    return [True,env]