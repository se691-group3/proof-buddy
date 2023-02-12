from proofchecker.proofs.ERobjs import *

# unsure if should include map & foldr, since can't do simple ER with them
# same with len, although the basic length property isn't too bad. maybe a rule?
# same with append. maybe let student define them?
#note that "define" is handled separately by the interface. no "cond"
resRac = ["cons", "rest", "first", "+", "-","*","=", ">", ">=", "<",\
          "<=","quotient","remainder","and", "or", "not", "xor", \
          "implies","null?","null","zero?","#t","#f","'", \
          "if","lambda", "int?", "list?", "ERROR","expt"]

#needed for checking ints. written by chatGPT
def is_integer(strng:str) -> bool:
    try:
        int(strng)
        return True
    except ValueError:
        return False

class RacTree:
    def __init__(self, data=None, children=None,parent=None,path=None):
        if children==None: #needed since default values can't be mutable in Python
            self.children=[] #list of nodes whose data is the entries in the S-expr. zeroth will be function
        else:
            self.children=children
        if path==None: #see above. otherwise it will be same path for all nodes!
            self.path=[] #a list of integers of how to get to this node.
        else:
            self.path=path
        self.data=data #holds the value of that node, possibly "(" for S-expr which means it has children
        self.parent=parent #pointer back to the parent (technically could be derived from path)
            
    def __str__(self):
        ans="("
        if self.data.name!="(":
            return str(self.data.name)
        for ch in self.children:
            ans+=str(ch)+" "
        return ans[:-1]+")"
    
    # given a list of ints, returns node with that path
    def nodeFromPath(self, mylist:list):
        if mylist==[]:
            return self
        ancestor = self.nodeFromPath(mylist[:-1])
        if len(ancestor.children) <= mylist[-1]: #not a valid path
            return errNode #should be okay to use, even tho defined after the class
        return ancestor.children[mylist[-1]]

errNode = RacTree(perr)

def str2List(expr:str) -> list:
    if expr=="":
        return []
    #note: space needed before ( to account for quote
    expr = expr.replace("]",")").replace("[","(").replace("{","(").replace("}",")").replace("\t"," ").replace("\n"," ").replace("("," ( ").replace(")"," )").strip()
    expList = expr.split()
    #checking for presence of an unquoted empty list
    nospace = expr.replace(" ","")
    for i in range(len(nospace)-1):
        if nospace[i]=="(" and nospace[i+1]==")" and (i==0 or nospace[i-1]!="'"):
            return []
    #check if parens balanced
    count = 0
    for x in expList:
        if x=="(":
            count+=1
        if x==")":
            count-=1
        if count < 0:
            return []
    return expList

#TODO: still a function stub. need lookup table for defined vars, maybe more
def str2ER(ch:str) -> ERobj: 
    #note: don't overwrite ch to lower, in case lookup has uppercase
    if ch.lower()=="lambda":
        ch="\u03BB"
    if ch.lower() in pdict.keys():
        return pdict[ch.lower()]
    if ch=="(":
        return ERobj("(","any")
    if is_integer(ch):
        return ERobj(ch,"int",value=int(ch))
    #the following error should be replaced by a lookup table for definitions
    return perr

# given a list that has a ( and index i, finds the index of the closing )
def findClose(L:list, i:int)->int:
    count = 0
    for j in range(i, len(L)):
        if L[j]=="(":
            count+=1
        elif L[j]==")":
            count-=1
        if count ==0:
            return j
    return -1 # this shouldn't happen

#turns a list of string into a RacTree in a non-recursive way
def makeRtreeHelp(expList:list) -> RacTree:
    if expList==[]: #should never hit this
        return errNode
    i=0 #this is the index currently being looked at
    currPar = None
    while i < len(expList):
        if expList[i]==")": #note: this assumes a wellformed string that doesn't start with )
            currPar = currPar.parent
        else:
            newNode = RacTree(str2ER(expList[i]), children=[],parent=currPar)
            if currPar != None: #only happens for root first time
                currPar.children.append(newNode)
        if expList[i]=="(":            
            currPar = newNode
        if i ==0:
            tree = newNode
        i+=1
    return tree

# does a BFS to assign paths to all nodes of the tree
def makeRtree(expList:list) -> RacTree:
    tree = makeRtreeHelp(expList)
    tree.path=[]
    i=-1 #initializing index (gets incremented before assigment)
    currPar = tree
    queue = [x for x in tree.children] #need a deep copy to not destroy root's children record
    while queue != []:
        node = queue[0]
        queue = queue[1:]+node.children
        if node.parent == currPar:
            i+=1
        else:
            currPar = node.parent
            i=0
        node.path=node.parent.path+[i]
    return tree

def treeTest(): #testing on ((if (zero? 1) + *) 1 2)
    #recall ERobj(data=None, children=[],parent=None,path=[])
    node0 = RacTree(ERobj("(","any"))
    node1 = RacTree(ERobj("(","any"), parent=node0) 
    node4=RacTree(pif,parent=node1)
    node5 = RacTree(ERobj("(","any"),parent=node1)
    node6 = RacTree(padd,parent=node1)
    node7 = RacTree(pmult,parent=node1)
    node1.children=[node4,node5, node6,node7]
    node2 = RacTree(str2ER("1"), parent=node0)
    node3 = RacTree(str2ER("2"),parent=node0)
    node8 = RacTree(pzeroPred, parent=node5)
    node9 = RacTree(str2ER("1"), parent=node5)
    node5.children=[node8,node9]
    node0.children = [node1, node2, node3]
    print("testing tree raw construction:",node0)
    myTree = makeRtree(str2List("((if (zero? 1) + *) 1 2)"))
    print("testing making tree from list:",myTree)
    return