import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
from itertools import chain, combinations
import os

def remove_duplicate_internal(G):
    internals = [node for node in G.nodes() if G.out_degree(node) != 0]
    print(internals)
    for internal1 in internals:
        for internal2 in internals:
            if internal1 in G.nodes() and internal2 in G.nodes():
                #print(internal1, internal2)
                if G.nodes[internal1]['label'] == G.nodes[internal2]['label'] and sorted(list(G.successors(internal1))) == sorted(list(G.successors(internal2))) and internal1 != internal2:
                    print((internal1, internal2))
                    for parent in G.predecessors(internal2):
                        G.add_edge(parent, internal1)
                    G.remove_node(internal2)
                    internals.remove(internal2)
    return




def remove_duplicate_terminal(G):
    terminals = [node for node in G.nodes() if G.out_degree(node) == 0]
    terminal_labels = {G.nodes[node]['label'] for node in terminals}
    for label in terminal_labels:
        terminals_with_label = [node for node in terminals if G.nodes[node]['label'] == label]
        for i in range(1, len(terminals_with_label)):
            terminal = terminals_with_label[i]
            for parent in G.predecessors(terminal):
                G.add_edge(parent, terminals_with_label[0])
            G.remove_node(terminal)
            terminals.remove(terminal)
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
    
    remove_duplicate_terminal(G)
    remove_duplicate_internal(G)


    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    nx.draw(G, pos, with_labels=True, font_weight="bold")
    #edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    #nx.draw_networkx_edge_labels(G, pos, font_color="red", font_size=12)
    plt.show()

    
pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
nx.draw(G, pos, with_labels=True, font_weight="bold")
#edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
#nx.draw_networkx_edge_labels(G, pos, font_color="red", font_size=12)
plt.show()
print("numero archi = " + str(len(G.edges())))       


