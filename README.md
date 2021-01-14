
# Script for sorting sequences by clade

## Purpose

Given a tree topology (newick format), a set of sequence names defining clades
of interest in the tree topology, and a FASTA file containing all sequences
represented in the tree, this simple Python script generates an individual
FASTA file for sequences contained in each of the clades.

## Setup

Activate a conda environment from the environment definition file
(`sort_seqs_by_clade_conda_env.yaml`).
    

## Usage

```
python3 sort_seqs_by_clade.py <topology file in newick format> \
                              <file listing reference sequence names> \
                              <fasta file with all sequences> \
                              <path to output directory to be generated>
```
