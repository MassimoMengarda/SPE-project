import pandas as pd
import numpy as np
import argparse

def main(processed_filepath, output_filepath):
    b_base_s = np.linspace(0.0012, 0.024, num=10)
    psi_s = np.linspace(515, 4886, num=15)
    p_0_s = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]

    element_to_elaborate = []
    bbase_to_elab = []
    psi_to_elab = []
    p_0_to_elab = []

    for b_base in b_base_s:
        for psi in psi_s:
            for p_0 in p_0_s:
                bbase_to_elab.append(b_base)
                psi_to_elab.append(psi)
                p_0_to_elab.append(p_0)

    full_list = pd.DataFrame(data={'b_base': bbase_to_elab, 'psi': psi_to_elab, 'p_0': p_0_to_elab})
    processed_list = pd.read_csv(processed_filepath, sep=';')

    fields_list = ['b_base', 'psi', 'p_0']

    mask = full_list[fields_list].isin(processed_list[fields_list].to_dict(orient='list')).all(axis=1)
    
    full_list = full_list[~mask]

    full_list.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("processed_filepath", type=str, help="where to find the processed file")
    parser.add_argument("output_filepath", type=str, help="the directory where store the result")
    args = parser.parse_args()
    processed_filepath = args.processed_filepath
    output_filepath = args.output_filepath
    
    main(processed_filepath, output_filepath)