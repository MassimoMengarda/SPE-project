import pandas as pd
import numpy as np
import argparse

# np.set_printoptions(threshold=np.inf)

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
    
    b_base_s_2 = np.linspace(0.0012, 0.024, num=10)

    full_list = pd.DataFrame(data={'b_base': bbase_to_elab, 'psi': psi_to_elab, 'p_0': p_0_to_elab})
    if processed_filepath is not None:
        processed_list = pd.read_csv(processed_filepath, sep=';')

        fields_list = ['b_base', 'psi', 'p_0']

        mask = []
        for field in fields_list:
            to_process_np = processed_list[field].to_numpy()
            to_process_reshaped = np.reshape(to_process_np, (1, to_process_np.shape[0]))
            full_list_to_process_np = full_list[field].to_numpy()
            mask.append(np.isclose(np.reshape(full_list_to_process_np, (full_list_to_process_np.shape[0], 1)), to_process_reshaped))
            # field_mask = np.isclose(np.reshape(full_list_to_process_np, (full_list_to_process_np.shape[0], 1)), to_process_reshaped, rtol=1e-10, atol=1e-30).any(1)
            # print(field_mask)
            # mask.append(field_mask)
        # print(.any(1).shape)
        # print(mask)
        mask = np.asarray(mask)
        mask = mask.all(axis=0)
        duplicate_elements_mask = np.sum(mask, axis=1) > 1
        print("Duplicate elements: ", np.count_nonzero(duplicate_elements_mask))
        print("Duplicate element list:")
        duplicate_elements_coords = np.where(duplicate_elements_mask)
        print(duplicate_elements_coords)
        for duplicate_elements_coord in duplicate_elements_coords[0]:
            print("- b_base: {} psi: {}, p_0: {}".format(bbase_to_elab[duplicate_elements_coord], psi_to_elab[duplicate_elements_coord], p_0_to_elab[duplicate_elements_coord]))

        mask = mask.any(1)
        print(mask)
        print("Element already elaborated: ", np.count_nonzero(mask))
        
        full_list = full_list[~mask]
        print(len(full_list))
    
    full_list.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the simulation")
    parser.add_argument("--processed_filepath", type=str, help="where to find the processed file")
    parser.add_argument("output_filepath", type=str, help="the directory where store the result")
    args = parser.parse_args()
    processed_filepath = args.processed_filepath
    output_filepath = args.output_filepath
    
    main(processed_filepath, output_filepath)