import os
import random

import numpy as np 
import torch


def seed_everything(seed: int, deterministic: bool = False) -> np.random.Generator:

    if seed < 0:
        raise ValueError("seed must be non-negative")

    # only useful in for child processes launced afterwords who inherit the environment
    os.environ["PYTHONHASHSEED"] = str(seed) 

    random.seed(seed)
    np.random.seed(seed) # for legacy numpy 
    rng = np.random.default_rng(seed) # numpy's new recommended form for rng
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        # for multi-GPU support use *seed_all
        torch.cuda.manual_seed_all(seed)

    # cuDNN is GPU library that does operations like convs
    # depending on the shape it may choose a faster algo
    # this is great for benchmarking but poor foor determinism
    torch.backends.cudnn.benchmark = not deterministic
    torch.backends.cudnn.deterministic = deterministic

    if deterministic:
        # say as cuDNN and it raises a warning instead of an exception when not possible
        torch.use_deterministic_algorithms(True, warn_only=True)
    
    return rng
