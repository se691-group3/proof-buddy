from proofchecker.proofs.ERobjs import *
from proofchecker.proofs.ERtrees import *

#take a racket tree, and a lookup dictionary of defines (not yet implemented), and returns a simplified ractree of just the outermost eval



def eval(origTree:RacTree, myPath:list, lookup:dict)->RacTree:
    # note that for delta-reductions (i.e. definitions) the path pointer is
    # at the label, whereas for evals it would be on the paren before the function
    myTree = copyTree(origTree) #this is to return a brand new tree, not just modify the original input tree
    currNode = myTree.nodeFromPath(myPath)
    currName=currNode.data.name
    if currName in lookup.keys():
        return myTree.replaceNode(myPath,lookup[currName])
    if currName == "(" and currNode.children[0].data.name=="(" and currNode.children[0].children[0].data.name=="λ":
        if len(currNode.children[0].children) != 3: #zeroth child is the lambda
            return makeErrTree("λ must take two arguments, a list and a racket expression")
        if currNode.children[0].children[1].data.name != "(":
            return makeErrTree("λ the first argument of λ should be a list of parameters")
        ans = betaReduct(myTree, myPath)
        
        # numArgs = len(currNode.children)-1
        # funcNode = currNode.children[0]
        # funcER = funcNode.data
        return RacTree(str2ER("42"))
    return myTree

# takes a tree and a node(path) which is a "(". the 
# note: cannot evaluate the (λ itself since that would just return the same anonymous function
# output is the original tree but with the"(" node replaced with the substitution
def betaReduct(origTree:RacTree,myPath:list)->RacTree: #need to pass path not node, since we'll need to access the equivalent spot in copy
    newTree = copyTree(origTree)
    currNode = origTree.nodeFromPath(myPath)    
    altCurrNode = newTree.nodeFromPath(myPath)
    paramNodes = currNode.children[0].children[1].children #list of parameter nodes
    numPars = len(paramNodes)
    numArgs = len(currNode.children)-1 # minus 1 is due to the "(λ" at start of expr
    if numPars != numArgs:
        return makeErrTree("anonymous function expected "+str(numPars)+" parameters, but there were "+str(numArgs)+" arguments")
    parDict={} #index is string name (since must be immutable), value is the node of replacement
    for index in range(numPars):
        par = paramNodes[index]
        if par.data.pbType !="param":
            return makeErrTree("λ the first argument of λ should be a list of parameters")
        parDict[par.data.name]=currNode.children[index+1] #again, +1 is due to the "(λ" at start. 
        # remember when use dict for replacing to make copies or else paths will overwrite each other for multiples
    sexpr = currNode.children[0].children[2] #this node of the tree is the s-expr definition of the function


    
    
    return newTree
