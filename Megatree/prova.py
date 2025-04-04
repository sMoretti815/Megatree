
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
from itertools import chain, combinations
import numpy as np
import os
os.environ["PATH"] += os.pathsep + r"C:\Users\Simone\anaconda3\Library\bin"



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
        
        for x in list(x_candidates):
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
    
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    nx.draw(G, pos, with_labels=True, font_weight="bold")
    #edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
    plt.show()

    
    z = (set(G.successors(y)) - set(G.successors(x))).pop()
    G.add_edge(x, z)
    G.nodes[x]['mapping'].extend(G.nodes[y]['mapping'])
    G.remove_node(y)
    return

def is_displayed(T, G):
    (T, r) = T
    t_topological = list(reversed(list(nx.topological_sort(T))))
    g_topological = list(reversed(list(nx.topological_sort(G))))
    t_dict = {key : value for (value, key) in enumerate(t_topological)}
    g_dict = {key : value for (value, key) in enumerate(g_topological)}
    D = np.zeros((len(t_topological), len(g_topological)))
    P = {}
    for (i, x) in enumerate(t_topological):
        for (j, y) in enumerate(g_topological):
            P[y] = P.get(y, [])
            if(T.nodes[x]['label'] != G.nodes[y]['label']):
                D[i, j] = 0
            elif T.out_degree(x) == 0:
                D[i, j] = 1
            else:
                D[i, j] = 1
                for z in T.successors(x):
                    z_valid = False
                    for h in G.successors(y):
                        if D[t_dict[z], g_dict[h]] == 1: 
                            z_valid = True
                            P[y].append(h)
                            break
                    if z_valid == False:
                        D[i, j] = 0
                        break
    return (D, P)
    
def reconstruct_tree(TG, P, y):
    for z in P[y]:
        TG.add_edge(y, z)
        reconstruct_tree(TG, P, z)
    return
    
def insert_tree(T, r, G):
    insert_node3(T, r, G)
    return

def insert_node(T, r, G):
    trovato = False
    for node in G.nodes():
        if G.nodes[node]['label'] == T.nodes[r]['label'] and list_label(T, sorted(list(T.successors(r)))) == list_label(G, sorted(list(G.successors(node)))):
            
            G.nodes[node]['mapping'].append(r)
            T.nodes[r]['mapped_on'] = node
            trovato = True
            break
            
    if trovato == False:
        G.add_node(r, mapping = [r], label = re.search(r'(^\S)', r).group(0))
        T.nodes[r]['mapped_on'] = r
        
    r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']
    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])
    #pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    #nx.draw(G, pos, with_labels=True, font_weight="bold")
    #plt.show()
    
    for successor in T.successors(r):
        insert_node(T, successor, G)
    return

def insert_node2(T, r, G):
    candidates = []
    for node in G.nodes():
        if G.nodes[node]['label'] == T.nodes[r]['label']:  
            dif = list_label(T, sorted(list(T.successors(r)))) ^ list_label(G, sorted(list(G.successors(node))))
            candidates.append((len(dif), node))
    
    (length, node)= min(candidates)
    

    if length <= len(list(T.successors(r))):
        G.nodes[node]['mapping'].append(r)
        T.nodes[r]['mapped_on'] = node         
    else:
        G.add_node(r, mapping = [r], label = re.search(r'(^\S)', r).group(0))
        T.nodes[r]['mapped_on'] = r
            
    r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']
    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])
    #pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    #nx.draw(G, pos, with_labels=True, font_weight="bold")
    #plt.show()
    
    for successor in T.successors(r):
        insert_node2(T, successor, G)
    return

def insert_node3(T, r, G):
    candidates = []
    trovato = False
    r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']
    for node in G.nodes():
        if G.nodes[node]['label'] == T.nodes[r]['label'] and list_label(T, sorted(list(T.successors(r)))) <= list_label(G, sorted(list(G.successors(node)))):
            node_descendants = nx.descendants(G, node)
            if r_predecessor not in node_descendants:
                dif = list_label(G, sorted(list(G.successors(node)))) - list_label(T, sorted(list(T.successors(r))))
                candidates.append((len(dif), node))
                trovato = True
    
    
    if trovato:
        (length, node)= min(candidates)
        G.nodes[node]['mapping'].append(r)
        T.nodes[r]['mapped_on'] = node         
    else:
        G.add_node(r, mapping = [r], label = re.search(r'(^\S)', r).group(0))
        T.nodes[r]['mapped_on'] = r

    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])
    #pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    #nx.draw(G, pos, with_labels=True, font_weight="bold")
    #plt.show()
    
    for successor in T.successors(r):
        insert_node3(T, successor, G)
    return

def list_label(G, list):
    result = [G.nodes[node]['label'] for node in list]
    return set(result)

def add_leaves(G, T):
    for (T, _) in T:
        leaves = [node for node in T.nodes() if T.out_degree(node) == 0]
        for node in G.nodes():
            if set(G.nodes[node]['mapping']) & set(leaves):
                G.nodes[node]['leaf'] = True
        
T1 = nx.DiGraph()
T2 = nx.DiGraph()
T3 = nx.DiGraph()
T4 = nx.DiGraph()
G = nx.DiGraph()
G.add_node("alpha", label="alpha")

