import torch

from fusion_core.utils.random import seed_everything

def test_seed_everything_reproduces_torch_values() -> None:
    seed_everything(17)
    first = torch.randn(16)

    seed_everything(17)
    second = torch.randn(16)

    assert(torch.equal(first,second))
