import matplotlib
matplotlib.use('TkAgg')
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
from itertools import chain, combinations
import os

#se un nodo ha due figli con la stessa label non potrà essere mai incorporato?
#bisogna controllare tutti gli alberi o solo quelli già inseriti?

def incorporable(G, Trees):
    result=[]
    y_candidates = []
    
    #trovo tutti nodi y per cui è vero che per ogni sottoinsieme Z dell'insieme dei successori di y esiste
    #un albero Tz con un nodo z per cui label(z) == label(y) e tale che i successori di z siano esattamente Z
    for y in G.nodes():
        #y_successors = [G.nodes[node]['label'] for node in G.successors(y)]
        y_successors = list(G.successors(y))
        
        #trovo la lista dei sottoinsiemi dei successori di y
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
    
    #per ogni y per cui vale la condizione sopra
    for y in G.nodes(): #o G.nodes()?
        #trovo tutti i nodi x con al stessa label e li salvo in una lista di nodi x possibili
        x_candidates = [x for x in G.nodes() if (y!=x and (G.nodes[y]['label']) == (G.nodes[x]['label']))]
        y_successors = list(G.successors(y))
        count_y = Counter(y_successors)
        
        for x in list(x_candidates):
            x_successors = list(G.successors(x))
            count_x = Counter(x_successors)
            #per ogni x se i successori di x non sono un sottoinsieme dei successori di y rimuovo x
            if not all(count_x[node] <= count_y[node] for node in count_x):
                x_candidates.remove(x)
                continue
        for x in x_candidates:
            result.append((y,x)) #y domina x
            
    #print(result)
    return result

def incorporate(G, nodes_incorporable):
    (y, x) = nodes_incorporable[len(nodes_incorporable)-1]
    #(y, x) = max(nodes, key=lambda x: G.nodes[x[0]]['depth'])
    print(f"nodes_incorporable: {nodes_incorporable}")
    print(f"incorporated {y} to {x}")
    #aggiungo un arco da ogni predecessore di x verso y e rimuovo x
    for x_predecessor in G.predecessors(x):
        G.add_edge(x_predecessor, y)
    G.nodes[y]['mapping'].extend(G.nodes[x]['mapping'])
    G.remove_node(x)
    return

def shrinkable(G):
    result = []
    #trovo tutti i nodi con un solo arco uscente
    y_candidates = [node for (node, out_degree) in G.out_degree() if out_degree == 1]
    #print(y_candidates)
    for y in y_candidates:
        #trovo i nodi per cui vale:
        x_candidates = [node for node in G.nodes() if G.nodes[node]['label'] == G.nodes[y]['label'] and #node e y hanno la stessa label
                        sorted(list(G.predecessors(node))) == sorted(list(G.predecessors(y))) and #predecessori di node = predecessori di y
                        y not in nx.descendants(G, node) and #non esite un percorso da node a y
                        list(G.successors(y))[0] in nx.descendants(G, node) and #il sucessore di y è un discendente di node
                        node!=y] #node e y sono due nodi diversi
                        
        for x in x_candidates:
            result.append((y, x))
    return result

def shrink(G, nodes_shrinkable):
    (y, x) = nodes_shrinkable[0]
    #(y, x) = max(nodes_shrinkable, key=lambda x: G.nodes[x[1]]['depth'])
    print(f"nodes_shrinkable: {nodes_shrinkable}")
    print(f"shrinked {y} to {x}")
    
    z = next(G.successors(y))
    G.add_edge(x, z)
    G.nodes[x]['mapping'].extend(G.nodes[y]['mapping'])
    G.remove_node(y)
    return

def weight_edges(G, Trees):
    for G_edge in G.edges():
         G.edges[G_edge]['weight'] = 0
    
    for (T, _) in Trees:
        for T_edge in T.edges():
            for G_edge in G.edges():
                #print(G_edge)
                for node_from in G.nodes[G_edge[0]]['mapping']:
                    for node_to in G.nodes[G_edge[1]]['mapping']:
                        #print(node_from + " " + node_to)
                        if ((node_from, node_to) == T_edge):
                            G.edges[G_edge]['weight'] += 1
    return

def depth_nodes(G, root):
    ordine_topologico = list(nx.topological_sort(G))
    depths = {node: float('inf') for node in G.nodes}
    depths[root] = 0
    
    for node in ordine_topologico:
        for successore in G.successors(node):
            depth = G[node][successore].get('depth', 1) 
            if depths[node] + 1 < depths[successore]:
                depths[successore] = depths[node] + 1
    nx.set_node_attributes(G, depths, "depth")
    return

