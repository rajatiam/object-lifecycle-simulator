# Object Lifecycle Simulator

Deterministic retention plans with legal holds and policy precedence. An independent Python 3.11+ project using the standard library, with a real command-line interface and no runtime package dependencies.

## Run locally

From the cloned repository, run:

```sh
python -m object_lifecycle_simulator plan examples/objects.json examples/policies.json --as-of 2026-10-03
python -m object_lifecycle_simulator plan examples/objects.json examples/policies.json --as-of 2026-10-03 --output examples/plan.json
python -m object_lifecycle_simulator --help
```

Examples contain synthetic data. First use requires no cloud account, API key or package download. Optionally install the CLI using `python -m pip install .` and run `object-lifecycle-simulator --help`.

## Verify

```sh
python -m unittest discover -v
```

GitHub Actions checks Python 3.11 and 3.13 on Linux and Windows, verifies package installation, and builds/runs the non-root Docker image.

```sh
docker build -t object-lifecycle-simulator .
docker run --rm object-lifecycle-simulator --help
```

Mount a working directory at `/workspace` to process your own files. The container runs as UID 10001; provide appropriate write permissions for outputs.

## Architecture and scope

Business algorithms live in `object_lifecycle_simulator/core.py`; `object_lifecycle_simulator/cli.py` owns argument parsing and JSON output. Tests exercise success cases and failure boundaries, with temporary storage for mutations. See [design decisions](docs/architecture.md).

Plans only: it never deletes objects or connects to a cloud account. Legal holds and future retain-until dates block deletion. Longest matching prefix determines policy; ambiguous duplicate prefixes are rejected.

This project demonstrates implemented engineering practices. It does not claim production deployment history or external certifications.
