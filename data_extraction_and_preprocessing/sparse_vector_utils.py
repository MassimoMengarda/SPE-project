import torch

def sparse_dense_vector_mul(s, d):
    i = s.indices()
    v = s.values()
    # get values from relevant entries of dense matrix
    if d.shape[0] != 1:
        dv = d[i[0,:], 0]
    else:
        dv = d[0, i[1,:]]
    return torch.sparse_coo_tensor(i, v * dv, s.size(), device=s.device).coalesce()