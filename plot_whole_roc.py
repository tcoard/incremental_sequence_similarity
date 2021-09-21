"""gets the roc1"""
import pickle
import time
import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve, auc

DATA_DIR = "final_data"

with open('sid_cogs.pkl', 'rb') as f:
    sid_cogs = pickle.load(f)

def get_classification(seq_dict, seq_id):
    classifacations = []
    evalues = []
    for match, evalue in seq_dict[seq_id]:
        # if there are no shared cogs
        classifacations.append(int(set(sid_cogs[match]).isdisjoint(sid_cogs[seq_id])))
        evalues.append(float(evalue))
        if len(classifacations) == 20:
            break

    return classifacations, evalues

def get_evalues(i, matches, alg_type):

    # with Pool(18) as pool:
    if alg_type == 'mm':
        in_file_prefix = "mm_matches"
    elif alg_type == 'ib':
        in_file_prefix = "ib_matches"
    elif alg_type == 'nb':
        in_file_prefix = "nb_matches"
    elif alg_type == 'di':
        in_file_prefix = "di_matches"

    with open(f"{DATA_DIR}/{in_file_prefix}{i}.pkl", "rb") as f:
        seq_dict = pickle.load(f)
    classifacations = []
    evalues = []
    for i, match in enumerate(matches):
        # if i == 1000:
        #     break
        if i % 1000 == 0:
            start = time.time()
        classifacation, evalue = get_classification(seq_dict, match)
        if i % 1000 == 0:
            print('a', time.time() - start)
            start = time.time()
        classifacations = classifacations + classifacation
        if i % 1000 == 0:
            print('b', time.time() - start)
        evalues = evalues + evalue
    return classifacations, evalues


def main():  # pylint: disable=too-many-locals

    exact_matches = []
    with open(f"{DATA_DIR}/exact_matches.txt", "r") as f:
        exact_matches = [line.strip() for line in f]

    cog_matches = []
    with open(f"{DATA_DIR}/cog_matches.txt", "r") as f: cog_matches = [line.strip() for line in f]

    no_cog_matches = []
    with open(f"{DATA_DIR}/no_cog_matches.txt", "r") as f:
        no_cog_matches = [line.strip() for line in f]

    for i in range(5):
        for alg_type in ('mm', 'ib', 'nb', 'di'):
            print(i, alg_type)
            exact_class, exact_evalues = get_evalues(i, exact_matches, alg_type)
            cog_class, cog_evalues = get_evalues(i, cog_matches, alg_type)
            classifacations = exact_class + cog_class
            evalues = exact_evalues + cog_evalues

            fpr, tpr, _ = roc_curve(classifacations, evalues)
            roc_auc = auc(fpr, tpr)
            print(roc_auc)
            plt.figure()
            lw = 2
            plt.plot(fpr, tpr, color='darkorange',
                     lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
            plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver operating characteristic example')
            plt.legend(loc="lower right")
            plt.savefig(f"roc_{alg_type}{i}.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
