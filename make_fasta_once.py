import random
import pandas as pd
import numpy as np

OUT_DIR = "100"
RANDOM_STATE = 1
NUM_SPLITS = 5
TOT_NUM_DATABASE_SEQ = 100000
TOT_NUM_SEARCH_SEQ = 1000
NUM_PER_SECTION = int(TOT_NUM_SEARCH_SEQ * 0.09)
NUM_NO_SHARED_COG = int(TOT_NUM_SEARCH_SEQ * 0.1)
REC_COUNT = 0

random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

COLUMNS = ["id", "seq", "cog"]


def to_fasta(df: pd.DataFrame) -> str:
    """Turns a dataframe of sequences into a fasta file"""
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


def get_rand_samp_from_cog(
    cog: str,
    get_samp_from: pd.DataFrame,
    sampled_cogs: pd.DataFrame,
    search_seqs: pd.DataFrame,
    get_cog_from: pd.DataFrame,
    being_added_cog: pd.DataFrame,
) -> pd.DataFrame:
    """from a given cog, get a random sample that is not already in the search query or search database"""

    # this happens when we cannot find any samples for a cog
    # that are not already in the search sequences
    # it has not run in any of my tests yet, the recursion further down has been enough
    if get_samp_from.empty:
        print(f"{cog} failed, choosing: ", end="")
        cog = get_cog_from[get_cog_from["cog"] != sampled_cogs["cog"]].sample(n=1)

    sample = get_samp_from.loc[get_samp_from["cog"] == cog].sample(n=1)

    # if the chosen sample is already in the search query or search database, we need to choose another sequence
    if sample["id"].values[0] in set(search_seqs["id"].values).union(set(being_added_cog["id"].values)):
        # remove last chosen sequence from the sequences we can choose from
        get_samp_from = get_samp_from[get_samp_from["id"].values != sample["id"].values]

        # just here for debugging
        global REC_COUNT  # pylint: disable=global-statement
        REC_COUNT += 1
        print(f"{REC_COUNT=}")

        # try again
        sample = get_rand_samp_from_cog(cog, get_samp_from, sampled_cogs, search_seqs, get_cog_from, being_added_cog)

    return sample


def get_search_sequences(split: pd.DataFrame, left_out: pd.DataFrame, search_seqs: pd.DataFrame) -> pd.DataFrame:
    """For a split, generate all of the search sequences related to that split.
    This will be NUM_PER_SECTION sequences that match exactly and
    NUM_PER_SECTION sequences that share a COG with a sequence in this split, but are not in any of the splits
    """
    being_added_exact = split.sample(n=NUM_PER_SECTION)
    with open(f"{OUT_DIR}/exact_matches.txt", "a") as f:
        print("\n".join(being_added_exact["id"].values), file=f)

    being_added_cog = pd.DataFrame(columns=COLUMNS)
    sampled_cogs = split["cog"].sample(n=NUM_PER_SECTION)
    for cog in sampled_cogs:
        being_added_cog = being_added_cog.append(
            get_rand_samp_from_cog(cog, left_out, sampled_cogs, search_seqs, split, being_added_cog)
        )

    with open(f"{OUT_DIR}/cog_matches.txt", "a") as f:
        print("\n".join(being_added_cog["id"].values), file=f)

    merged = pd.concat([being_added_exact, being_added_cog])
    return merged


def main() -> None:
    """Partition data into 5 splits that make up the search database and generate the search query sequences"""
    df = pd.read_pickle("all_cogs.pkl")

    # i need to make sure that none of the sequences chosen belong to cogs that will be chosen

    df["Frequency"] = df.groupby("cog")["cog"].transform("count")
    # keep the duplicates from the biggest cogs
    # so that when no_cog_match is taking sequences from the small cogs,
    # it doesn't take a sequence that belongs to multiple cogs
    df = df.sort_values("Frequency", ascending=False)

    # put the smallest cogs at the top
    df = df.sort_values("Frequency", ascending=True)
    df = df.drop("Frequency", axis=1)

    no_cog_match = df.drop_duplicates(subset=["id"]).head(NUM_NO_SHARED_COG)
    if no_cog_match.shape != no_cog_match.drop_duplicates(subset=["id"]).shape:
        # this didn't happen in testing so I am not writing code to fix it now
        # but it shouldn't happen
        raise NotImplementedError

    # for each id in the df to remove
    # get their cogs
    # get all sequences in the master db that have that cog
    # remove those sequences
    df = df[~df["id"].isin(df[df["cog"].isin(df[df["id"].isin(no_cog_match["id"])]["cog"])]["id"])]
    # remove duplicate samples so that they are not chosen twice
    df = df.drop_duplicates(subset=["id"])

    with open(f"{OUT_DIR}/no_cog_matches.txt", "w") as f:
        print("\n".join(no_cog_match["id"].values), file=f)

    final_db = df.sample(n=TOT_NUM_DATABASE_SEQ)
    left_out = df.merge(final_db, how="outer", indicator=True).loc[lambda x: x["_merge"] == "left_only"]
    left_out = left_out.drop(columns=["_merge"])

    search_seqs = pd.DataFrame(columns=COLUMNS)
    # ".sample(frac=1)" shuffles the rows of final_db around
    for i, split in enumerate(np.array_split(final_db.sample(frac=1), NUM_SPLITS)):
        search_seqs = search_seqs.append(get_search_sequences(split, left_out, search_seqs))

        # remove sequences already used so that there are not any duplicates
        to_remove = left_out["id"].isin(search_seqs["id"])
        left_out = left_out.drop(left_out[to_remove].index)

        with open(f"{OUT_DIR}/split{i}.fa", "w") as f:
            f.write(to_fasta(split))

    # no_cog_match_all = left_out.merge(final_db, how="outer", indicator=True).loc[lambda x: x["_merge"] == "left_only"]
    # no_cog_match_all = no_cog_match_all.drop(columns=["_merge"])
    # no_cog_match = no_cog_match_all.sample(n=NUM_NO_SHARED_COG)

    search_seqs = search_seqs.append(no_cog_match)

    with open(f"{OUT_DIR}/search.fa", "w") as f:
        f.write(to_fasta(search_seqs))

    # For debugging
    # print("db:", final_db.drop_duplicates(subset=["cog"]).shape[0])
    # print("left out:", left_out.drop_duplicates(subset=["cog"]).shape[0])
    # print("search sequences:", search_seqs.drop_duplicates(subset=["cog"]).shape[0])


if __name__ == "__main__":
    main()
