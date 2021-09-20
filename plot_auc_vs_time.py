import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
from statistics import mean


def main():  # pylint: disable=too-many-locals

    mmseq_times = [
        [2.984, 2.614, 2.64, 2.479, 2.638],
        [105.684],
        [3.116, 1.37, 149.839],
        [3.78, 1.551, 175.839],
        [4.215, 1.631, 198.734],
        [4.987, 1.869, 210.051],
    ]

    iblast_times = [
        [0],
        [0.345, 4701.22],
        [0.134, 9060.45],
        [0.527, 12529.1],
        [22.853, 15421],
        [0.63, 17904.6],
    ]

    nblast_times = [
        [3.392, 5.551, 8.396, 11.33, 13.517],
        [4519.34],
        [7388.92],
        [9812.89],
        [11827.5],
        [14067.3],
    ]

    diamond_times = [
        [0.649, 1.275, 1.779, 2.277, 2.68],
        [30.568],
        [45.474],
        [59.572],
        [72.984],
        [86.667],
    ]

    iblast_auc = 0.44150427519864044
    nblast_auc = 0.578742347163334
    mmseq_auc = 0.4535278237440494
    diamond_auc = 0.15754283933542332

    mm_search_time = sum([sum(i) for i in mmseq_times[1:]])
    ib_search_time = sum([sum(i) for i in iblast_times[1:]])
    nb_search_time = sum([sum(i) for i in nblast_times[1:]])
    diamond_search_time = sum([sum(i) for i in diamond_times[1:]])
    plt.scatter(iblast_auc, ib_search_time, marker="o", label="iBLAST", s=150)
    plt.scatter(nblast_auc, nb_search_time, marker="o", label="BLAST", s=150)
    plt.scatter(mmseq_auc, mm_search_time, marker="o", label="MMseqs2", s=150)
    plt.scatter(diamond_auc, diamond_search_time, marker="o", label="Diamond", s=150)
    plt.ylabel("Seconds")
    plt.xlabel("Mean AUC1 at Time 4")

    # plt.legend(handler_map={ib: HandlerLine2D(numpoints=1)})
    plt.legend()
    plt.savefig("test.png", bbox_inches="tight")

    # fig, ax = plt.subplots()
    # # largest time will be the search, so take it out for all but the first entry
    # mm_init_time = [
    #     sum(mmseq_times[0]),
    # ] + [sum(sorted(i)[:-1]) or 0 for i in mmseq_times[1:]]
    # ib_init_time = [
    #     sum(iblast_times[0]),
    # ] + [sum(sorted(i)[:-1]) or 0 for i in iblast_times[1:]]
    # nb_init_time = [
    #     sum(nblast_times[0]),
    # ] + [sum(sorted(i)[:-1]) or 0 for i in nblast_times[1:]]
    # di_init_time = [
    #     sum(diamond_times[0]),
    # ] + [sum(sorted(i)[:-1]) or 0 for i in diamond_times[1:]]
    # ax.bar(list(map(lambda x: x - 0.3, range(6))), mm_init_time, width, label="MMseqs2 Data Setup")
    # ax.bar(list(map(lambda x: x - 0.1, range(6))), ib_init_time, width, label="iBLAST Data Setup")
    # ax.bar(list(map(lambda x: x + 0.1, range(6))), nb_init_time, width, label="BLAST Data Setup")
    # ax.bar(list(map(lambda x: x + 0.3, range(6))), di_init_time, width, label="Diamond Data Setup")

    # setup_labels = ["0", "Initial Setup", "Search 0", "Search 1", "Search 2", "Search 3", "Search 4"]
    # ax.set_xticklabels(setup_labels)

    # ax.set_ylabel("Seconds")
    # ax.set_title("Time Per Setup")
    # ax.legend()
    # fig.savefig("barplot_init.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
