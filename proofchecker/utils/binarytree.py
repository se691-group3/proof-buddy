# from typing import List used to doing composite types

# Creates an binary tree
# as part of refactoring, this should be an n-ary tree (see children list) with methods that state whether it's a literal of a function call, num of inputs,
# types of inputs and outputs et al

from collections import deque

# new global variable necessary to distinguish variables in expressions
# uncertain about constants so be sure to test those. what about parens?
BINSYMBOLS = ['∧', '∨', '→', '↔'] # not sure how quantifiers are stored in tree. possibly as binary. 
UNASYMBOLS = ['¬', '∀', '∃'] #quantifiers stored in single node as "∀x∈V" with one right child as the scope
ZERSYMBOLS = ['⊥']  # also need booleans?  t_BOOL=r'((True)|(TRUE)|(False)|(FALSE)|⊥)'
ASSOCS = ['∧', '∨', '↔'] #list of nonunary operations that are associative (and therefore don't require parens in monolithic multiples. e.g A∧B∧C)
SYMBOLS = BINSYMBOLS + UNASYMBOLS + ZERSYMBOLS


class Node:
    """
    Represents a node in a binary search tree
    """
    def __init__(self, data):
        self.left = None
        self.value = data
        self.right = None
        self.children = [] # this will be a list of all other children (unfortunately cannot do left, right, since no setters for those)

    def __str__(self):
        return inorder(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
'''
# method of expressions. takes an expression (expr) and a list of bindings (env) and returns ans=#t/#f if self is an instance of expr. returns updated bindings
    def instanceOf(self, expr, env):
        ans = False
        exprTree = make_tree(expr, parser) # this won't work since the tflparser needs Node and causes circular dependency.

        #put stuff here that checks. will need to convert to trees 
        return ans, env'''

def inorder(root: Node):
    """
    Returns a string representation of an in-order tree traversal
    """

    # create an empty stack
    result = ''
    stack = deque()
    # start from the root node (set current node to the root node)
    curr = root
    # if the current node is None and the stack is also empty, we are done
    while stack or curr:
        # if the current node exists, push it into the stack (defer it)
        # and move to its left child
        if curr:
            stack.append(curr)
            curr = curr.left
        else:
            # otherwise, if the current node is None, pop an element from the stack,
            # print it, and finally set the current node to its right child
            curr = stack.pop()
            result += curr.value
            curr = curr.right
    return result

def preorder(root: Node):
    """
    Returns a string representation of a pre-order tree traversal
    """
    result = ''
    stack = deque()
    stack.append(root)
    while len(stack) > 0:
        # Pop the top item from stack and print it
        node = stack.pop()
        result += node.value
         
        # Push right and left children of the popped node
        # to stack
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    
    return result

# An iterative function to do postorder
# traversal of a given binary tree
def postorder(root: Node):
    
    result = ''
    stack = deque()
     
    while(True):
        while(root != None):
            stack.append(root)
            stack.append(root)
            root = root.left
 
        # Check for empty stack
        if (len(stack) == 0):
            break
         
        root = stack.pop()
 
        if (len(stack) > 0 and stack[-1] == root):
            root = root.right
        else:
            result += root.value
            root = None
    
    return result

#  # puts parens around it if not var/constant
def enclose(tree:Node):
    if tree.value in BINSYMBOLS:
        return "("+tree2Str(tree)+")"
    return tree2Str(tree)

#TODO write for more children that just two
# tree is the obj to be printed
def tree2Str(tree:Node):  #unary function Colton put on the RIGHT child rather than the left!!!!
    
    if tree==None or tree.value==None or tree.value=="": #might not be necessary, but just in case!
        return ""
    if tree.value[0] not in (BINSYMBOLS+UNASYMBOLS): #i.e. variable or constant or a predicate like "Pxy" or "P(x,y)"
        return tree.value
    if tree.value[0] in UNASYMBOLS: # i.e. could be lone ¬ or could be "∀x∈V"
        return tree.value+enclose(tree.right)
    # only case left is a binsymbols #TODO this needs to be a loop based on n-ary of root
    else:
        return enclose(tree.left)+tree.value+enclose(tree.right)

def tree_to_string(root: Node, string: list):
    """
    Function to construct string from binary tree
    """

    if root is None:
        return

    # Push the root data as character
    string.append(str(root.value))

    # if leaf node, then return
    if not root.left and not root.right:
        return

    # For left subtree
    string.append('(')
    tree_to_string(root.left, string)
    string.append(')')
 
    # Only if right child is present to avoid extra parenthesis
    if root.right:
        string.append('(')
        tree_to_string(root.right, string)
        string.append(')')


def string_to_tree_helper(start_index, end_index, arr, root):

    if start_index[0] >= end_index:
        return None

    if arr[start_index[0]] == "(":

        if arr[start_index[0]+1] != ")":

            if root.left is None:

                if start_index[0] >= end_index:
                    return

                new_root = Node(arr[start_index[0]+1])
                root.left = new_root
                start_index[0] += 2
                string_to_tree_helper(start_index, end_index, arr, new_root)
 
        else:
            start_index[0] += 2
 
        if root.right is None:

            if start_index[0] >= end_index:
                return
 

            if arr[start_index[0]] != "(":
                start_index[0] += 1
                return
 
            new_root = Node(arr[start_index[0]+1])
            root.right = new_root
            start_index[0] += 2
            string_to_tree_helper(start_index, end_index, arr, new_root)

        else:
            return

    if arr[start_index[0]] == ")":

        if start_index[0] >= end_index:
            return

        start_index[0] += 1

        return

    return


def string_to_tree(string):
 
    root = Node(string[0])
 
    if len(string) > 1:

        start_index = [1]
        end_index = len(string)-1
 
        string_to_tree_helper(start_index, end_index, string, root)
 
    return root