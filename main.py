from group import PandemicGroup

def main():
    N = 200
    I = 1
    beta = 0.152
    gamma = 0.053
    group = PandemicGroup(N, I, beta, gamma)

    max_t = 100
    PandemicGroup.plot_advancement(group, max_t)

main()