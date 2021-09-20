#!/bin/bash

# WARNING this will currently spit everything out into the current directory

THREADS=18

time diamond makedb --in db0.fa -d db0
time diamond makedb --in db1.fa -d db1
time diamond makedb --in db2.fa -d db2
time diamond makedb --in db3.fa -d db3
time diamond makedb --in db4.fa -d db4


time diamond blastp -d db0 -q search.fa -o results0.tsv --threads $THREADS --sensitive
time diamond blastp -d db1 -q search.fa -o results1.tsv --threads $THREADS --sensitive
time diamond blastp -d db2 -q search.fa -o results2.tsv --threads $THREADS --sensitive
time diamond blastp -d db3 -q search.fa -o results3.tsv --threads $THREADS --sensitive
time diamond blastp -d db4 -q search.fa -o results4.tsv --threads $THREADS --sensitive