#T1.add_edges_from([("alpha", "a1"), ("a1","b1"), ("b1", "d1"), ("b1","c1"), ("d1","e1"), ("c1","f1"), ("f1","g1")])
#T2.add_edges_from([("alpha", "a2"),("a2","b2"), ("b2", "d2"), ("b2","c2"), ("d2","f2"), ("c2","e2"), ("a2","g2")])
#T3.add_edges_from([("alpha", "a3"), ("a3","b3"), ("a3", "g3"), ("b3","c3"), ("b3","d3"), ("d3","f3"), ("g3","e3")])
#T4.add_edges_from([("alpha", "a4"), ("a4","b4"), ("b4", "d4"), ("d4","c4"), ("c4","e4")])
#Trees = [(T1, "a1"),(T2, "a2"),(T3, "a3"), (T4, "a4")]

#T1.add_edges_from([("alpha", "x1"), ("x1", "a1"), ("x1", "b1"), ("b1", "c1")])
#T2.add_edges_from([("alpha", "x2"), ("x2", "a2"), ("a2", "b2"), ("x2", "c2")])
#T3.add_edges_from([("alpha", "x3"), ("x3", "a3"), ("a3", "c3"), ("x3", "b3")])
#Trees = [(T1, "x1"),(T2, "x2"),(T3, "x3")]

#T1.add_edges_from([("alpha", "a1"), ("a1","b1"), ("b1","c1"), ("a1","e1"), ("e1","d1")])
#T2.add_edges_from([("alpha", "a2"),("a2","b2"), ("b2", "d2"), ("a2","c2"), ("b2","e2")])
#T3.add_edges_from([("alpha", "a3"), ("a3","b3"), ("a3", "e3"), ("b3","c3"), ("b3","d3")])
#Trees = [(T1, "a1"),(T2, "a2"),(T3, "a3")]

#T1.add_edges_from([("alpha", "a1"), ("a1", "b1"), ("b1", "c1")])
#T2.add_edges_from([("alpha", "b2"), ("b2", "c2"), ("c2", "a2")])
#T3.add_edges_from([("alpha", "c3"), ("c3", "a3"), ("a3", "b3")])
#Trees = [(T1, "a1"),(T2, "b2"),(T3, "c3")]


T1.add_edges_from([("alpha", "a1"), ("a1", "b1"), ("b1", "c1")])
T2.add_edges_from([("alpha", "b2"), ("b2", "c2"), ("c2", "a2")])
Trees = [(T1, "a1"),(T2, "b2")]

#etichetto i nodi dentro gli alberi
for (Tree, _) in Trees:
    for node in Tree.nodes():
        Tree.nodes[node]['mapped_on'] = node
        if node != "alpha":
            Tree.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
        else:
            Tree.nodes[node]['label'] = "alpha"
            Tree.nodes[node]['mapped_on'] = "alpha"
    pos = nx.nx_agraph.graphviz_layout(Tree, prog="dot")
    other_nodes = [n for n in Tree.nodes if n != "alpha"]
    #nx.draw_networkx_nodes(Tree, pos, nodelist=other_nodes)
    labels = nx.get_node_attributes(Tree, 'label')
    labels = {k: v for k, v in labels.items() if k != "alpha"}
    edges_to_draw = [(u, v) for u, v in Tree.edges if u != "alpha"]
    #nx.draw_networkx_edges(Tree, pos, edgelist=edges_to_draw)
    #nx.draw_networkx_labels(Tree, pos, labels)
    #plt.show()

#inserico mano a mano ogni albero nel grafo
for (Tree, root) in Trees:
    
    if nx.is_empty(G):
        G.add_nodes_from(Tree.nodes)
        G.add_edges_from(Tree.edges)
        
        #etichetto i nodi dentro il grafo
        for node in Tree.nodes():
            G.nodes[node]['mapping'] = [node]
            if node != "alpha":
                G.nodes[node]['label'] = re.search(r'(^\S)', node).group(0)
            else:
                G.nodes[node]['label'] = "alpha"
    else:
        insert_tree(Tree, root, G)
    
    
    #fino a che ci sono nodi che possono essere shrinkati o incorporati lo faccio, poi passo ad inserire l'albero successivo
    nodes_shrinkable = []#shrinkable(G)
    nodes_incorporable = []#incorporable(G, Trees)
    #depth_nodes(G, "alpha")
    while nodes_incorporable or nodes_shrinkable:  
        if nodes_incorporable:
            incorporate(G, nodes_incorporable)
        else:
            shrink(G, nodes_shrinkable)
            
        #nodes_shrinkable = shrinkable(G)
        #nodes_incorporable = incorporable(G, Trees)
        #depth_nodes(G, "alpha")
        weight_edges(G, Trees)
    
        #pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        #nx.draw(G, pos, with_labels=True, font_weight="bold")
        #edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
        #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
        #plt.show()


weight_edges(G, Trees)
add_leaves(G, Trees)

pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
leaf_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("leaf") == True]
other_nodes = [n for n in G.nodes if n not in leaf_nodes]
edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_nodes(G, pos, nodelist=other_nodes)
nx.draw_networkx_nodes(G, pos, nodelist=leaf_nodes, node_color="lightgreen", node_shape="s")
labels = nx.get_node_attributes(G, 'label')
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, labels)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=12)
plt.show()
print("numero archi = " + str(len(G.edges())))       

for T in Trees:
    (D, P) = is_displayed(T, G)
    TG = nx.DiGraph()
    reconstruct_tree(TG, P, "alpha")
    #pos = nx.nx_agraph.graphviz_layout(TG, prog="dot")
    #nx.draw(TG, pos, with_labels=True, font_weight="bold")
    #plt.show()