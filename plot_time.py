import matplotlib.pyplot as plt


def main():  # pylint: disable=too-many-locals

    mmseq_times = [
        [2.641, 2.530, 2.534, 2.623, 2.539],  # init db
        [
            106.082,
        ],  # search 0
        [0.791, 0.224, 151.270],  # search 1
        [1.213, 0.305, 179.712],
        [1.440, 0.389, 197.819],
        [1.699, 0.461, 218.812],
    ]

    iblast_times = [
        [0.496, 3.379, 2.943, 3.000, 2.887, 2.842],  # init
        [0.344, 5003.846],
        [0.140, 9259.190],
        [90.600, 12995.052],
        [90.571, 16129.708],
        [0.619, 18271.101],
    ]

    nblast_times = [
        [2.939, 5.767, 8.162, 10.780, 14.260],
        [
            4752.489,
        ],
        [
            7507.431,
        ],
        [
            10073.744,
        ],
        [
            12140.823,
        ],
        [
            14421.235,
        ],
    ]

    diamond_times = [[2.085, 1.514, 3.120, 3.626, 4.618], [8.015], [11.272], [15.453], [18.254], [20.942]]

    fig, ax = plt.subplots()
    width = 0.2

    # ax.bar(list(map(lambda x: x-0.2, range(6))), [sum(i) for i in mmseq_times], width, label='MMseqs2')
    # ax.bar(list(map(lambda x: x, range(6))), [sum(i) for i in iblast_times], width, label='iBLAST')
    # ax.bar(list(map(lambda x: x+0.2, range(6))), [sum(i) for i in nblast_times], width, label='BLAST')

    mm_search_time = [max(i) for i in mmseq_times[1:]]
    ib_search_time = [max(i) for i in iblast_times[1:]]
    nb_search_time = [max(i) for i in nblast_times[1:]]
    diamond_search_time = [max(i) for i in diamond_times[1:]]
    ax.bar(list(map(lambda x: x - 0.3, range(5))), mm_search_time, width, label="MMseqs2 Search")
    ax.bar(list(map(lambda x: x - 0.1, range(5))), ib_search_time, width, label="iBLAST Search")
    ax.bar(list(map(lambda x: x + 0.1, range(5))), nb_search_time, width, label="BLAST Search")
    ax.bar(list(map(lambda x: x + 0.3, range(5))), diamond_search_time, width, label="Diamond Search")
    search_labels = ["0", "Search 0", "Search 1", "Search 2", "Search 3", "Search 4"]
    ax.set_xticklabels(search_labels)

    ax.set_ylabel("Seconds")
    ax.set_title("Time Per Search")
    ax.legend()
    fig.savefig("barplot_search.png", bbox_inches="tight")
    plt.clf()

    fig, ax = plt.subplots()
    # largest time will be the search, so take it out for all but the first entry
    mm_init_time = [
        sum(mmseq_times[0]),
    ] + [sum(sorted(i)[:-1]) or 0 for i in mmseq_times[1:]]
    ib_init_time = [
        sum(iblast_times[0]),
    ] + [sum(sorted(i)[:-1]) or 0 for i in iblast_times[1:]]
    nb_init_time = [
        sum(nblast_times[0]),
    ] + [sum(sorted(i)[:-1]) or 0 for i in nblast_times[1:]]
    di_init_time = [
        sum(diamond_times[0]),
    ] + [sum(sorted(i)[:-1]) or 0 for i in diamond_times[1:]]
    ax.bar(list(map(lambda x: x - 0.3, range(6))), mm_init_time, width, label="MMseqs2 Data Setup")
    ax.bar(list(map(lambda x: x - 0.1, range(6))), ib_init_time, width, label="iBLAST Data Setup")
    ax.bar(list(map(lambda x: x + 0.1, range(6))), nb_init_time, width, label="BLAST Data Setup")
    ax.bar(list(map(lambda x: x + 0.3, range(6))), di_init_time, width, label="Diamond Data Setup")

    setup_labels = ["0", "Initial Setup", "Search 0", "Search 1", "Search 2", "Search 3", "Search 4"]
    ax.set_xticklabels(setup_labels)

    ax.set_ylabel("Seconds")
    ax.set_title("Time Per Setup")
    ax.legend()
    fig.savefig("barplot_init.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