def shrinkable2(G):
    result = []
    
    #print(y_candidates)
    for y in G.nodes():
        #trovo i nodi per cui vale:
        x_candidates = [node for node in G.nodes() if G.nodes[node]['label'] == G.nodes[y]['label'] and #node e y hanno la stessa label
                        sorted(list(G.predecessors(node))) == sorted(list(G.predecessors(y))) and #predecessori di node = predecessori di y
                        y not in nx.descendants(G, node) and #non esite un percorso da node a y
                        all(y_suc in nx.descendants(G, node) for y_suc in list(G.successors(y))) and #il sucessore di y è un discendente di node
                        node!=y] #node e y sono due nodi diversi
        
        for x in x_candidates:
            if (len(set(G.successors(y)) - set(G.successors(x))) != 1):
                x_candidates.remove(x)
        
        for x in x_candidates:
            result.append((y, x))
    return result

def shrink2(G, nodes_shrinkable):
    (y, x) = nodes_shrinkable[0]
    #(y, x) = max(nodes_shrinkable, key=lambda x: G.nodes[x[1]]['depth'])
    print(nodes_shrinkable)
    print("shrinked")
    
    z = (set(G.successors(y)) - set(G.successors(x))).pop()
    G.add_edge(x, z)
    G.nodes[x]['mapping'].extend(G.nodes[y]['mapping'])
    G.remove_node(y)
    return

T1 = nx.DiGraph()
T2 = nx.DiGraph()
T3 = nx.DiGraph()
G = nx.DiGraph()
G.add_node("alpha", label="alpha")


T1.add_edges_from([("alpha", "a1"), ("a1","b1"), ("b1", "d1"), ("b1","c1"), ("d1","e1"), ("c1","f1"), ("f1","g1")])
T2.add_edges_from([("alpha", "a2"),("a2","b2"), ("b2", "d2"), ("b2","c2"), ("d2","f2"), ("c2","e2"), ("a2","g2")])
T3.add_edges_from([("alpha", "a3"), ("a3","b3"), ("a3", "g3"), ("b3","c3"), ("b3","d3"), ("d3","f3"), ("g3","e3")])
Trees = [(T1, "a1"),(T2, "a2"),(T3, "a3")]

#T1.add_edges_from([("alpha", "x1"), ("x1", "a1"), ("x1", "b1"), ("b1", "c1")])
#T2.add_edges_from([("alpha", "x2"), ("x2", "a2"), ("a2", "b2"), ("x2", "c2")])
#T3.add_edges_from([("alpha", "x3"), ("x3", "a3"), ("a3", "c3"), ("x3", "b3")])
#Trees = [(T1, "x1"),(T2, "x2"),(T3, "x3")]

#T1.add_edges_from([("alpha", "a1"), ("a1","b1"), ("b1","c1"), ("a1","e1"), ("e1","d1")])
#T2.add_edges_from([("alpha", "a2"),("a2","b2"), ("b2", "d2"), ("a2","c2"), ("b2","e2")])
#T3.add_edges_from([("alpha", "a3"), ("a3","b3"), ("a3", "e3"), ("b3","c3"), ("b3","d3")])
#Trees = [(T1, "a1"),(T2, "a2"),(T3, "a3")]

#etichetto i nodi dentro gli alberi
for (Tree, _) in Trees:
    for node in Tree.nodes():
        Tree.nodes[node]['mapping'] = [node]
        if node != "alpha":
            Tree.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
        else:
            Tree.nodes[node]['label'] = "alpha"

#inserico mano a mano ogni albero nel grafo 
for (Tree, root) in Trees:
    G.add_nodes_from(Tree.nodes)
    G.add_edges_from(Tree.edges)
    
    #etichetto i nodi dentro il grafo
    for node in Tree.nodes():
        G.nodes[node]['mapping'] = [node]
        if node != "alpha":
            G.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
        else:
            G.nodes[node]['label'] = "z"
    
    #fino a che ci sono nodi che possono essere shrinkati o incorporati lo faccio, poi passo ad inserire l'albero successivo
    nodes_shrinkable = shrinkable(G)
    nodes_incorporable = incorporable(G, Trees)
    #depth_nodes(G, "alpha")
    while nodes_incorporable or nodes_shrinkable:  
        if nodes_incorporable:
            incorporate(G, nodes_incorporable)
        else:
            shrink(G, nodes_shrinkable)
            
        nodes_shrinkable = shrinkable(G)
        nodes_incorporable = incorporable(G, Trees)
        #depth_nodes(G, "alpha")
        weight_edges(G, Trees)
    
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        nx.draw(G, pos, with_labels=True, font_weight="bold")
        edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
        plt.show()


weight_edges(G, Trees)
    
pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
nx.draw(G, pos, with_labels=True, font_weight="bold")
edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
plt.show() 
print("numero archi = " + str(len(G.edges())))       


