"""gets the roc1"""
import pickle
from functools import partial
from collections import defaultdict
from multiprocessing import Pool

DATA_DIR = "final_data"

with open("sid_cogs.pkl", "rb") as f:
    sid_cogs = pickle.load(f)


def get_auc(seq_dict, current_db_seqs_df, seq_id):
    true_pos = 0
    had_false_positive = False
    for match, _ in seq_dict[seq_id]:
        # if there are no shared cogs
        if set(sid_cogs[match]).isdisjoint(sid_cogs[seq_id]):
            # print(seq_id, match, evalue)
            had_false_positive = True
            break
        true_pos += 1
    total_seq_with_cog_in_db = sum([len(current_db_seqs_df[cog]) for cog in sid_cogs[seq_id]])

    return (true_pos, total_seq_with_cog_in_db, had_false_positive, seq_id)


def write_files(i, current_db_seqs_df, matches, alg_type, seq_type):

    # with Pool(18) as pool:
    if alg_type == "mm":
        in_file_prefix = "mm_matches"
        out_file_prefix = "mmseq_auc_"
    elif alg_type == "ib":
        in_file_prefix = "ib_matches"
        out_file_prefix = "iblast_auc_"
    elif alg_type == "nb":
        in_file_prefix = "nb_matches"
        out_file_prefix = "nblast_auc_"
    elif alg_type == "di":
        in_file_prefix = "di_matches"
        out_file_prefix = "diamond_auc_"

    with open(f"{DATA_DIR}/{in_file_prefix}{i}.pkl", "rb") as f:
        seq_dict = pickle.load(f)
    # func = partial(get_auc, seq_dict, current_db_seqs_df)
    # aucs = pool.map(func, matches)
    for match in matches:
        auc = get_auc(seq_dict, current_db_seqs_df, match)
        with open(f"{DATA_DIR}/{out_file_prefix}{seq_type}{i}.txt", "a") as out:
            # for auc in aucs:
            out.write(f"{auc}\n")
            if auc[1] != 0:
                out.write(f"{auc[0]/auc[1]}\n")
            else:
                out.write(f"NaN\n")


def main():  # pylint: disable=too-many-locals

    exact_matches = []
    with open(f"{DATA_DIR}/exact_matches.txt", "r") as f:
        exact_matches = [line.strip() for line in f]

    cog_matches = []
    with open(f"{DATA_DIR}/cog_matches.txt", "r") as f:
        cog_matches = [line.strip() for line in f]

    no_cog_matches = []
    with open(f"{DATA_DIR}/no_cog_matches.txt", "r") as f:
        no_cog_matches = [line.strip() for line in f]

    current_db_seqs = []  # this grows with each split
    for i in range(5):
        with open(f"{DATA_DIR}/split{i}.fa", "r") as f:
            for line in f:
                if line.startswith(">"):
                    current_db_seqs.append(line.strip()[1:])
        # current_db_seqs_df = df[df["id"].isin(current_db_seqs)]
        # current_db_seqs_df = {sid: sid_cogs[sid] for sid in current_db_seqs}
        current_db_seqs_df = defaultdict(list)
        for sid in current_db_seqs:
            for cog in sid_cogs[sid]:
                current_db_seqs_df[cog].append(sid)

        for alg_type in ("mm", "ib", "nb", "di"):
            write_files(i, current_db_seqs_df, exact_matches, alg_type, "exact")
            write_files(i, current_db_seqs_df, cog_matches, alg_type, "cog")
            write_files(i, current_db_seqs_df, no_cog_matches, alg_type, "no_cog")


if __name__ == "__main__":
    main()
