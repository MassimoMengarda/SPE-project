from group import PandemicGroup

def main():
    N = 200
    I = 1

    # Data taken from the follwing sources:
    # https://www.ceps.eu/wp-content/uploads/2020/03/Monitoring_Covid_19_contagion_growth_in_Europe.pdf
    # https://www.ncbi.nlm.nih.gov/research/coronavirus/publication/33491299
    beta = 0.152
    gamma = 0.053
    group = PandemicGroup(N, I, beta, gamma)

    max_t = 100
    PandemicGroup.plot_advancement(group, max_t)

if __name__ == "__main__":
    main()