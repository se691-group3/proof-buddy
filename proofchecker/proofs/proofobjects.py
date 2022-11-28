# from proofchecker.proofs.proofchecker import verify_proof #CANNOT USE THIS SINCE IT DEPENDS ON THIS CLASS
import json # needed to save/load proofs as json files

class ProofLineObj:

    def __init__(self, line_no=None, expression=None, rule=None): #really rule should be type ProofRule, but keeping string for now until fully refactored
        #similarly, expression should type ProofExpression (an nary tree with methods) but keeping string for now. all these attribs are strings!
        self.line_no = line_no
        self.expression = expression
        self.rule = rule
    
    def __str__(self):
        return ('Line {}: {}, {}'.format(
            self.line_no,
            self.expression,
            self.rule
        ))
    
    def strList(self):  #returns a list of strings useful for JSON
        return [self.line_no, self.expression, self.rule]
    
    def setLineNum(self, myNum):
        self.line_no = myNum
    
    def getLineNum(self):
        return self.line_no

    def setExpr(self, myExpr):
        self.expression = myExpr
    
    def getExpr(self):
        return self.expression

    def setRule(self, myRule):
        self.rule = myRule

    def getRule(self):
        return self.rule  

    def line2Dict(self)->dict:  # a new method of Line objects that is useful for making json files
        return {"lineNum":self.getLineNum(), "expr":self.getExpr(),"rule":self.getRule()}

class ProofObj:
    # added name attribute as part of object (rather than part of gui)
    #note that premises and conclusion are lineObjects not strings!  WAIT: maybe they are strs sometimes, since crashed line2Dict
    def __init__(self, rules='tfl_basic', premises=[], conclusion='', lines=[], created_by='', name="", complete=False):
        self.rules = rules 
        self.ruleList = [] #TODO: for future, this will have to be a list of allowed rules, not a specific string, presently rules='fol_derived' etc
        self.premises = premises
        self.conclusion = conclusion
        self.lines = lines
        self.created_by = created_by
        self.name = name
        self.complete = complete
    
    def __str__(self): #BUG: this could potentially be a problem if old version called this thinking it was getting only lines!
        #result = "Proof: "+self.name+"\n" #added name as a title, but commented out to prevent testing errors based on reading lines
        result=""
        for line in self.lines:
            result += str(line) +'\n'
        return result

    def __iter__(self):
        return (x for x in self.lines)

    def getPremises(self):
        return self.premises

    def getRuleList(self):  # can make a setter later, once the idea becomes more fleshed out
        return self.ruleList
    
    def numPremises(self):
        count = 0
        for line in self.lines:
            if line.rule=="Premise":
                count+=1
        return count

    def getLine(self,n):
        return self.lines[n]

    def setLine(self,n, myLine: ProofLineObj):
        self.lines[n]=myLine

    def getConclusion(self):       
        return self.conclusion
    
    def setConclusion(self, myConclusion: ProofLineObj):
        self.conclusion=myConclusion

    # creates string of a json representation of a proof (later will save it into a filename)
    def saveJson(self): #nothing returned here, it just creates a jsonfile at outfile
        myDict={}
        myDict["name"]=self.name # didn't bother with getters since just strings/bools for these
        myDict["created_by"]=self.created_by
        myDict["complete"]=self.complete
        myDict["rules"]=self.rules #didn't bother with a getter since it will be obsoleted by ruleList eventually
        myDict["ruleList"]=self.getRuleList()
        P=self.getPremises() # this is needed due to inconsistency of premises intially stored as strings rather than line numbers
        myDict["premises"]=[]
        if P == "": # This case is for proofs where there are no premises
            P = []
        if P != []:
            if isinstance(P[0], str):
                for n in range(len(P)):
                    myDict["premises"].append({"lineNum":n+1, "expr":P[n],"rule":"Premise"})
            else:
                myDict["premises"]=[L.line2Dict() for L in P]
        self.setConclusion(self.lines[-1]) # needed since otherwise might be a string rather than a LineObj
        myDict["conclusion"]=self.getConclusion().line2Dict()
        myDict["lines"]=[L.line2Dict() for L in self.lines] #makes a sub dictionary for the lines
        with open(self.name.replace(" ","")+".json",'w') as f:
            json.dump({"Proofs":[myDict]} ,f,indent=2) # format for json files is a dictionary with one item containing a list of dictionaries
        return #nothing to really return

def loadJson(name):
    myProof = ProofObj()
    print("looking for: "+name.replace(" ","")+".json")
    with open(name.replace(" ","")+".json",'r') as f:
        proofDict = json.load(f)["Proofs"][0] # for extensibility, Proofs could theoretically hold multiple possible proofs. for now, just the one
    myProof.name = proofDict["name"]
    myProof.created_by=proofDict["created_by"]
    myProof.complete=proofDict["complete"] #check to make sure this is the constant True and not a string or lowercase true like in the json
    myProof.rules=proofDict["rules"] # will be obsolete once ruleList made
    myProof.ruleList=proofDict["ruleList"] #not yet implemented
    myProof.premises=[] # should already be empty, but initializing just in case of something weird i didn't expect
    for L in proofDict["premises"]:
        myProof.premises.append(ProofLineObj(L["lineNum"],L["expr"],L["rule"]))
    L = proofDict["conclusion"]
    myProof.setConclusion(ProofLineObj(L["lineNum"],L["expr"],L["rule"]))
    myProof.lines=[]
    for L in proofDict["lines"]:
        myProof.lines.append(ProofLineObj(L["lineNum"],L["expr"],L["rule"]))
    return myProof

# making a rule as an extension of a Proof. 
class ProofRule(ProofObj):
    
    def __init__(self, rules='tfl_basic', premises=[], conclusion='', lines=[], created_by='', name=""):
        super().__init__(rules, premises, conclusion, lines, created_by, name)

class ProofResponse:

    def __init__(self, is_valid=False, err_msg=None):
        self.is_valid = is_valid
        self.err_msg = err_msg