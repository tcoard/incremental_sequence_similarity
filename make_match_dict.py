import pickle
import re
from collections import defaultdict

IBLAST_RESULTS = "iblast_run"
MMSEQS_RESULTS = "mmseqs2_run/run_data"
BLAST_RESULTS = "blast_run"
DIAMOND_RESULTS = "diamond_run"


def parse_iblast(i, is_normal_blast):
    seq_matches = defaultdict(list)
    file_name = ""
    if is_normal_blast:
        file_name = f"{BLAST_RESULTS}/result{i}.xml"
    else:
        file_name = f"{IBLAST_RESULTS}/result{i}.xml"
    with open(file_name, "r") as f:
        search_id = ""
        match_id = ""
        evalue = 0
        for line in f:
            line = line.strip()
            if line.startswith("<Iteration_query-def>"):
                search_id = re.match(r".*>([^<]+)<.*", line).group(1)
            else:
                if line.startswith("<Hit_def>"):
                    match_id = re.match(r".*>([^<]+)<.*", line).group(1)
                elif line.startswith("<Hsp_evalue>"):
                    evalue = re.match(r".*>([^<]+)<.*", line).group(1)
                    seq_matches[search_id].append((match_id, evalue))

    return seq_matches


def parse_mmseqs(i, is_diamond):
    seq_matches = defaultdict(list)
    file_name = ""
    if is_diamond:
        file_name = f"{DIAMOND_RESULTS}/search{i}.m8"
    else:
        file_name = f"{MMSEQS_RESULTS}/result{i}.tsv"

    with open(file_name, "r") as f:
        search_id = ""
        match_id = ""
        evalue = 0
        for line in f:
            line = line.strip()
            items = line.split("\t")
            search_id = items[0]
            match_id = items[1]
            evalue = items[-2]
            seq_matches[search_id].append((match_id, evalue))

    # with open("mmseqs.json", 'wt') as out:
    #     pp = pprint.PrettyPrinter(indent=4, stream=out)
    #     pp.pprint(seq_matches)
    return seq_matches


def main():  # pylint: disable=too-many-locals
    for i in range(5):
        mm_matches = parse_mmseqs(i, is_diamond=False)
        with open(f"mm_matches{i}.pkl", "wb") as f:
            pickle.dump(mm_matches, f)

        di_matches = parse_mmseqs(i, is_diamond=True)
        with open(f"di_matches{i}.pkl", "wb") as f:
            pickle.dump(di_matches, f)

        ib_matches = parse_iblast(i, is_normal_blast=False)
        with open(f"ib_matches{i}.pkl", "wb") as f:
            pickle.dump(ib_matches, f)

        nb_matches = parse_iblast(i, is_normal_blast=True)
        with open(f"nb_matches{i}.pkl", "wb") as f:
            pickle.dump(nb_matches, f)


if __name__ == "__main__":
    main()
