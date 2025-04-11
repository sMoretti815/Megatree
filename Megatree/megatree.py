import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from itertools import chain, combinations
import numpy as np
import os
import graphviz
import matplotlib.image as mpimg
from io import BytesIO
import argparse

os.environ["PATH"] += os.pathsep + r"C:\\Users\\Simone\\anaconda3\\Library\\bin"

def weight_edges(G, trees):
    for G_edge in G.edges():
        if G_edge[0] == "alpha":
            G.edges[G_edge]['label'] = len(G.nodes()[G_edge[1]]['mapping'])
        else:
            G.edges[G_edge]['label'] = 0
    
    for (T, _) in trees:
        for T_edge in T.edges():
            for G_edge in G.edges():
                #print(G_edge)
                for node_from in G.nodes[G_edge[0]]['mapping']:
                    for node_to in G.nodes[G_edge[1]]['mapping']:
                        #print(node_from + " " + node_to)
                        if ((node_from, node_to) == (T_edge[0] + T.graph["num"], T_edge[1] + T.graph["num"])):
                            G.edges[G_edge]['label'] += 1
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

def is_displayed(T, G):
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

def list_label(G, list):
    result = [G.nodes[node]['label'] for node in list]
    return set(result)

def add_leaves(G, T):
    for (T, _) in T:
        leaves = [node + T.graph["num"] for node in T.nodes() if T.out_degree(node) == 0]
        for node in G.nodes():
            if set(G.nodes[node]['mapping']) & set(leaves):
                G.nodes[node]['leaf'] = True
        leaf_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("leaf") == True]
        for node in leaf_nodes:
            G.nodes[node]['shape'] = "square"

def insert_tree_intersect(T, r, G):
    candidates = []
    trovato = False
    in_degree = T.in_degree(r)
    if in_degree == 0:
        r_predecessor = "alpha"
    else:
        r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']

    for node in G.nodes():
        if G.nodes[node]['label'] == T.nodes[r]['label']:
            if list_label(T, list(T.successors(r))) == list_label(G, list(G.successors(node))) or list_label(T, list(T.successors(r))) & list_label(G, list(G.successors(node))):
                node_descendants = nx.descendants(G, node)
                if r_predecessor not in node_descendants:
                    dif = list_label(G, sorted(list(G.successors(node)))) ^ list_label(T, sorted(list(T.successors(r))))
                    candidates.append((len(dif), node))
                    trovato = True
    
    if trovato:
        (length, node)= min(candidates)
        G.nodes[node]['mapping'].append(r + T.graph["num"] )
        T.nodes[r]['mapped_on'] = node         
    else:
        newNode = r + T.graph["num"]
        G.add_node(newNode , mapping = [newNode], label = T.nodes[r]['label'])
        T.nodes[r]['mapped_on'] = newNode

    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])
    #pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    #nx.draw(G, pos, with_labels=True, font_weight="bold")
    #plt.show()
    
    for successor in T.successors(r):
        insert_tree_intersect(T, successor, G)
    return

def level_procedure(T, r, G):
    in_degree = T.in_degree(r)

    if in_degree == 0:
        r_predecessor = "alpha"
    else:
        r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']

    #trovo tutti i nodi in G con la stessa label e la stessa profondità del nodo che voglio inserire
    same_depth = [node for node in G.nodes() if G.nodes[node]['depth'] == T.nodes[r]['depth'] + 1 and G.nodes[node]['label'] == T.nodes[r]['label']]

    if len(same_depth) == 0:
        #se non c'è nessun nodo valido in G lo aggiungo
        newNode = r + T.graph["num"]
        G.add_node(newNode , mapping = [newNode], label = T.nodes[r]['label'])
        G.nodes[newNode]['depth'] = T.nodes[r]['depth'] + 1
        T.nodes[r]['mapped_on'] = newNode
    
    else:
        #se trovo un nodo valido gli aggiugno ai suoi nodi mappati quello che devo inserire
        G.nodes[same_depth[0]]['mapping'].append(r + T.graph["num"] )
        T.nodes[r]['mapped_on'] = same_depth[0]


    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])

    for successor in T.successors(r):
        level_procedure(T, successor, G)
    return

def load_trees(directory):
    trees = []
    for (i, file) in enumerate(os.listdir(directory)):
        T = nx.DiGraph(nx.drawing.nx_agraph.read_dot(os.path.join(directory, file)))
        r = [r for r, d in T.in_degree() if d == 0]

        T.graph["num"] = "-" + str(i)
        
        depth_nodes(T, r[0])
        trees.append((T, r[0]))
    return trees

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', action='store', type=str, required=True,
                        help='Path to the directory of the trees')
    parser.add_argument('-p', '--operation', action='store', type=str, required=True,
                        help='insert_tree_interset/level_procedure')
    parser.add_argument('-s', '--show', action='store_true',
                        help='enable to show megatree after every tree')
    parser.add_argument('-o', '--out', action='store', type=str, required=True,
                        help='Path to output file')
    
    args = parser.parse_args()

    G = nx.DiGraph()
    G.add_node("alpha", label = "alpha", mapping = ["alpha"], depth = 0)
    
    trees = load_trees(args.directory)
    op = args.operation
    
    #inserico mano a mano ogni albero nel grafo
    for (i, (Tree, root)) in enumerate(trees):

        op(Tree, root, G)
        
        depth_nodes(G, "alpha")
        weight_edges(G, trees)
        add_leaves(G, trees)

        if argparse.show:
            O = nx.nx_agraph.to_agraph(G)
            O = graphviz.Source(O.to_string())
            img_data = O.pipe(format='png')
            img = mpimg.imread(BytesIO(img_data), format='png')
            plt.imshow(img)
            plt.show()

    totArchi = sum(len(T.edges()) for T, _ in trees)
    print("numero archi prima = " + str(totArchi))    
    print("numero archi dopo = " + str(len(G.edges())))

    nx.drawing.nx_agraph.write_dot(G, args.out)
    graph = nx.nx_agraph.to_agraph(G)
    graph = graphviz.Source(O.to_string())
    graph.render(args.out, format="pdf", cleanup=True)


if __name__ == "__main":
    main()
