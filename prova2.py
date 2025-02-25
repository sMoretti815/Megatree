import matplotlib
matplotlib.use('TkAgg')
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
from itertools import chain, combinations

#due nodi con stessa label sono uguali?
#se un nodo ha due figli con la stessa label non potrà essere mai incorporato?
#bisogna controllare tutti gli alberi o solo quelli già inseriti?


def incorporable(G, Trees):
    result=[]
    y_candidates = []
    
    for y in G.nodes():
        #y_successors = [G.nodes[node]['label'] for node in G.successors(y)]
        y_successors = list(G.successors(y))
        
        #creo la lista con tutti i sottoinsiemi dei successori di y
        powerlist = chain.from_iterable(combinations(y_successors, r) for r in range(1, len(y_successors)+1))
        y_valid = True
        
        for l in powerlist:
            find = False
            for (T, _) in Trees:
                for z in T.nodes():
                    if T.nodes[z]['label'] == G.nodes[y]['label']: #per ogni nodo z in ogni albero trovo quelli la cui label è uguale a quella di y
                        if (sorted([node for node in T.successors(z)])) == sorted(list(l)): 
                            find = True
                            break
            if find == False:
                y_valid = False
                break 
        if y_valid:
          y_candidates.append(y)
        
    for y in y_candidates():
        x_candidates = [x for x in G.nodes() if (y!=x and (G.nodes[y]['label']) == (G.nodes[x]['label']))]
        y_successors = list(G.successors(y))
        
        count_y = Counter(y_successors)
        for x in list(x_candidates):
            x_successors = list(G.successors(x))
            
            count_x = Counter(x_successors)
            if any(count_y[node] >= count_x[node] for node in count_y):
                x_candidates.remove(x)
                continue
        for x in x_candidates:
            result.append((x,y)) #x domina y
            
    #print(result)
    return result

def incorporate(G, nodes):
    print(nodes)
    print("incorporated")
    nx.draw_shell(G, with_labels=True, font_weight="bold")
    plt.show()
    for node in G.predecessors(nodes[len(nodes)-1][1]):
        G.add_edge(node, nodes[len(nodes)-1][0])
    
    G.remove_node(nodes[len(nodes)-1][1])
    return


def shrinkable(G):
    result = []
    y_candidates = [node for (node, degree) in G.out_degree() if degree == 1]
    #print(y_candidates)
    for y in y_candidates:
        x_candidates = [node for node in G.nodes() if G.nodes[node]['label'] == G.nodes[y]['label'] and
                        sorted(list(G.predecessors(node))) == sorted(list(G.predecessors(y))) and 
                        #sorted([G.nodes[pre_y]['label'] for pre_y in G.predecessors(y)]) == sorted([G.nodes[pre_node]['label'] for pre_node in G.predecessors(node)]) and
                        y not in nx.descendants(G, node) and 
                        list(G.successors(y))[0] in nx.descendants(G, node) and
                        node!=y]
        for x in x_candidates:
            result.append((y, x))
    #print(result)
    return result

def shrink(G, nodes_shrinkable):
    print(nodes_shrinkable)
    print("shrinked")
    nx.draw_shell(G, with_labels=True, font_weight="bold")
    plt.show()
    z = next(G.successors(nodes_shrinkable[0][0]))
    G.add_edge(nodes_shrinkable[0][1], z)
    G.remove_node(nodes_shrinkable[0][0])
    return

T1 = nx.DiGraph()
T2 = nx.DiGraph()
T3 = nx.DiGraph()
G = nx.DiGraph()
G.add_node("alpha", label="z")
alpha = list(G.nodes())[0]
T1.add_edges_from([("alpha", "a1"), ("a1","b1"), ("b1", "d1"), ("b1","c1"), ("d1","e1"), ("c1","f1"), ("f1","g1")])
T2.add_edges_from([("alpha", "a2"),("a2","b2"), ("b2", "d2"), ("b2","c2"), ("d2","f2"), ("c2","e2"), ("a2","g2")])
T3.add_edges_from([("alpha", "a3"), ("a3","b3"), ("a3", "g3"), ("b3","c3"), ("b3","d3"), ("d3","f3"), ("g3","e3")])
Trees = [(T1, "a1"),(T2, "a2"),(T3, "a3")]

for (Tree, _) in Trees:
    for node in Tree.nodes():
        if node != "alpha":
            Tree.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
        else:
            Tree.nodes[node]['label'] = "z"
        
for (Tree, root) in Trees:
    G.add_nodes_from(Tree.nodes)
    G.add_edges_from(Tree.edges)
    
    for node in Tree.nodes():
        if node != "alpha":
            G.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
        else:
            G.nodes[node]['label'] = "z"
        
    nodes_shrinkable = shrinkable(G)
    nodes_incorporable = incorporable(G, Trees)
    while nodes_incorporable or nodes_shrinkable:  
        if nodes_incorporable:
            incorporate(G, nodes_incorporable)
        else:
            shrink(G, nodes_shrinkable)
        nodes_shrinkable = shrinkable(G)
        nodes_incorporable = incorporable(G, Trees)
        
    
    nx.draw_shell(G, with_labels=True, font_weight="bold")
    plt.show() 
    
            
    #aggiungere pesi


