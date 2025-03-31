import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
# import matplotlib.pyplot as plt
import numpy as np
import graphviz
import argparse
import sys
import matplotlib.pyplot as plt

# NOTE: The tool will occasionally crash due to the operations. Some controls in
# the operations are avoided so it is possible to delete something that has
# already been deleted. Just re-run it and hope for the right randomness:
#
#    " The man who said "I'd rather be lucky than good" saw deeply into life. People
#      are afraid to face how great a part of life is dependent on luck. It's scary
#      to think so much is out of one's control. "


def remove_collapse_node(T, node):
    parent = list(T.predecessors(node))
    if len(parent) == 0:
        raise ValueError("Trying to delete root")

    children = list(T.successors(node))

    if len(children) > 0:
        parent = parent[0]
        for child in children:
            T.add_edge(parent, child)
    T.remove_node(node)

    # labels = T.nodes[node]['label'].split(',')
    # label_set.remove(labels)

def node_move(T, O, node1, node2):
    parent1 = list(T.predecessors(node1))

    if len(parent1) == 0:
        raise ValueError("Trying to move root")

    if node1 in nx.ancestors(T,node2):
        raise ValueError("a")
    
    ancestors = set(nx.ancestors(O, T.nodes[node2]['label']))

    if T.nodes[node1]['label'] in ancestors:
        raise ValueError("Move don't respect order1")
    
    for node in nx.descendants(T, node1):
        if T.nodes[node]['label'] in ancestors:
            raise ValueError("Move don't respect order2")
    
    T.remove_edge(parent1[0], node1)
    T.add_edge(node2, node1)
    

def random_nodemove(T, O, label_to_node, label_set):
    moved = False
    while not moved:
        n1, n2 = np.random.choice(T.nodes, 2, replace=False)
        #print((T.nodes[n1]['label'], T.nodes[n2]['label']))
        try:
            node_move(T, O, n1, n2)
            moved = True
        except ValueError as e:
            continue

    return

def node_swap(T, O, node1, node2):
    parent1 = list(T.predecessors(node1))
    parent2 = list(T.predecessors(node2))

    if len(parent1) == 0 or len(parent2) == 0:
        raise ValueError("Trying to swap root")
    
    if T.nodes[node1]['label'] in nx.descendants(O, T.nodes[node2]['label']) or T.nodes[node1]['label'] in nx.ancestors(O, T.nodes[node2]['label']):
        raise ValueError("swap not respect order")

    T.nodes[node1]['label'], T.nodes[node2]['label'] = T.nodes[node2]['label'], T.nodes[node1]['label']


def random_labelswap(T, O, label_to_node, label_set):
    # NOTE: this does not check for root removal, if the 'root' is removed from
    # the the set of labels (as is now) it is not necessary to check.
    # Otherwise fix.

    l1, l2 = np.random.choice(list(label_set), 2, replace=False)
    node1 = label_to_node[l1]
    node2 = label_to_node[l2]

    new_label1 = T.nodes[node1]['label'].split(',')
    new_label1.append(l2)
    print(l1, l2, new_label1)
    new_label1.remove(l1)

    new_label2 = T.nodes[node2]['label'].split(',')
    new_label2.append(l1)
    print(l1, l2, new_label2)
    new_label2.remove(l2)

    T.nodes[node1]['label'] = ','.join(new_label1)
    T.nodes[node2]['label'] = ','.join(new_label2)


def random_node_remove(T, *args):
    deleted = False
    while not deleted:
        node = np.random.choice(T.nodes)
        try:
            remove_collapse_node(T, node)
            deleted = True
        except:
            continue


def random_label_remove(T, O, label_to_node, label_set):
    # NOTE: this does not check for root removal, if the 'root' is removed from
    # the the set of labels (as is now) it is not necessary to check.
    # Otherwise fix.

    label = np.random.choice(list(label_set), 1)[0]
    node = label_to_node[label]

    new_label = T.nodes[node]['label'].split(',')
    if len(new_label) == 1:
        remove_collapse_node(T, node)
    else:
        new_label.remove(label)
        T.nodes[node]['label'] = ','.join(new_label)

    label_set.remove(label)


def random_label_duplication(T, O, label_to_node, label_set):
    label = np.random.choice(list(label_set), 1)[0]
    node = label_to_node[label]

    random_node = np.random.choice(T.nodes)
    while random_node == node or len(list(T.predecessors(random_node))) == 0:
        random_node = np.random.choice(T.nodes)

    T.nodes[random_node]['label'] += f',{label}'


