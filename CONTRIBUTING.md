# Contributing / extending smart-fusion

This repo is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
monorepo: one lockfile (`uv.lock`), several independently-versioned packages
under `packages/`. This doc exists so that "where does this code go?" has a
default answer before you start typing.

## The packages, and what each one owns

| Package           | Owns                                                          | Depends on (internal) |
|--------------------|---------------------------------------------------------------|------------------------|
| `fusion-core`      | Shared abstractions with no I/O: `MultimodalSample`, `MultimodalDataset`, `MultimodalRegistry`, generic utils (`seed_everything`). | — |
| `fusion-datasets`  | Dataset adapters (e.g. Argoverse) that produce `MultimodalSample`s and register themselves with `MultimodalRegistry`. | `fusion-core` |
| `fusion-viz`       | Turns a `MultimodalSample` into a figure; a library (`fusion_viz.plotting`) plus a CLI (`fusion-viz`) that's a thin wrapper over it. | `fusion-core`, `fusion-datasets` |
| `fusion-api`       | Not yet defined — currently a stub. Decide its scope before adding to it (see below). | — |

`fusion-core` never imports from `fusion-datasets`, `fusion-viz`, or
`fusion-api` — dependencies only flow "outward" from core. If you find
yourself wanting `fusion-core` to import a downstream package, that's a sign
the thing you're adding belongs in the downstream package instead (see the
`MultimodalRegistry` pattern below).

## Deciding where new code goes

1. **Is it a generic, I/O-free abstraction other packages will build on** (a
   new base class, a shared utility)? → `fusion-core`.
2. **Does it load/produce `MultimodalSample`s from some external source**
   (a new dataset, a new sensor format)? → a new adapter inside
   `fusion-datasets`, registered via `MultimodalRegistry.register(...)` —
   don't touch `fusion-core` to add it.
3. **Does it consume samples/results to produce human-facing output**
   (a plot, a report, a served API)? → its own package under `packages/`,
   named `fusion-<purpose>`. Use `fusion-viz` as the template (see below).
4. **Is it a one-off, non-reusable script** (a GPU smoke test, a data
   migration you'll run once)? → `scripts/` at the repo root, not a
   package. `scripts/check_setup.py` is the existing example.
5. **Is it a test?** → root-level `tests/`, not a per-package `tests/`
   directory. This repo tests across the shared workspace venv rather than
   per-package; name files `test_<thing being tested>.py` and import from
   whatever installed package owns the code (see
   `tests/test_fusion_viz_plotting.py`).

If none of these fit, that's a sign the boundary is genuinely unclear —
open the discussion rather than guessing at a package name.

## Adding a new package: checklist

Use `packages/fusion-viz` as the worked example.

1. `packages/fusion-<name>/` with:
   - `pyproject.toml` — copy an existing package's, don't start from
     `uv init` defaults. Needs `[build-system]` with `uv_build` (compare
     `fusion-core`'s and `fusion-datasets`'s — `fusion-api` is missing this
     and should not be copied as a template until that's fixed).
   - `src/fusion_<name>/__init__.py`, `src/fusion_<name>/py.typed`.
   - `README.md` describing the package's purpose and, if it has one, its
     CLI usage.
2. Internal dependencies go in `dependencies = [...]` **and** get a
   matching entry in `[tool.uv.sources]` with `{ workspace = true }` — both
   are required, not just one.
3. Add the package directory to `[tool.uv.workspace].members` in the root
   `pyproject.toml`.
4. **Gotcha:** being a workspace member does not mean it gets installed by
   a plain `uv sync`. Only packages the root project (or another installed
   package) actually depends on get pulled into the shared venv — this is
   why `fusion-datasets` isn't installed today even though it's a member.
   To work on / test a package nothing else depends on yet, use
   `uv sync --package fusion-<name>` (or `--all-packages` for everything,
   which is what CI-equivalent local runs should use) or
   `uv run --package fusion-<name> <command>`.
5. If the package should be usable from the shell, add
   `[project.scripts]` with `fusion-<name> = "fusion_<name>.cli:main"` and
   keep `cli.py` to argument parsing + I/O only — put the actual logic in a
   separate module (`plotting.py`, etc.) that's importable and testable
   without going through the CLI.
6. Add at least a smoke test in root `tests/`.

## CLI convention

Each package that needs a CLI exposes its own standalone `[project.scripts]`
entry (`fusion-viz`, and so on) — there's no unified `fusion` dispatcher
command today. This was a deliberate choice to avoid building a plugin
dispatcher for a single command; **revisit it once a second CLI need shows
up.** At that point, either keep them standalone or introduce a
`packages/fusion-cli` package with a Click/Typer group that each package
registers a subcommand into — don't retrofit the first CLI you write today
into that shape speculatively.

One Typer-specific gotcha worth knowing before you add a second
`@app.command()` to any CLI here: a Typer app with exactly one command
collapses to "no subcommand name needed" (`fusion-viz <dataset> <index>`
works; `fusion-viz plot-sample <dataset> <index>` does not). Adding a
second command changes the invocation syntax for the first one too —
update that package's README when it happens.

## Cross-package extensibility: the registry pattern

`fusion-core` defines `MultimodalRegistry` so that downstream packages
(`fusion-datasets`, and consumers like `fusion-viz`) can refer to a dataset
by string name without `fusion-core` ever importing them back. When you add
a new dataset adapter, follow this shape rather than adding an `if/elif` on
dataset name anywhere, and rather than having `fusion-core` know the new
adapter exists:

```python
# packages/fusion-datasets/src/fusion_datasets/my_dataset/adapter.py
from fusion_core.data.base import MultimodalDataset, MultimodalRegistry

@MultimodalRegistry.register("my_dataset")
class MyDataset(MultimodalDataset):
    ...
```

Registration only happens on import, so anything that looks datasets up by
name (like `fusion-viz`'s CLI) must `import fusion_datasets` first — that's
a real import, not decoration, purely for the side effect.

## Naming

- Package directories and PyPI/workspace names: `fusion-<name>`, kebab-case.
- Import/module names: `fusion_<name>`, snake_case (`fusion-viz` →
  `import fusion_viz`).

## Known gaps (don't treat these as settled precedent)

- `fusion-api`'s scope is undecided — empty `README.md`, empty
  `dependencies`, no `[build-system]`. Nail down what it's for before
  extending it or copying its `pyproject.toml` as a template.
- `fusion-datasets` doesn't register any datasets yet, so
  `MultimodalRegistry.available()` is currently empty — `fusion-viz`'s CLI
  is wired up and tested against `plot_multimodal_sample` directly, but
  hasn't been exercised end-to-end against a real dataset yet.
