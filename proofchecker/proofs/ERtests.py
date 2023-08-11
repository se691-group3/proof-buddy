from proofchecker.proofs.ERobjs import *
from proofchecker.proofs.ERtrees import *
from proofchecker.proofs.EReval import *
#  this is a test comment

    #testing on ((if (zero? 1) + *) 1 2)
def treeTest1():#recall ERobj(data=None, children=[],parent=None,path=[])
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
    node0.pathify()
    myTree1 = makeRtree(str2List("((if (zero? 1) + *) 1 2)"))
    print("testing tree raw construction:",node0)
    print("testing making tree from list:",myTree1)
    print("testing for tree equality vs just string equality: ",node0==myTree1)

    #testing on (fact 3) with replace
    #treelist is list of trees so far, nodeList is list of node
def treeTest2(treeList:list, myNode:list):#recall ERobj(data=None, children=[],parent=None,path=[])
    #first checking copying
    if treeList==[]:
        treeList = [makeRtree(str2List("(fact 3)"))]
    lookup = {}
    lookup["fact"]=makeRtree(str2List("(λ (n) (if (zero? n) 1 (* n (fact (- n 1)))))"))
    newtree = eval(treeList[-1],myNode,lookup)
    return treeList + [newtree]

def replaceTest():
    node0=makeRtree(str2List("(+ n 4)"))
    node1=makeRtree(str2List("(+ 1 2)"))
    ans=node0.condReplace("n", node1)
    print(ans)
    return



#testing path method
    # node0 = RacTree(ERobj("(","any"))
    # node1 = RacTree(ERobj("(","any"), parent=node0) 
    # node4=RacTree(pif,parent=node1)
    # node5 = RacTree(ERobj("(","any"),parent=node1)
    # node6 = RacTree(padd,parent=node1)
    # node7 = RacTree(pmult,parent=node1)
    # node1.children=[node4,node5, node6,node7]
    # node2 = RacTree(str2ER("1"), parent=node0)
    # node3 = RacTree(str2ER("2"),parent=node0)
    # node8 = RacTree(pzeroPred, parent=node5)
    # node9 = RacTree(str2ER("1"), parent=node5)
    # node5.children=[node8,node9]
    # node0.children = [node1, node2, node3]
    # node0.pathify()

    # node10= RacTree(ERobj("(","any"))
    # node11 = RacTree(str2ER("7"), parent=node10)
    # node12 = RacTree(str2ER("6"), parent=node10)
    # node13 = RacTree(psubtr, parent=node10)
    # node10.children=[node13, node11, node12]
    # node10.pathify()
    
    """ node0 = RacTree(ERobj("(","any"),path=[])
    node1 = RacTree(pcons,parent=node0, path=[0,0])
    node2 = RacTree(str2ER("7"), parent=node0,path=[0,1])
    node3 = RacTree(ERobj("(","any"),path=[0,2])
    node0.children = [node1, node2, node3]
    node4 = RacTree(pcons,parent=node3, path=[0,2,0])
    node5 = RacTree(str2ER("3"), parent=node3,path=[0,2,1])
    node6 = RacTree(pnull,parent=node3, path=[0,2,2])
    node3.children = [node4, node5, node6] """

   # myTree2 = makeRtree(str2List("(- 7 6)"))
   # print("testing tree raw construction:",node10)
    # print("testing making tree from list:",myTree2)

    # node0.replaceNode([1], node10)
    # myTree3 = makeRtree(str2List("((if (zero? 1) + *) (- 7 6) 2)"))
    # print("testing tree raw construction:",node0)
    # #myTree = makeRtree(str2List("(cons 7 (cons 3 null))"))
    # print("testing making tree from list:",myTree3)
    # print("testing for tree equality vs just string equality: ",node0==myTree3)
     # node10.display()
    # myTree2.display()
    # for i in range(3):
    #     print("child "+str(i)+" constructed")
    #     node10.children[i].display()
    #     print("child "+str(i)+" string")
    #     myTree2.children[i].display()

    #print("testing for tree equality vs just string equality: ",node10==myTree2)


    return