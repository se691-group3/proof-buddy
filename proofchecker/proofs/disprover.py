from proofchecker.proofs.proofobjects import ProofObj, ProofResponse 
from proofchecker.proofs.proofutils import make_tree
from proofchecker.utils import tflparser
from proofchecker.utils.binarytree import Node#, tree2Str #for testing

'''
to work, the GUI driver needs to have parts that do this:
#from proofchecker.proofs.disprover import makeDict, setVals, checkCntrEx # for new Disprove mode
#from proofchecker.utils import tflparser # might be needed for Disproof testing

    valDict = setVals(makeDict(proof))
    response = checkCntrEx(proof,valDict)
    if response.is_valid:
        print("That is a valid counterexample -- Good Job!")
    else:
        print(response.err_msg)
'''
# dictionary of binary operations corresponding to the string symbols
opDict={}
opDict['∧']=lambda x,y: x and y
opDict['∨']=lambda x,y: x or y
opDict['→']=lambda x,y: not x or y
opDict['↔']=lambda x,y: x == y

# makes a dictionary of all variables in a proof defaulting values to False
def makeDict(proof: ProofObj):
    notVars={'∧', '∨', '→', '↔','¬','⊥',"(",")"," "}
    prfVars=[]
    myPrems = proof.getPremises() # this is a (possibly empty) list of strings
    for p in myPrems: #this could have been done with a "".join too
        prfVars+=[x for x in p]
    prfVars+=[x for x in proof.getConclusion()]
    prfVars = list(set(prfVars)-notVars)
    valDict={}
    for v in prfVars:
        valDict[v]=False
    return valDict

# dummy function which represents the user setting values for the variables
def setVals(myDict):
    # in reality, there would be a GUI that lets the user set values
    # until the team implements this, it will be hardcoded below
    myDict["A"]=True 
    myDict["B"]=True 
    myDict["C"]=True 
    myDict["D"]=False 
    return myDict

#takes expression tree and dictionary of values and evaluates the expression
def evalExpr(eTree:Node, valDict:dict):
    #eTree = make_tree(expr, tflparser.parser) #note: Disproving only for TFL
    if eTree.value in valDict.keys(): # replace variable with its assigned value
        return valDict[eTree.value]
    # since strings don't contain arg count, must separate based on arity. TODO: refactor
    if eTree.value == "⊥": 
        return False
    if eTree.value == "¬":
        return not(evalExpr(eTree.right, valDict))   
    return opDict[eTree.value](evalExpr(eTree.left,valDict),evalExpr(eTree.right,valDict))

# returns list of indices of premises which aren't valid in the given assignment
def evalPrems(proof:ProofObj, valDict:dict):
    ans=[]
    prems = [make_tree(x,tflparser.parser) for x in proof.getPremises()]
    for i in range(len(prems)):
        if not(evalExpr(prems[i], valDict)): 
            ans.append(i+1)  # could be done with list comprehension, but less clear
    return ans

#returns a proofResponse for the counterexample
def checkCntrEx(proof:ProofObj, valDict:dict):
    ans = ProofResponse(True,"")
    if evalExpr(make_tree(proof.getConclusion(), tflparser.parser), valDict):
        ans.is_valid = False
        ans.err_msg="Conclusion is satisfied, so not a counterexample\n"
    sats = evalPrems(proof, valDict)
    if sats != []:
        ans.is_valid = False
        ans.err_msg+="Invalid counterexample. the following premises were not satisfied: "
        for x in sats:
            ans.err_msg+=str(x)+" "
    return ans