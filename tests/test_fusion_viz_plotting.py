import matplotlib

matplotlib.use("Agg")

import torch
from matplotlib.figure import Figure

from fusion_core.data.base import MultimodalSample
from fusion_viz.plotting import plot_multimodal_sample


def test_plot_multimodal_sample_returns_figure_with_one_axis_per_modality() -> None:
    sample = MultimodalSample(
        modalities={
            "audio": torch.randn(16),
            "video": torch.randn(3, 8, 8),
        },
        label=torch.tensor(0),
    )

    fig = plot_multimodal_sample(sample)

    assert isinstance(fig, Figure)
    assert len(fig.axes) == len(sample.modalities)
