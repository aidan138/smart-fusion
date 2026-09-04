"""Entry point for the `fusion-viz` command.

Command parsing and I/O only — plotting logic lives in plotting.py so it
stays usable without going through the CLI.
"""

from __future__ import annotations

from pathlib import Path

import fusion_datasets  # noqa: F401 - import side effect: registers datasets
import typer
from fusion_core.data.base import MultimodalRegistry

from fusion_viz.plotting import plot_multimodal_sample

app = typer.Typer(help="Visualize multimodal dataset samples from the CLI.")


@app.command()
def plot_sample(
    dataset: str = typer.Argument(..., help="Name registered with MultimodalRegistry, e.g. 'argoverse'."),
    index: int = typer.Argument(0, help="Sample index within the dataset."),
    out: Path | None = typer.Option(
        None, "--out", "-o", help="Save the figure here instead of opening a window."
    ),
) -> None:
    """Plot a single sample, one panel per modality."""
    dataset_cls = MultimodalRegistry.get(dataset)
    sample = dataset_cls()[index]
    fig = plot_multimodal_sample(sample)

    if out is not None:
        fig.savefig(out)
        typer.echo(f"Saved to {out}")
    else:
        import matplotlib.pyplot as plt

        plt.show()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
