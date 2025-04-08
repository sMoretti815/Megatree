import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
from itertools import chain, combinations
import numpy as np
import os
import graphviz
import matplotlib.image as mpimg
from io import BytesIO

os.environ["PATH"] += os.pathsep + r"C:\\Users\\Simone\\anaconda3\\Library\\bin"

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
        if G_edge[0] == "alpha":
            G.edges[G_edge]['label'] = len(G.nodes()[G_edge[1]]['mapping'])
        else:
            G.edges[G_edge]['label'] = 0
    
    for (T, _) in Trees:
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

def reconstruct_tree(TG, P, y):
    for z in P[y]:
        TG.add_edge(y, z)
        reconstruct_tree(TG, P, z)
    return

def insert_tree_rilassato(T, r, G):
    candidates = []
    trovato = False
    in_degree = T.in_degree(r)
    if in_degree == 0:
        r_predecessor = "alpha"
    else:
        r_predecessor = T.nodes[next(T.predecessors(r))]['mapped_on']

    for node in G.nodes():
        if G.nodes[node]['label'] == T.nodes[r]['label']:
            if list_label(T, sorted(list(T.successors(r)))) <= list_label(G, sorted(list(G.successors(node)))):
                node_descendants = nx.descendants(G, node)
                if r_predecessor not in node_descendants:
                    dif = list_label(G, sorted(list(G.successors(node)))) - list_label(T, sorted(list(T.successors(r))))
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
        insert_tree_rilassato(T, successor, G)
    return

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
            if list_label(T, sorted(list(T.successors(r)))) == list_label(G, sorted(list(G.successors(node)))) or list_label(T, sorted(list(T.successors(r)))) & list_label(G, sorted(list(G.successors(node)))):
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

    same_depth = [node for node in G.nodes() if G.nodes[node]['depth'] == T.nodes[r]['depth'] + 1 and G.nodes[node]['label'] == T.nodes[r]['label']]

    if len(same_depth) == 0:
        newNode = r + T.graph["num"]
        G.add_node(newNode , mapping = [newNode], label = T.nodes[r]['label'])
        G.nodes[newNode]['depth'] = T.nodes[r]['depth'] + 1
        T.nodes[r]['mapped_on'] = newNode
    else:
        G.nodes[same_depth[0]]['mapping'].append(r + T.graph["num"] )
        T.nodes[r]['mapped_on'] = same_depth[0]

    G.add_edge(r_predecessor, T.nodes[r]['mapped_on'])

    for successor in T.successors(r):
        level_procedure(T, successor, G)
    return


G = nx.DiGraph()

G.add_node("alpha")
G.nodes["alpha"]["label"] = "alpha"
G.nodes["alpha"]["mapping"] = ["alpha"]
G.nodes["alpha"]["depth"] = 0
file_list = []
Trees = []

T_version = "T11"
op = level_procedure


for (i, file) in enumerate(os.listdir("TreeSim\\Trees_out\\" + T_version)):
    if file.endswith(".gv"):
        T = nx.DiGraph(nx.drawing.nx_agraph.read_dot("TreeSim\\Trees_out\\" + T_version + "\\" + file))
        r = [r for r, d in T.in_degree() if d == 0 ]
        T.graph["num"] = "-" + str(i)
        depth_nodes(T, r[0])
        Trees.append((T, r[0]))

#for (Tree, _) in Trees:
    #pos = nx.nx_agraph.graphviz_layout(Tree, prog="dot")
    #other_nodes = [n for n in Tree.nodes if n != "alpha"]
    #nx.draw_networkx_nodes(Tree, pos, nodelist=other_nodes)
    #labels = nx.get_node_attributes(Tree, 'label')
    #labels = {k: v for k, v in labels.items() if k != "alpha"}
    #edges_to_draw = [(u, v) for u, v in Tree.edges if u != "alpha"]
    #nx.draw_networkx_edges(Tree, pos, edgelist=edges_to_draw)
    #nx.draw_networkx_labels(Tree, pos, labels= labels)
    #plt.show()

#inserico mano a mano ogni albero nel grafo
for (i, (Tree, root)) in enumerate(Trees):

    op(Tree, root, G)
    
    #fino a che ci sono nodi che possono essere shrinkati o incorporati lo faccio, poi passo ad inserire l'albero successivo
    nodes_shrinkable = []#shrinkable(G)
    nodes_incorporable = []#incorporable(G, Trees)
    depth_nodes(G, "alpha")
    while nodes_incorporable or nodes_shrinkable:  
        if nodes_incorporable:
            incorporate(G, nodes_incorporable)
        else:
            shrink(G, nodes_shrinkable)
            
        nodes_shrinkable = shrinkable(G)
        nodes_incorporable = incorporable(G, Trees)
        #depth_nodes(G, "alpha")

    weight_edges(G, Trees)
    add_leaves(G, Trees)
    O = nx.nx_agraph.to_agraph(G)
    O = graphviz.Source(O.to_string())
    outName = "Resources\\Megatree_" + T_version + "_" + str(i) + op.__name__
    O.render(outName, format="pdf", cleanup=True)
    img_data = O.pipe(format='png')
    img = mpimg.imread(BytesIO(img_data), format='png')
    plt.axis('off')
    #plt.imshow(img)
    #plt.show()

weight_edges(G, Trees)
add_leaves(G, Trees)

O = nx.nx_agraph.to_agraph(G)
O = graphviz.Source(O.to_string())
img_data = O.pipe(format='png')
img = mpimg.imread(BytesIO(img_data), format='png')
#plt.imshow(img)
#plt.show()

totArchi = sum(len(T.edges()) for T, _ in Trees)
print("numero archi prima = " + str(totArchi))    
print("numero archi dopo = " + str(len(G.edges())))


outName = "TreeSim\\Trees_out\\" + T_version + "\\" + "Megatree_" + T_version

nx.drawing.nx_agraph.write_dot(G, outName + ".txt")
graph = graphviz.Source.from_file(outName + ".txt")
graph.render(outName + op.__name__ + "_pdf", format="pdf", cleanup=True)


for (T, r) in Trees:
    #(D, P) = is_displayed(T, G)
    TG = nx.DiGraph()
    #reconstruct_tree(TG, P, r + T.graph["num"])
    labels = nx.get_node_attributes(TG, 'label')
    pos = nx.nx_agraph.graphviz_layout(TG, prog="dot")
    nx.draw_networkx_labels(TG, pos, labels)
    nx.draw(TG, pos, font_weight="bold")
    #plt.show()