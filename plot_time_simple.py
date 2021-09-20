import matplotlib.pyplot as plt


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

    fig, ax = plt.subplots()
    width = 0.2

    # ax.bar(list(map(lambda x: x-0.2, range(6))), [sum(i) for i in mmseq_times], width, label='MMseqs2')
    # ax.bar(list(map(lambda x: x, range(6))), [sum(i) for i in iblast_times], width, label='iBLAST')
    # ax.bar(list(map(lambda x: x+0.2, range(6))), [sum(i) for i in nblast_times], width, label='BLAST')

    mm_search_time = [sum(i) for i in mmseq_times[1:]]
    ib_search_time = [sum(i) for i in iblast_times[1:]]
    nb_search_time = [sum(i) for i in nblast_times[1:]]
    diamond_search_time = [sum(i) for i in diamond_times[1:]]
    ax.bar(list(map(lambda x: x - 0.3, range(5))), mm_search_time, width, label="MMseqs2 Search")
    ax.bar(list(map(lambda x: x - 0.1, range(5))), ib_search_time, width, label="iBLAST Search")
    ax.bar(list(map(lambda x: x + 0.1, range(5))), nb_search_time, width, label="BLAST Search")
    ax.bar(list(map(lambda x: x + 0.3, range(5))), diamond_search_time, width, label="Diamond Search")
    search_labels = ["0", "Time 0", "Time 1", "Time 2", "Time 3", "Time 4"]
    ax.set_xticklabels(search_labels)

    ax.set_ylabel("Seconds")
    ax.set_title("Time Per Search")
    ax.legend()
    fig.savefig("barplot_search.png", bbox_inches="tight")
    plt.clf()

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
