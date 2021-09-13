"""gets the roc1"""
import pickle
from functools import partial
from multiprocessing import Pool
import pandas as pd

DATA_DIR = "data"


def get_auc(seq_dict, df, current_db_seqs_df, seq_id):
    true_pos = 0
    had_false_positive = False
    for match, evalue in seq_dict[seq_id]:
        # if there are no shared cogs
        if set(df[df["id"] == match]["cog"].values).isdisjoint(df[df["id"] == seq_id]["cog"].values):
            # print(seq_id, match, evalue)
            had_false_positive = True
            break
        true_pos += 1

    total_seq_with_cog_in_db = current_db_seqs_df[current_db_seqs_df["cog"].isin(df[df["id"] == seq_id]["cog"])].shape[
        0
    ]

    return (true_pos, total_seq_with_cog_in_db, had_false_positive, seq_id)


def write_files(i, df, current_db_seqs_df, matches, seq_type):
    with Pool() as pool:
        with open(f"{DATA_DIR}/mm_matches{i}.pkl", "rb") as f:
            mm_matches = pickle.load(f)
        mmseq_func = partial(get_auc, mm_matches, df, current_db_seqs_df)
        mmseq_aucs = pool.map(mmseq_func, matches)
        with open(f"{DATA_DIR}/mmseq_auc_{seq_type}{i}.txt", "w") as out:
            for auc in mmseq_aucs:
                out.write(f"{auc}\n")
                out.write(f"{auc[0]/auc[1]}\n")

        with open(f"{DATA_DIR}/ib_matches{i}.pkl", "rb") as f:
            ib_matches = pickle.load(f)
        iblast_func = partial(get_auc, ib_matches, df, current_db_seqs_df)
        iblast_aucs = pool.map(iblast_func, matches)
        with open(f"{DATA_DIR}/iblast_auc_{seq_type}.txt{i}", "w") as out:
            for auc in iblast_aucs:
                out.write(f"{auc}\n")
                out.write(f"{auc[0]/auc[1]}\n")

        with open(f"{DATA_DIR}/nb_matches{i}.pkl", "rb") as f:
            nb_matches = pickle.load(f)
        nblast_func = partial(get_auc, nb_matches, df, current_db_seqs_df)
        nblast_aucs = pool.map(nblast_func, matches)
        with open(f"{DATA_DIR}/nblast_auc_{seq_type}.txt{i}", "w") as out:
            for auc in nblast_aucs:
                out.write(f"{auc}\n")
                out.write(f"{auc[0]/auc[1]}\n")

        with open(f"{DATA_DIR}/di_matches{i}.pkl", "rb") as f:
            di_matches = pickle.load(f)
        diamond_func = partial(get_auc, di_matches, df, current_db_seqs_df)
        diamond_aucs = pool.map(diamond_func, matches)
        with open(f"{DATA_DIR}/diamond_auc_{seq_type}.txt{i}", "w") as out:
            for auc in diamond_aucs:
                out.write(f"{auc}\n")
                out.write(f"{auc[0]/auc[1]}\n")


def main():  # pylint: disable=too-many-locals
    df = pd.read_pickle("all_cogs.pkl")
    # need to save space with pool.map
    df = df.drop(columns=["seq"])

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
        current_db_seqs_df = df[df["id"].isin(current_db_seqs)]

        write_files(i, df, current_db_seqs_df, exact_matches, "exact")
        write_files(i, df, current_db_seqs_df, cog_matches, "cog")
        write_files(i, df, current_db_seqs_df, no_cog_matches, "no_cog")


if __name__ == "__main__":
    main()
