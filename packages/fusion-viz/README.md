# fusion-viz

Visualization for `MultimodalSample` data produced by `fusion-datasets` adapters.
Usable as a library (`fusion_viz.plotting`) or as the `fusion-viz` CLI.

## CLI

```
fusion-viz <dataset-name> <index> [--out path/to/figure.png]
```

`<dataset-name>` must be a dataset registered with `fusion_core.data.base.MultimodalRegistry`
(registration happens as a side effect of importing `fusion_datasets`).

Note: Typer collapses a single-command app to this "no subcommand name" form.
If a second `@app.command()` is ever added to `cli.py`, the subcommand name
(`plot-sample`) becomes required again — update this usage line at that point.

## Library

```python
from fusion_viz.plotting import plot_multimodal_sample

fig = plot_multimodal_sample(sample)
fig.savefig("sample.png")
```
