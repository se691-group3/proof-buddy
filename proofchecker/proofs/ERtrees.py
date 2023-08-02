from proofchecker.proofs.ERobjs import *

# unsure if should include map & foldr, since can't do simple ER with them
# same with len, although the basic length property isn't too bad. maybe a rule?
# same with append. maybe let student define them?
#note that "define" is handled separately by the interface. no "cond"
resRac = ["cons", "rest", "first", "+", "-","*","=", ">", ">=", "<",\
          "<=","quotient","remainder","and", "or", "not", "xor", \
          "implies","null?","null","zero?","#t","#f","'", \
          "if","lambda", "int?", "list?", "ERROR","expt"]

testFuncs = ["fact"]

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
    
    # for testing
    def display(self):
        print("data: ", self.data)
        print("path: ", self.path)
        if self.parent == None:
            print("parent: None")
        else:
            print("parent: ", self.parent.data)
        print("children:")
        for i in self.children:
            print(i.data.name)
    
    def __eq__(self, other) ->bool:
        #return str(self)==str(other) would probably also work as a shortcut?
        n=len(self.children)
        if isinstance(other,RacTree):
            # note that checking self.parent == other.parent would cause infinite loop!
            # note that self.data is an ERobj so needed equality checker for that too
            return self.data==other.data and self.path==other.path and \
                n==len(other.children) and \
                    all([self.children[i]==other.children[i] for i in range(n)])     
        return False
    
    # a tree method that fills in all the path attributes for the nodes
    def pathify(self):
        tree = self
        tree.path=[]
        i=-1 #initializing index (gets incremented before assigment)
        currPar = tree
        queue = [x for x in tree.children] #need a deep copy to not destroy root's children record
        while queue != []:
            node = queue[0]
            queue = queue[1:]+node.children
            if id(node.parent) == id(currPar): # need id here to prevent full node checking
                i+=1
            else:
                currPar = node.parent
                i=0
            node.path=node.parent.path+[i]
        return
       
    # given a list of ints, returns node with that path
    def nodeFromPath(self, mylist:list):
        if mylist==[]:
            return self
        ancestor = self.nodeFromPath(mylist[:-1])
        if len(ancestor.children) <= mylist[-1]: #not a valid path
            return errNode #should be okay to use, even tho defined after the class
        return ancestor.children[mylist[-1]]
    
    # a tree method which subs in the given newnode for the old one at path and returns original tree modified
    def replaceNode(self, myPath:list, newNode):
        print("inside replace: ", self, newNode)
        newTree = self #originally made a copy, but then this would not work for a Replace All in a For loop
        oldNode = newTree.nodeFromPath(myPath)
        if oldNode == errNode or oldNode==newTree:
            return
        priorNode = newTree.nodeFromPath(myPath[:-1]) #could have used oldNode.parent
        newNode.parent = priorNode
        priorNode.children[myPath[-1]]=newNode
        newTree.pathify() #otherwise paths of substituted nodes will be wrong
        return newTree
    
    #TODO: fix so test works!
    def condReplace(self,parStr:str, newNode:'RacTree')->'RacTree':
        print("self and new ",self, newNode)
        parent = self.parent
        if self.data.name == parStr: #recall python doesn't check strings for memory location, just if chars are the same. for location use "is"
            self.replaceNode([],newNode)
            self.parent = parent
            print("now: ", self)
        else:
            for child in self.children:
                child.condReplace(parStr,newNode)
        self.pathify()
        return self
    

def copyTree(orig:RacTree)->RacTree: # tree construction is:  data=None, children=None, parent=None, path=None
    if orig is None:
        return None
    copied_node = RacTree(ERcopy(orig.data), [], None, None)
    for child in orig.children:
        copied_child = copyTree(child)
        copied_node.children.append(copied_child)
        copied_child.parent = copied_node
    copied_node.pathify()
    return copied_node


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
    if ch.lower() in testDict.keys():
        return testDict[ch.lower()]
    if ch=="(":
        return ERobj("(","any")
    if is_integer(ch):
        return ERobj(ch,"int",value=int(ch))
    #if not found, then default now instead of an error, is that it's a parameter
    return ERobj(ch, "param")
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
    tree.pathify()
    # all of the below has been made into the tree method "pathify"
    # tree.path=[]
    # i=-1 #initializing index (gets incremented before assigment)
    # currPar = tree
    # queue = [x for x in tree.children] #need a deep copy to not destroy root's children record
    # while queue != []:
    #     node = queue[0]
    #     queue = queue[1:]+node.children
    #     if id(node.parent) == id(currPar): # need id here to prevent full node checking
    #         i+=1
    #     else:
    #         currPar = node.parent
    #         i=0
    #     node.path=node.parent.path+[i]
    return tree

def makeErrTree(msg:str):
    ans=ERcopy(perr)
    ans.value=msg
    return RacTree(ans)
