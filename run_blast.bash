# WARNING this will currently spit everything out into the current directory

THREADS=48

# make blast databases for each split 
time makeblastdb -in db0.fa -dbtype prot -blastdb_version 5
time makeblastdb -in db1.fa -dbtype prot -blastdb_version 5
time makeblastdb -in db2.fa -dbtype prot -blastdb_version 5
time makeblastdb -in db3.fa -dbtype prot -blastdb_version 5
time makeblastdb -in db4.fa -dbtype prot -blastdb_version 5

time blastp -db db0.fa -query search.fa -outfmt 5 -out result0.xml -num_threads $THREADS

time blastp -db db1.fa -query search.fa -outfmt 5 -out result1.xml -num_threads $THREADS

time blastp -db db2.fa -query search.fa -outfmt 5 -out result2.xml -num_threads $THREADS

time blastp -db db3.fa -query search.fa -outfmt 5 -out result3.xml -num_threads $THREADS

time blastp -db db4.fa -query search.fa -outfmt 5 -out result4.xml -num_threads $THREADS 
