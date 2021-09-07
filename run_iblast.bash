#!/bin/bash

# WARNING this will currently spit everything out into the current directory

THREADS=18

# Initialize the database
rm incblast.db
python -c "import sys; sys.path.insert(0, '../../iBLAST/source');import DBUtility; DBUtility.initialize_database()"

# make blast databases for each split
makeblastdb -in split0.fa -dbtype prot -blastdb_version 5
makeblastdb -in split1.fa -dbtype prot -blastdb_version 5
makeblastdb -in split2.fa -dbtype prot -blastdb_version 5
makeblastdb -in split3.fa -dbtype prot -blastdb_version 5
makeblastdb -in split4.fa -dbtype prot -blastdb_version 5

# add database to the cummulative database
time blastdb_aliastool -dblist "split0.fa" -dbtype prot -out total -title "total"
# perform blast search
time python3 ../../iBLAST/source/iBLAST.py "blastp -db total -query search.fa -outfmt 5 -out result0.xml -num_threads $THREADS"

time blastdb_aliastool -dblist "split0.fa split1.fa" -dbtype prot -out total -title "total"
time python3 ../../iBLAST/source/iBLAST.py "blastp -db total -query search.fa -outfmt 5 -out result1.xml -num_threads $THREADS"

time blastdb_aliastool -dblist "split0.fa split1.fa split2.fa" -dbtype prot -out total -title "total"
time python3 ../../iBLAST/source/iBLAST.py "blastp -db total -query search.fa -outfmt 5 -out result2.xml -num_threads $THREADS"

time blastdb_aliastool -dblist "split0.fa split1.fa split2.fa split3.fa" -dbtype prot -out total -title "total"
time python3 ../../iBLAST/source/iBLAST.py "blastp -db total -query search.fa -outfmt 5 -out result3.xml -num_threads $THREADS"

time blastdb_aliastool -dblist "split0.fa split1.fa split2.fa split3.fa split4.fa" -dbtype prot -out total -title "total"
time python3 ../../iBLAST/source/iBLAST.py "blastp -db total -query search.fa -outfmt 5 -out result4.xml -num_threads $THREADS"
