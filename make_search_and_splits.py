import random
import pandas as pd
import numpy as np

OUT_DIR = "data"
RANDOM_STATE = 1
NUM_SPLITS = 5
TOT_NUM_DATABASE_SEQ = 100000
NUM_PER_SECTION = int(TOT_NUM_DATABASE_SEQ * 0.09)
NUM_NO_SHARED_COG = int(TOT_NUM_DATABASE_SEQ * 0.1)
REC_COUNT = 0
# TOT_NUM_SEARCH_SEQ = 100
# NUM_SEARCH_SEQ = int(TOT_NUM_SEARCH_SEQ / NUM_SPLITS)  # 200

random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

COLUMNS = ["id", "seq", "cog"]


def to_fasta(df: pd.DataFrame) -> str:
    fasta = str()
    # cog_map = str()
    ids = set()
    for _, row in df.iterrows():
        if row["id"] not in ids:
            ids.add(row["id"])
            fasta += f">{row['id']}\n"
            fasta += f"{row['seq']}\n"
            # cog_map += f"{row['id']} {row['cog']}\n"
        else:
            print(row)
    return fasta  # , cog_map


def get_rand_samp_from_rand_cog(
    cog: str,
    get_samp_from: pd.DataFrame,
    sampled_cogs: pd.DataFrame,
    search_seqs: pd.DataFrame,
    get_cog_from: pd.DataFrame,
    being_added_cog: pd.DataFrame,
) -> pd.DataFrame:
    """get samp_amount cogs and then take 1 random sample from each cog"""

    # this happens when we cannot find any samples for a cog
    # that are not already in the search sequences
    if get_samp_from.empty:
        print(f"{cog} failed, choosing: ", end="")
        cog = get_cog_from[get_cog_from["cog"] != sampled_cogs["cog"]].sample(n=1)

    sample = get_samp_from.loc[get_samp_from["cog"] == cog].sample(n=1)

    if sample["id"].values[0] in set(search_seqs["id"].values).union(set(being_added_cog["id"].values)):
        # remove last chosen sequence
        get_samp_from = get_samp_from[get_samp_from["id"].values != sample["id"].values]
        # try again
        global REC_COUNT
        REC_COUNT += 1
        print(f"{REC_COUNT=}")
        sample = get_rand_samp_from_rand_cog(cog, get_samp_from, sampled_cogs, search_seqs, get_cog_from, being_added_cog)

    return sample


def get_search(split: pd.DataFrame, left_out: pd.DataFrame, search_seqs: pd.DataFrame) -> pd.DataFrame:
    being_added_exact = split.sample(n=NUM_PER_SECTION)

    being_added_cog = pd.DataFrame(columns=COLUMNS)
    sampled_cogs = split["cog"].sample(n=NUM_PER_SECTION)
    for cog in sampled_cogs:
        being_added_cog = being_added_cog.append(
            get_rand_samp_from_rand_cog(cog, left_out, sampled_cogs, search_seqs, split, being_added_cog)
        )

    merged = pd.concat([being_added_exact, being_added_cog])
    return merged


def main() -> None:
    df = pd.read_pickle("all_cogs.pkl")
    df = df.drop_duplicates(subset=["id"])
    final_db = df.sample(n=TOT_NUM_DATABASE_SEQ)
    left_out = df.merge(final_db, how="outer", indicator=True).loc[lambda x: x["_merge"] == "left_only"]
    left_out = left_out.drop(columns=["_merge"])

    search_seqs = pd.DataFrame(columns=COLUMNS)
    for i, split in enumerate(np.array_split(final_db.sample(frac=1), NUM_SPLITS)):
        search_seqs = search_seqs.append(get_search(split, left_out, search_seqs))

        # remove sequences already used so that there are not any duplicates
        to_remove = left_out["id"].isin(search_seqs["id"])
        left_out = left_out.drop(left_out[to_remove].index)

        with open(f"{OUT_DIR}/split{i}.fa", "w") as f:
            f.write(to_fasta(split))

    no_cog_match_all = left_out.merge(final_db, how="outer", indicator=True).loc[lambda x: x["_merge"] == "left_only"]
    no_cog_match_all = no_cog_match_all.drop(columns=["_merge"])
    no_cog_match = no_cog_match_all.sample(n=NUM_NO_SHARED_COG)
    search_seqs = search_seqs.append(no_cog_match)

    # no_cog_match = get_rand_samp_from_rand_cog(no_cog_match_all, no_cog_match_all, samp_amount=NUM_NO_SHARED_COG)

    with open(f"{OUT_DIR}/search.fa", "w") as f:
        f.write(to_fasta(search_seqs))

    # print("db:", final_db.drop_duplicates(subset=["cog"]).shape[0])
    # print("left out:", left_out.drop_duplicates(subset=["cog"]).shape[0])
    # print("search sequences:", search_seqs.drop_duplicates(subset=["cog"]).shape[0])


if __name__ == "__main__":
    main()
