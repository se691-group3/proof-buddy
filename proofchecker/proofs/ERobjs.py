ERtypes = ["int", "bool", "list", "any", "None", "function"] #any is used for function arguments, None is used for output of thunks

class ERobj:
    def __init__(self, name, pbType, ins=None, outType=None, value=None, numArgs=None, length=None):
        self.name = name # the string label
        self.pbType = pbType # from PBtypes
        self.ins = ins #for functions, it's the tuple of input types
        self.outtype = outType # for functions, it's the output type
        self.numArgs = numArgs # for functions, it's the number of inputs
        self.length = length # for lists, it's the length 
        self.value = value # for ints/bools/lists this is a wrapper. for functions it's the lambda expression of it's def. 
        #value is the function that tells what happens when it gets evaluated
    def __str__(self):
        return str(self.name)

cons = ERobj("cons", "function", ["any","list"],"list",[],2,None)
err = ERobj("ERROR", "None")

def isValidType(t) -> bool: #checks if a given string/list is a valid Equational Reasoning type (tricky due to functions)
    #( list of input types, output type)
    if t in ERtypes: 
        return True
    if not(isinstance(t,tuple) and len(t) == 2 and isValidType(t[1]) and isinstance(t[0],list)):
        return False
    return  isTypesList(t[0])
    
def isTypesList(L:list) -> bool: #checks that every element of a list is a valid type, needed to check inputs
    if not(isinstance(L,list)):
        return False
    if L==[]:
        return True
    return isValidType(L[0]) and isTypesList(L[1:])

def funType2Str(t) -> str: #method used in testing to print a type
    if t in ERtypes:
        return t
    if isinstance(t,list):
        if len(t)==1:         # preventing parens around a single items
            return t[0]
        ans="("
        for x in t:
            ans+=funType2Str(x)+", "
        return ans[:-2]+")"              # removes last comma
    if isinstance(t,tuple):
        return "("+funType2Str(t[0])+" --> "+funType2Str(t[1])+")"
    return "ERROR"

def type2Str(t) -> str:
    if not(isValidType(t)):
        return "ERROR"
    if t in ERtypes:
        return t
    return funType2Str(t)[1:-1] #dropping outermost parens