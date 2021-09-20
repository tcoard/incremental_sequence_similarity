import glob
import pickle
from collections import defaultdict
import pandas as pd


def main():
    # split seq into cogs
    # take n test cogs
    # take x% of those cogs
    # take a few seq to run blast on
    # Repeat
    # increase x
    # take a few seq to run blast on

    id_cog = dict()

    ids = list()
    seqs = list()
    cogs = list()
    sid_cogs = defaultdict(list)
    for fname in glob.glob("fasta/*.fa"):
        # for fname in glob.glob(f"fasta/COG2906.fa"):
        print(fname)
        cog = fname.split(".")[0].split("/")[1]
        curr_id = ""
        seq = ""
        with open(fname, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    # ignore the first capture
                    if curr_id:
                        ids.append(curr_id)
                        seqs.append(seq)
                        cogs.append(cog)
                        # df_row = pd.DataFrame([[curr_id, seq, cog]], columns=columns)
                        # df = df.append(df_row)

                    curr_id = line.split(" ")[0][1:]
                    seq = ""
                else:
                    seq += line

            # last seq
            if curr_id:
                ids.append(curr_id)
                seqs.append(seq)
                cogs.append(cog)
                # df_row = pd.DataFrame([[curr_id, seq, cog]], columns=columns)
                # df = df.append(df_row)

    columns = ["id", "seq", "cog"]
    # print(ids)
    # df = pd.DataFrame(list(zip(ids, seqs, cogs)), columns=columns)
    # df.to_pickle("all_cogs.pkl")
    for sid, _, cog in list(zip(ids, seqs, cogs)):
        sid_cogs[sid].append(cog)
    with open("sid_cogs.pkl", "wb") as f:
        pickle.dump(sid_cogs, f)


if __name__ == "__main__":
    main()
