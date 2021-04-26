import numpy as np
import torch

def coo_to_tensor_torch(coo):
    indices = np.mat([coo.row, coo.col])
    return torch.sparse_coo_tensor(torch.LongTensor(indices), torch.from_numpy(coo.data), size=coo.shape).coalesce()