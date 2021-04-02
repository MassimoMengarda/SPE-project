from simulation import Model

def main(info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir):
    poi_index = read_csv(os.path.join(info_dir, "poi_indexes.csv"))
    cases = read_csv(cases_filepath)
    n_pois = len(poi_index.index)
    cbgs_population = read_npy(os.path.join(info_dir, "cbg_population_matrix.npy"))
    pois_area = read_npy(os.path.join(info_dir, "poi_area.npy"))
    weeks = ["2019-01-07"] # TODO better implementation
    
    b_base_s = np.linspace(0.0012, 0.024, num=10)
    psi_s = np.linspace(515, 4886, num=15)
    p_0_s = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]

    best_params = (b_base_s[0], psi_s[0], p_0_s[0])

    for b_base in b_base_s:
        for psi in psi_s:
            for p_0 in p_0_s:
                for i in range(10):
                    output_dir = os.path.join(output_dir, str(b_base), str(psi), str(p_0))
                    m = Model(cbgs_population, ipfp_dir, dwell_dir, output_dir, n_pois, pois_area, weeks, b_base, psi, p_0, t_e=96, t_i=84)
                    m.simulate()
                    
                    # if True: # TODO check if those params are best
                    #     best_params = (b_base, psi, p_0)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("ipfp_directory", type=str, help="the directory where the ipfp matrixes are stored")
    parser.add_argument("info_directory", type=str, help="the directory where the matrixes index are stored")
    parser.add_argument("dwell_directory", type=str, help="the directory where the dwell matrixes are stored")
    parser.add_argument("cases_filepath", type=str, help="the filepath where the number of cases are stored")
    parser.add_argument("output_directory", type=str, help="the directory where store the result")
    args = parser.parse_args()
    ipfp_dir = args.ipfp_directory
    info_dir = args.info_directory
    dwell_dir = args.dwell_directory
    cases_filepath = args.cases_filepath
    output_dir = args.output_directory
    
    main(info_dir, ipfp_dir, dwell_dir, cases_filepath, output_dir)
