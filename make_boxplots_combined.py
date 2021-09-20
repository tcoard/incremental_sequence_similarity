from itertools import product
import pandas as pd
import seaborn as sns

DATA_DIR = "final_data"


def get_data(df, i):
    algos = [("iBLAST", "iblast"), ("BLAST", "nblast"), ("MMseqs2", "mmseq"), ("Diamond", "diamond")]
    seq_types = ["exact", "cog"]
    permuts = product(algos, seq_types)

    for (calgo, algo), seq_type in permuts:
        file_name = algo + "_auc_" + seq_type + str(i) + ".txt"
        with open(f"{DATA_DIR}/{file_name}", "r") as f:
            aucs = [float(line) for line in f if not line.startswith("(")]
            df = df.append(pd.DataFrame({"Program": calgo, "AUC1": aucs, "Time": i}))

    for algo in algos:
        print(algo, df[df["Program"] == algo]["AUC1"].mean())
    return df


def main():
    df = pd.DataFrame(columns=["Program", "AUC1", "Time"])
    for i in range(5):
        df = get_data(df, i)

    g = sns.FacetGrid(df, col="Time")
    g.map(sns.boxplot, "Program", "AUC1")

    # sns_plot = sns.boxplot(x="Program", y="AUC1", data=df)
    # sns_plot.set_title("AUC1 for Each Algorithm")
    # # sns_plot.set_xticklabels(sns_plot.get_xticklabels(), rotation=30)
    # sns_plot.set_xticklabels(["iBLAST", "BLAST", "MMseqs2", "Diamond"])
    g.savefig(f"boxplots_test.png", bbox_inches="tight")
    # sns_plot.clf()


if __name__ == "__main__":
    main()
