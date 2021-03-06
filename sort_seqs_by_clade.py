#!/usr/bin/env python3
"""Given a tree topology (with at least three monophyletic clades of interest),
a set of (at least three) sequence names defining clades of interest in the
tree topology, and a FASTA file containing all sequences represented in the
tree, this script generates a FASTA file for sequences contained in each of the
clades.

Usage:
    python3 sort_seqs_by_clade.py <topology file in newick format> \
                                  <file listing reference sequence names> \
                                  <fasta file with all sequences> \
                                  <path to output directory to be generated>
"""
import os
import sys
import shutil
from ete3 import Tree
from Bio import SeqIO


def retrieve_clade_seqs(topology_newick_file,
                        reference_seq_names_file, 
                        input_fasta_file,
                        output_fasta_directory):
    """Main function for retrieving sequences for specific clades.
    """
    # Parse the resulting tree to determine in which clade of interest, if any,
    # the sequence was placed.

    # Parse tree using ete3.
    # Note: parentheses and commas get replaced with underscores.
    t1 = Tree(topology_newick_file, quoted_node_names=True)

    # Print tree.
    #print('Full tree:')
    #print(t1)

    # Make a copy of the tree object.
    t2 = t1.copy()

    # Get list of reference sequences from input.
    ref_seq_list = []
    for i in open(reference_seq_names_file):
        ref_seq_list.append(i.strip().split(',')[0])
    print('\nReference sequences:')
    for x in ref_seq_list:
        print(x)
    print()

    # Check that there are at least three reference sequences defined.
    assert len(ref_seq_list) >= 3, """Less than three reference sequences are
    named in the file %s.""" % reference_seq_names_file

    # Check that all the reference sequences are all in the tree topology.
    all_leaf_names = [x.name for x in t2.get_leaves()]
    for ref_seq_name in ref_seq_list:
        assert ref_seq_name in all_leaf_names, """Reference sequence %s was not
        found among the sequences represented in the tree %s.""" % \
        (ref_seq_name, topology_newick_file)

    # Initiate dict to store lists of seq names by ref seq name.
    seq_names_by_ref_seq_name = {}

    # For each reference sequence, traverse all nodes and find the node with
    # the largest number of child nodes that are leaf (terminal) nodes,
    # containing the reference sequence of interest, but not containing any of
    # the other reference sequences.
    ts_num = 0
    first_ref_seq_node_name = None
    ts_that_additional_seq_was_placed_in = None
    for ts in ref_seq_list:
        ts_num += 1

        if ts_num == 1:
            first_ref_seq_node_name = ts
            # Root on another reference sequence for the first reference sequence in
            # the list to get whole clade, then root the tree on the ancestor
            # node of that first clade.

            # Get a node name for a node corresponding to a different
            # reference sequence.
            other_ref_seq_node_name = None
            for i in ref_seq_list:
                if i != ts:
                    other_ref_seq_node_name = i
                    break

            # Get node corresponding to a different reference sequence.
            other_ref_seq_node = None
            for node in t2.traverse():
                if node.name == other_ref_seq_node_name:
                    other_ref_seq_node = node
                    break
            assert other_ref_seq_node is not None

            # Root on the other reference sequence node.
            t2.set_outgroup(other_ref_seq_node)

        elif ts_num == 2:
            # Root on the first reference sequence node for all subsequent
            # clades.
            first_ref_seq_node = None
            for node in t2.traverse():
                leaf_list = []
                for leaf in node.get_leaves():
                    if leaf.name == first_ref_seq_node_name:
                        first_ref_seq_node = node
                        break
            t2.set_outgroup(first_ref_seq_node)

        # Make a copy of the tree topology to work with for each run
        # through this loop.
        t3 = t2.copy()

        # Make a list of nodes that contain reference seq, but not any others.
        nodes_of_interest = []
        for node in t3.traverse():
            # Search in nodes that contain the reference sequence.
            if node.search_nodes(name=ts):
                # Search in nodes that don't contain other reference sequences.
                contains_other_ref_seqs = False
                for ts2 in ref_seq_list:
                    if not ts2 == ts:
                        if node.search_nodes(name=ts2):
                            contains_other_ref_seqs = True
                if not contains_other_ref_seqs:
                    # Add nodes of interest to list.
                    nodes_of_interest.append(node)

        # find the node with the most child leaf nodes.
        node_w_most_leaves = sorted(nodes_of_interest, key=lambda x:\
                len(x.get_leaves()), reverse=True)[0]
        node_w_most_leaves.name = 'X'
        print('\n\nClade defined by sequence ' + ts + ':')
        print(node_w_most_leaves)

        # Add list of leaf names from this clade to the dict.
        seq_names_by_ref_seq_name[ts] = [x.name for x in \
                                         node_w_most_leaves.get_leaves()]

    # Print number of sequences in each clade.
    print('\nNumber of sequences in each clade:')
    sorted_keys = sorted(seq_names_by_ref_seq_name.keys(),
                         key=lambda x: len(seq_names_by_ref_seq_name[x]),
                         reverse=True)
    for key in sorted_keys:
        print(key + ':\t' + str(len(seq_names_by_ref_seq_name[key])))

    # Parse input FASTA file.
    all_seqs = list(SeqIO.parse(input_fasta_file, 'fasta'))

    # Make output directory.
    if os.path.isdir(output_fasta_directory):
        shutil.rmtree(output_fasta_directory)
    os.mkdir(output_fasta_directory)

    # Write relevant sequences to output FASTA files.
    for ref_seq_name in ref_seq_list:
        # Define list of sequence objects to be written to output.
        clade_specific_seq_objs = [x for x in all_seqs if x.id in \
                seq_names_by_ref_seq_name[ref_seq_name]]

        # Define path to output FASTA file.
        output_fasta_file = os.path.join(output_fasta_directory,
                                         ref_seq_name.replace(' ',
                                             '_').replace('/', '_') +\
                                         '__clade.faa'
                                         )

        # Open output FASTA file.
        with open(output_fasta_file, 'w') as o:
            # Write relevant sequences to the file.
            SeqIO.write(clade_specific_seq_objs, o, 'fasta')
            

if __name__ == '__main__':

    # Parse command line arguments.
    cmdln = sys.argv
    topology_newick_file = cmdln[1]
    reference_seq_names_file = cmdln[2]
    input_fasta_file = cmdln[3]
    output_fasta_directory = cmdln[4]

    retrieve_clade_seqs(topology_newick_file,
                        reference_seq_names_file, 
                        input_fasta_file,
                        output_fasta_directory)
