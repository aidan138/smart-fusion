"""Plotting logic, kept free of CLI concerns.

Import and call these directly from notebooks/scripts/tests; cli.py is
just one more caller of this module, not a special one.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from fusion_core.data.base import MultimodalSample


def plot_multimodal_sample(sample: MultimodalSample) -> Figure:
    """One subplot per modality: an image for 2D/3D tensors, a line for 1D."""
    names = sorted(sample.modalities)
    fig, axes = plt.subplots(1, len(names), figsize=(4 * len(names), 4), squeeze=False)

    for ax, name in zip(axes[0], names):
        tensor = sample.modalities[name].detach().cpu()
        ax.set_title(name)

        # Collapse any leading (e.g. time/frame) dims down to a single CHW/HW image.
        while tensor.ndim > 3:
            tensor = tensor[0]

        if tensor.ndim == 3:
            # torch convention is channel-first; imshow wants channel-last.
            ax.imshow(tensor.permute(1, 2, 0).squeeze(-1).numpy(), cmap="viridis")
        elif tensor.ndim == 2:
            ax.imshow(tensor.numpy(), cmap="viridis")
        else:
            ax.plot(tensor.numpy())

    fig.suptitle(str(sample.meta.get("id", "")))
    fig.tight_layout()
    return fig
