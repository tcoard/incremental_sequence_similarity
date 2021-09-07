#!/bin/bash
THREADS=18
RUN_DIR="run_data"
mkdir -p $RUN_DIR

# make database for each split
time mmseqs createdb split0.fa $RUN_DIR/db0
time mmseqs createdb split1.fa $RUN_DIR/split1
time mmseqs createdb split2.fa $RUN_DIR/split2
time mmseqs createdb split3.fa $RUN_DIR/split3
time mmseqs createdb split4.fa $RUN_DIR/split4

time # perform search
time mmseqs easy-search search.fa $RUN_DIR/db0 $RUN_DIR/search0.m8 tmp --threads $THREADS

time # add the next split and its headers to the cummulative database
time mmseqs concatdbs $RUN_DIR/db0 $RUN_DIR/split1 $RUN_DIR/db1
time mmseqs concatdbs $RUN_DIR/db0_h $RUN_DIR/split1_h $RUN_DIR/db1_h
time mmseqs easy-search search.fa $RUN_DIR/db1 $RUN_DIR/search1.m8 tmp --threads $THREADS

time mmseqs concatdbs $RUN_DIR/db1 $RUN_DIR/split2 $RUN_DIR/db2
time mmseqs concatdbs $RUN_DIR/db1_h $RUN_DIR/split2_h $RUN_DIR/db2_h
time mmseqs easy-search search.fa $RUN_DIR/db2 $RUN_DIR/search2.m8 tmp --threads $THREADS

time mmseqs concatdbs $RUN_DIR/db2 $RUN_DIR/split3 $RUN_DIR/db3
time mmseqs concatdbs $RUN_DIR/db2_h $RUN_DIR/split3_h $RUN_DIR/db3_h
time mmseqs easy-search search.fa $RUN_DIR/db3 $RUN_DIR/search3.m8 tmp --threads $THREADS

time mmseqs concatdbs $RUN_DIR/db3 $RUN_DIR/split4 $RUN_DIR/db4
time mmseqs concatdbs $RUN_DIR/db3_h $RUN_DIR/split4_h $RUN_DIR/db4_h
time mmseqs easy-search search.fa $RUN_DIR/db4 $RUN_DIR/search4.m8 tmp --threads $THREADS
