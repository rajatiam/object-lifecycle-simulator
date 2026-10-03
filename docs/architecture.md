# Object Lifecycle Simulator: architecture

## Explicit clock and retention precedence

An explicit as-of date makes plans reproducible. Longest matching prefix selects a policy. Expiration takes priority over transition; legal holds and future retain-until dates block expiration. Output is sorted by object key.

## Module boundaries

`object_lifecycle_simulator/core.py` contains the algorithm and persistence operations. `cli.py` validates arguments and prints JSON. The package entrypoint translates input and storage errors into structured stderr with exit status 2. Domain-specific unsuccessful results can use exit status 1. There is no shared runtime dependency on the portfolio folder.

## Failure and operational boundaries

The simulator validates dates, storage classes, policy thresholds and duplicate identities. It performs no cloud calls and no deletions. It models creation age only; object versions, delete markers and provider-specific lifecycle semantics are outside its contract. Output must differ from input files.

## Verification

Core tests cover valid results and failure boundaries. Process-level CLI tests run the committed examples in temporary copies, inspect JSON output and verify domain outcomes. CI runs on Python 3.11 and 3.13, Linux and Windows, checks package installation, and builds and executes the non-root Docker image.

## Extension choices

The standard-library implementation keeps local execution inspectable and offline. A hosted or distributed version would require workload-specific authorization, resource limits, durable coordination and observability. Extend the core through tested functions rather than adding infrastructure without a scaling requirement.
