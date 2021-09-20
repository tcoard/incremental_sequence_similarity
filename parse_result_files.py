import pprint
import re
from collections import defaultdict
import pandas as pd
import seaborn as sns

# import pickle

IBLAST_RESULTS = "1k_iblast_latest"
MMSEQS_RESULTS = "1k_mmseqs_lastest/run_data"
META_DATA = "1k_mmseqs_lastest"

# <Hit>
#   <Hit_num>1</Hit_num>
#   <Hit_id>gnl|BL_ORD_ID|8296</Hit_id>
#   <Hit_def>WP_094062158.1</Hit_def>
#   <Hit_accession>8296</Hit_accession>
#   <Hit_len>404</Hit_len>
#   <Hit_hsps>
#     <Hsp>
#       <Hsp_num>1</Hsp_num>
#       <Hsp_bit-score>829.706</Hsp_bit-score>
#       <Hsp_score>2142</Hsp_score>
#       <Hsp_evalue>0</Hsp_evalue>
def parse_iblast(i):
    seq_matches = defaultdict(list)
    with open(f"{IBLAST_RESULTS}/result{i}.xml", "r") as f:
        search_id = ""
        match_id = ""
        evalue = 0
        found_10 = True
        for line in f:
            line = line.strip()
            if line.startswith("<Iteration_query-def>"):
                search_id = re.match(r".*>([^<]+)<.*", line).group(1)
                found_10 = False
            elif not found_10:
                if line.startswith("<Hit_def>"):
                    match_id = re.match(r".*>([^<]+)<.*", line).group(1)
                elif line.startswith("<Hsp_evalue>"):
                    evalue = re.match(r".*>([^<]+)<.*", line).group(1)
                    seq_matches[search_id].append({match_id: evalue})
                    # only get the top 10 matches for now
                    if len(seq_matches[search_id]) == 10:
                        found_10 = True

    # with open("iblast.json", 'wt') as out:
    #     pp = pprint.PrettyPrinter(indent=4, stream=out)
    #     pp.pprint(seq_matches)
    return seq_matches


def parse_mmseqs(i):
    seq_matches = defaultdict(list)
    with open(f"{MMSEQS_RESULTS}/search{i}.m8", "r") as f:
        search_id = ""
        match_id = ""
        completed_id = ""
        evalue = 0
        for line in f:
            line = line.strip()
            items = line.split("\t")
            search_id = items[0]
            if search_id != completed_id:
                match_id = items[1]
                evalue = items[-2]
                seq_matches[search_id].append({match_id: evalue})
                if len(seq_matches[search_id]) == 10:
                    completed_id = search_id

    # with open("mmseqs.json", 'wt') as out:
    #     pp = pprint.PrettyPrinter(indent=4, stream=out)
    #     pp.pprint(seq_matches)
    return seq_matches


def main():  # pylint: disable=too-many-locals
    df = pd.read_pickle("all_cogs.pkl")

    # for i in range(5):
    for i in range(5):
        mm_matches = parse_mmseqs(i)
        ib_matches = parse_iblast(i)
        # cog_matches.txt
        # exact_matches.txt
        # no_cog_matches.txt
        exact_match_discordance = []
        exact_match_discordance_cog = []
        with open(f"{META_DATA}/exact_matches.txt", "r") as f:
            for line in f:
                seq_id = line.strip()
                # next(iter( gets the string of the dict key
                mm_ids = {next(iter(i.keys())) for i in mm_matches[seq_id]}
                ib_ids = {next(iter(i.keys())) for i in ib_matches[seq_id]}
                exact_match_discordance.append(len(mm_ids.symmetric_difference(ib_ids)))
                mm_cogs = set(df[df["id"].isin(mm_ids)]["cog"].values)
                ib_cogs = set(df[df["id"].isin(ib_ids)]["cog"].values)
                exact_match_discordance_cog.append(len(mm_cogs.symmetric_difference(ib_cogs)))

        cog_match_discordance = []
        cog_match_discordance_cog = []
        with open(f"{META_DATA}/cog_matches.txt", "r") as f:
            for line in f:
                seq_id = line.strip()
                mm_ids = {next(iter(i.keys())) for i in mm_matches[seq_id]}
                ib_ids = {next(iter(i.keys())) for i in ib_matches[seq_id]}
                cog_match_discordance.append(len(mm_ids.symmetric_difference(ib_ids)))

                mm_cogs = set(df.loc[df["id"].isin(mm_ids)]["cog"].values)
                ib_cogs = set(df.loc[df["id"].isin(ib_ids)]["cog"].values)
                cog_match_discordance_cog.append(len(mm_cogs.symmetric_difference(ib_cogs)))

        no_cog_match_discordance = []
        no_cog_match_discordance_cog = []
        with open(f"{META_DATA}/no_cog_matches.txt", "r") as f:
            for line in f:
                seq_id = line.strip()
                mm_ids = {next(iter(i.keys())) for i in mm_matches[seq_id]}
                ib_ids = {next(iter(i.keys())) for i in ib_matches[seq_id]}
                no_cog_match_discordance.append(len(mm_ids.symmetric_difference(ib_ids)))

                mm_cogs = set(df.loc[df["id"].isin(mm_ids)]["cog"].values)
                ib_cogs = set(df.loc[df["id"].isin(ib_ids)]["cog"].values)
                no_cog_match_discordance_cog.append(len(mm_cogs.symmetric_difference(ib_cogs)))

        s1 = pd.DataFrame(exact_match_discordance, columns=["Number Nonmatching"])
        s2 = pd.DataFrame(cog_match_discordance, columns=["Number Nonmatching"])
        s3 = pd.DataFrame(no_cog_match_discordance, columns=["Number Nonmatching"])
        s4 = pd.DataFrame(exact_match_discordance_cog, columns=["Number Nonmatching"])
        s5 = pd.DataFrame(cog_match_discordance_cog, columns=["Number Nonmatching"])
        s6 = pd.DataFrame(no_cog_match_discordance_cog, columns=["Number Nonmatching"])
        dfc = pd.concat(
            [s1, s2, s3, s4, s5, s6],
            keys=[
                "Exact Match Seq",
                "Cog Match Seq",
                "No Cog Match Seq",
                "Exact Match COG",
                "Cog Match COG",
                "No Cog Match COG",
            ],
            names=["Type", "Row ID"],
        ).reset_index()
        sns_plot = sns.boxplot(x="Type", y="Number Nonmatching", data=dfc)
        sns_plot.set_title(f"DB Update #{i} (iBLAST vs MMseqs2)")
        sns_plot.set_xticklabels(sns_plot.get_xticklabels(), rotation=30)
        sns_plot.figure.savefig(f"boxplots{i}.png", bbox_inches="tight")
        sns_plot.figure.clf()


if __name__ == "__main__":
    main()
