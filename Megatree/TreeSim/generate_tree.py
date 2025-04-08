import sys
import argparse
import string
import random

import graphviz
from graphviz import Digraph


def main():
    parser = argparse.ArgumentParser(
        description="MP3-treesim tree generation tool")
    parser.add_argument("-n", "--nodes",
                        dest="n",
                        help="Total number of nodes (internal nodes and leafs) [Default: 10]",
                        metavar='N',
                        type=int,
                        action="store",
                        default=10)
    parser.add_argument("-l", "--labels",
                        dest="l",
                        help="Total number of labels [Default: 10]",
                        metavar='L',
                        type=int,
                        action="store",
                        default=10)
    parser.add_argument("-s", "--sons",
                        dest="s",
                        help="Maximum number of sons for node [Default: 3]",
                        metavar='S',
                        type=int,
                        action="store",
                        default=3)
    parser.add_argument("-f", "--full",
                        dest="full",
                        help="Generate a complete tree [Default: false]",
                        action="store_true",
                        default=False)
    parser.add_argument("-o", "--out",
                        dest="out",
                        help="Output prefix [Default: out]",
                        metavar="OUT",
                        type=str,
                        action="store",
                        default="out")
    args = parser.parse_args()

    tot_nodes = args.n
    max_sons = args.s
    n_labels = args.l
    out_prefix = args.out
    full = args.full

    g = Digraph('G', filename=out_prefix + ".gv")

    labels = list(string.ascii_uppercase)
    i = 1
    while n_labels > len(labels):
        labels += [x * i for x in list(string.ascii_uppercase)]
        i += 1
    reserved_labels = labels[0:tot_nodes]
    random.shuffle(reserved_labels)
    additional_labels = labels[tot_nodes:tot_nodes + n_labels - tot_nodes]
    nodes2addlabel = {}
    for label in additional_labels:
        node_idx = random.choice(list(range(1, tot_nodes + 1)))
        nodes2addlabel[node_idx] = label if node_idx not in nodes2addlabel else nodes2addlabel[node_idx] + "," + label

    added_nodes = 0
    label = "root"
    g.node(str(added_nodes), label)
    last_nodes = [added_nodes]
    added_nodes += 1

    while added_nodes != tot_nodes:
        father = last_nodes.pop(0)
        n_sons = max_sons if args.full else random.randint(1, max_sons)
        for i in range(0, n_sons):
            if added_nodes == tot_nodes:
                break
            son_label = reserved_labels[added_nodes - 1]
            if added_nodes in nodes2addlabel:
                son_label += "," + nodes2addlabel[added_nodes]
            g.node(str(added_nodes), son_label)
            g.edge(str(father), str(added_nodes))
            last_nodes.append(added_nodes)
            added_nodes += 1

    g.render()
    graphviz.render("dot", "png", out_prefix + ".gv")


if __name__ == "__main__":
    main()
