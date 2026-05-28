# i-fetch-rocks-sim

`i-fetch-rocks-sim` is a Python package for loading and inspecting **I Fetch Rocks** save files.

This repository is intended to host the reusable, game-save-oriented simulator and analysis API.

## Goals

- Load save files into structured Python models.
- Expose stable APIs for listing rooms, devices, and wires.
- Support optional simulation and diff utilities.
- Stay reusable for external apps and tooling.

## Local development

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -e .[dev]
.venv\Scripts\pytest
```

## Early API sketch

```python
from ifetchrocks_sim import SaveReader

reader = SaveReader()
save = reader.load_path("path/to/save.json")
print(save.device_count)
```

## Status

Scaffold only. Core logic migration from your existing project is the next step.
