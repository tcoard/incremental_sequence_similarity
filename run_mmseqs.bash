#!/bin/bash
RUN_DIR="run_data"

# make database for each split
mmseqs createdb split0.fa $RUN_DIR/db0
mmseqs createdb split1.fa $RUN_DIR/split1
mmseqs createdb split2.fa $RUN_DIR/split2
mmseqs createdb split3.fa $RUN_DIR/split3
mmseqs createdb split4.fa $RUN_DIR/split4

# perform search
mmseqs easy-search search.fa $RUN_DIR/db0 $RUN_DIR/search0.m8 tmp

# add the next split and its headers to the cummulative database
mmseqs concatdbs $RUN_DIR/db0 $RUN_DIR/split1 $RUN_DIR/db1
mmseqs concatdbs $RUN_DIR/db0_h $RUN_DIR/split1_h $RUN_DIR/db1_h

mmseqs easy-search search.fa $RUN_DIR/db1 $RUN_DIR/search1.m8 tmp


mmseqs concatdbs $RUN_DIR/db1 $RUN_DIR/split2 $RUN_DIR/db2
mmseqs concatdbs $RUN_DIR/db1_h $RUN_DIR/split2_h $RUN_DIR/db2_h
mmseqs easy-search search.fa $RUN_DIR/db2 $RUN_DIR/search2.m8 tmp

mmseqs concatdbs $RUN_DIR/db2 $RUN_DIR/split3 $RUN_DIR/db3
mmseqs concatdbs $RUN_DIR/db2_h $RUN_DIR/split3_h $RUN_DIR/db3_h
mmseqs easy-search search.fa $RUN_DIR/db3 $RUN_DIR/search3.m8 tmp

mmseqs concatdbs $RUN_DIR/db3 $RUN_DIR/split4 $RUN_DIR/db4
mmseqs concatdbs $RUN_DIR/db3_h $RUN_DIR/split4_h $RUN_DIR/db4_h
mmseqs easy-search search.fa $RUN_DIR/db4 $RUN_DIR/search4.m8 tmp
