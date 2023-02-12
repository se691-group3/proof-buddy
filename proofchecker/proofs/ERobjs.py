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

# NOTE: lambdas take the ERobj.value, as inputs, not the value itself.
# similarly, lambda output values, not the ERobjs. So, they will need to be
# unwrapped before being passed, and then wrapped up after the return before use.
# these ERobjects are what will be in the data attribute of the RacTree nodes

pcons = ERobj("cons", "function", ("any","list"),"list",None,2)
prest = ERobj("rest", "function", ("list"),"list",None,1)
pfirst = ERobj("first", "function", ("list"),"any",None,1)
padd = ERobj("+", "function", ("int","int"),"int",lambda x,y: x+y,2)
psubtr = ERobj("-", "function", ("int","int"),"int",lambda x,y: x-y,2)
pmult = ERobj("*", "function", ("int","int"),"int",lambda x,y: x*y,2)
pexpt = ERobj("expt", "function", ("int","int"),"int",lambda x,y: x**y,2)
peq = ERobj("=", "function", ("any","any"),"bool",lambda x,y: x==y,2)
pgtr = ERobj(">", "function", ("int","int"),"bool",lambda x,y: x>y,2)
pgtreq = ERobj(">=", "function", ("int","int"),"bool",lambda x,y: x>=y,2)
pless = ERobj("<", "function", ("int","int"),"bool",lambda x,y: x<y,2)
plesseq = ERobj("<=", "function", ("int","int"),"bool",lambda x,y: x<=y,2)
pquotient = ERobj("quotient" "function", ("int","int"),"int",lambda x,y: x//y,2)
prem = ERobj("remainder", "function", ("int","int"),"int",lambda x,y: x%y,2)
pand = ERobj("and", "function", ("bool","bool"),"bool",lambda x,y: x and y,2)
por = ERobj("or", "function", ("bool","bool"),"bool",lambda x,y: x or y,2)
pnot = ERobj("not", "function", ("bool",),"bool",lambda x: not x,1)
pxor = ERobj("xor", "function", ("bool","bool"),"bool",lambda x,y: x!=y,2)
pimp = ERobj("implies", "function", ("bool","bool"),"bool",lambda x,y: (not x) or y,2)
pnullPred = ERobj("null?", "function", ("any",),"bool",lambda x: x==[],1)
pzeroPred = ERobj("zero?", "function", ("any",),"bool",lambda x: x==0,1)
pintPred = ERobj("int?", "function", ("any",),"bool",lambda x: isinstance(x,int),1)
# BUG: might be bug with quoted lists, so better to refer to ERobj.type ?
plistPred = ERobj("list?", "function", ("any",),"bool",lambda x: isinstance(x,list),1)
pnull = ERobj("null", "list", None,None,[],None,0) # first time len attrib not None
ptrue = ERobj("#t", "bool",value=True) 
pfalse = ERobj("#f", "bool",value=False)

#unsure if we should make output be a special kind of list, or if reg list okay?
pquote = ERobj("'", "function", ("list",),"list",[],1) 

# unicode for λ. and technically 2nd input arg should be "sexpr" but no such type
plambda = ERobj("\u03BB", "function", ("list","any"),"function",None,2)

# BAD IDEA b/c need new objects each time since diff childs: sexpr = ERobj("(", "list")

#note: the output type for "if" isn't quite correct. it's really = 3rd arg, not "any"
pif = ERobj("if", "function", ["bool","any","any"],"any",None,3)

#possible problem if they name a variable ERROR, so make sure that gets reserved
perr = ERobj("ERROR", "None")

# TODO: list of the core racket-lite functions (will need to change if add more )
pcore = [pcons, prest, pfirst, padd, psubtr, pmult, pexpt, peq, pgtr, pgtreq,\
    pless, plesseq, pquotient, prem, pand, por, pnot, pxor, pimp, pnullPred,\
        pzeroPred,pintPred, plistPred, pnull, ptrue,pfalse,pquote,plambda,pif,perr]

# making a look-up table of ERobj by string name
pdict ={}
for x in pcore:
    pdict[x.name]=x

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