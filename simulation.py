import numpy as np

t = 0
time_limit = 24 * 7

# TODO: init this data with real data
cbg_s = np.asarray([100, 100, 100]) 
cbg_e = np.asarray([3, 0, 0])
cbg_i = np.asarray([0, 0, 0])
cbg_r = np.asarray([0, 0, 0])

# TODO: finish this crappy code
while t < time_limit:
    delta_ci = get_delta_ci(b_base, cbg_i, cbg_n)
    delta_pj = get_delta_pj(cbg_i, cbj_n, d_pj, a_pj, w_ij)

    cbg_new_e = get_new_e(cbg_s, cbg_i, cbg_n, delta_pj, delta_ci, w_ij, psi)
    cbg_new_i = get_new_i(cbg_e, delta_e)
    cbg_new_r = get_new_r(cbg_i, delta_i)


def get_delta_ci(b_base, cbg_i, cbg_n):
    return b_base * (cbg_i / cbg_n)

def get_delta_pj(cbg_i, cbj_n, d_pj, a_pj, w_ij):
    return (np.square(d_pj) / a_pj) * np.sum(cbg_i / cbj_n * w_ij, axis=0)

def get_new_e(cbg_s, cbg_i, cbg_n, delta_pj, delta_ci, w_ij, psi):
    pois = np.random.poisson(psi * (cbg_s / cbg_n) * np.sum(delta_pj * w_ij))
    binom = np.random.binomial(cbg_s, delta_ci)

    return pois + binom

def get_new_i(cbg_e, delta_e):
    return np.random.binomial(cbg_e, 1 / delta_e)

def get_new_r(cbg_i, delta_i):
    return np.random.binomial(cbg_i, 1 / delta_i)


#################################################
#################################################
#################################################

# if experiment_to_run == 'normal_grid_search':
#     p_sicks = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]
#     home_betas = np.linspace(BETA_AND_PSI_PLAUSIBLE_RANGE['min_home_beta'],
#         BETA_AND_PSI_PLAUSIBLE_RANGE['max_home_beta'], 10)
#     poi_psis = np.linspace(BETA_AND_PSI_PLAUSIBLE_RANGE['min_poi_psi'], BETA_AND_PSI_PLAUSIBLE_RANGE['max_poi_psi'], 15)
#     for home_beta in home_betas:
#         for poi_psi in poi_psis:
#             for p_sick in p_sicks:
#                 configs_with_changing_params.append({'home_beta':home_beta, 'poi_psi':poi_psi, 'p_sick_at_t0':p_sick})

#     # ablation analyses.
#     for home_beta in np.linspace(0.005, 0.04, 20):
#         for p_sick in p_sicks:
#             configs_with_changing_params.append({'home_beta':home_beta, 'poi_psi':0, 'p_sick_at_t0':p_sick})

# elif experiment_to_run == 'grid_search_aggregate_mobility':
#     p_sicks = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]
#     beta_and_psi_plausible_range_for_aggregate_mobility = {"min_home_beta": 0.0011982272027079982,
#                                     "max_home_beta": 0.023964544054159966,
#                                     "max_poi_psi": 0.25,
#                                     "min_poi_psi": 2.5}
#     home_betas = np.linspace(beta_and_psi_plausible_range_for_aggregate_mobility['min_home_beta'],
#                              beta_and_psi_plausible_range_for_aggregate_mobility['max_home_beta'], 10)
#     poi_psis = np.linspace(beta_and_psi_plausible_range_for_aggregate_mobility['min_poi_psi'],
#                            beta_and_psi_plausible_range_for_aggregate_mobility['max_poi_psi'], 15)
#     for home_beta in home_betas:
#         for poi_psi in poi_psis:
#             for p_sick in p_sicks:
#                 configs_with_changing_params.append({'home_beta':home_beta, 'poi_psi':poi_psi, 'p_sick_at_t0':p_sick})

# elif experiment_to_run == 'grid_search_home_proportion_beta':
#     p_sicks = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]
#     home_betas = np.linspace(BETA_AND_PSI_PLAUSIBLE_RANGE['min_home_beta'],
#         BETA_AND_PSI_PLAUSIBLE_RANGE['max_home_beta'], 10)
#     poi_psis = np.linspace(BETA_AND_PSI_PLAUSIBLE_RANGE['min_poi_psi'], BETA_AND_PSI_PLAUSIBLE_RANGE['max_poi_psi'], 15)
#     for home_beta in home_betas:
#         for poi_psi in poi_psis:
#             for p_sick in p_sicks:
#                 configs_with_changing_params.append({'home_beta':home_beta, 'poi_psi':poi_psi, 'p_sick_at_t0':p_sick})