def random_nodeswap(T, O, *args):
    swapped = False
    while not swapped:
        n1, n2 = np.random.choice(T.nodes, 2, replace=False)
        #print((T.nodes[n1]['label'], T.nodes[n2]['label']))
        try:
            node_swap(T, O, n1, n2)
            swapped = True
        except:
            continue


def load_dotfile(path):
    T = nx.DiGraph(nx.drawing.nx_agraph.read_dot(path))

    label_to_node = dict()
    label_set = set()
    

    for node in T.nodes(data=True):
        id_node = node[0]
        labels = node[1]['label'].split(',')
        for l in labels:
            label_set.add(l)
            label_to_node[l] = id_node

    label_set = sorted(list(label_set))
    label_set.remove('root')

    return T, label_to_node, label_set

def check_duplication(T):
    labels = list()
    for node in T.nodes:
        l = T.nodes[node]['label']
        if not l in labels:
            labels.append(l)
        else:
            sys.exit(1)
    print('dup ok')

def update_order(T, O):
    for u,v in T.edges:
            if T.nodes[v]['label'] not in nx.descendants(O, T.nodes[u]['label']):
                O.add_edge(T.nodes[u]['label'], T.nodes[v]['label'])


def main():
    parser = argparse.ArgumentParser(
        description='MP3-treesim tree perturbation tool', add_help=True)

    parser.add_argument('-t', '--tree', action='store', type=str, required=True,
                        help='Path to the tree')
    parser.add_argument('--labelswap', action='store', type=int, default=0,
                        help='Number/probability of label swaps to produce')
    parser.add_argument('--noderemove', action='store', type=int, default=0,
                        help='Number/probability of nodes to remove')
    parser.add_argument('--labelremove', action='store', type=int, default=0,
                        help='Number/probability of labels to remove')
    parser.add_argument('--labelduplication', action='store', type=int, default=0,
                        help='Number/probability of labels to duplicate')
    parser.add_argument('--nodeswap', action='store', type=int, default=0,
                        help='Number/probability of nodes to swap')
    parser.add_argument('--nodemove', action='store', type=int, default=0,
                        help='Number/probability of nodes to move')
    parser.add_argument('--treenum', action='store', type=int, default=0,
                        help='Number/probability of tree to generate')
    parser.add_argument('--out', action='store', type=str, required=True,
                        help='Path to output file')
    parser.add_argument('--totoperations', action='store', type=int, default=-1,
                        help='Number of total operations. If set to -1 (default) all operations will be executed.')

    args = parser.parse_args()

    T, label_to_node, label_set = load_dotfile(args.tree)
    O = nx.DiGraph()
    O.add_nodes_from(label_set)
    for u,v in T.edges:
        O.add_edge(T.nodes[u]['label'], T.nodes[v]['label'])

    for i in range(args.treenum):
        T, label_to_node, label_set = load_dotfile(args.tree)
        if args.totoperations == -1:
            # Execute all operations
            for _ in range(args.labelswap):
                random_labelswap(T, label_to_node, label_set)
            for _ in range(args.noderemove):
                random_node_remove(T, label_to_node, label_set)
            for _ in range(args.labelremove):
                random_label_remove(T, label_to_node, label_set)
            for _ in range(args.labelduplication):
                random_label_duplication(T, label_to_node, label_set)
            for _ in range(args.nodeswap):
                random_nodeswap(T, O, label_to_node, label_set)
                #update_order(T, O)
            for _ in range(args.nodemove):
                random_nodemove(T, O, label_to_node, label_set)
                #update_order(T, O)
        else:
            choices = [args.labelswap, args.noderemove,
                    args.labelremove, args.labelduplication, args.nodeswap, args.nodemove]
            sum_c = sum(choices)
            choices = list(map(lambda x: x / sum_c, choices))
            perturbations = [random_labelswap, random_node_remove,
                            random_label_remove, random_label_duplication, random_nodeswap, random_nodemove]

            operations = np.random.choice(
                perturbations, size=args.totoperations, p=choices)

            for op in operations:
                print(op)
                op(T, O, label_to_node, label_set)
                #update_order(T, O)

        if args.labelduplication == 0:
            check_duplication(T)


        update_order(T, O)
        outName = args.out + str(i+2) + ".gv"
        nx.drawing.nx_agraph.write_dot(T, outName)

        graph = graphviz.Source.from_file(outName)
        graph.render(outName + "_pdf", format="pdf", cleanup=True)



    O = nx.nx_agraph.to_agraph(O)
    O = graphviz.Source(O.to_string())
    O.render(args.out + "_order", format="pdf", cleanup=True)
    
if __name__ == '__main__':
    main()
