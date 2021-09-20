# incremental_sequence_similarity
The workflow is (note the workflow currently requires manual set up):
* Download the COG data.
* Run `make_fasta_once.py` to make the search and database split fastas.
* Run the `run*.bash` files to run each algorithm.
* Run `format.py` to make a pkl object of the cog data.
* Run `make_match_dict.py` to pull the results into smaller and more readable files.
* Run `parse_res_roc.py` to generate the AUC1 data.
* Then one can run any of the other scripts to generate graphs for different metrics.

## TODO
Comment the code

### NOTES:
I would statically type more of the code, but the server I use uses an older version of python and I don't want
to figure out why typing syntax works by default and what doesn't. So the code that is typed is run locally.
