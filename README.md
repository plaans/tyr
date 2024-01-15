# Tyr: Task Planner Comparison Tool

[![pipeline](https://gitlab.laas.fr/rgodet1/tyr/badges/master/pipeline.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/pipelines)
[![coverage](https://gitlab.laas.fr/rgodet1/tyr/badges/master/coverage.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/graphs/master/charts)
[![Latest Release](https://gitlab.laas.fr/rgodet1/tyr/-/badges/release.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/releases)

[![python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?logo=python)](https://www.python.org/)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![type checker: mypy](https://img.shields.io/badge/%20type_checker-mypy-%231674b1)](https://github.com/python/mypy)
[![semantic-release: conventionalcommits](https://img.shields.io/badge/semantic--release-conventionalcommits-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)


## Overview

**Tyr** is a Python-based tool designed for comparing a set of task planners over a variety of problems using the [unified-planning](https://unified-planning.readthedocs.io) library.
This project aims to provide a understanding analysis of task planners' performance on different problem sets, offering valuable insights into their efficiency and effectiveness.

## Table of Contents

- [Installation](#installation)
    - [Cloning the Repository](#cloning-the-repository)
    - [Installing the Dependencies](#installing-the-dependencies)
- [Configuration](#configuration)
  - [Domains](#domains)
- [Available Tools](#available-tools)
  - [Domains](#domains-1)
- [License](#license)
- [Contact](#contact)

# Installation

### Cloning the Repository

To clone this repository, use the following command:

```bash
git clone https://gitlab.laas.fr/rgodet1/tyr
```

### Installing the Dependencies

To install dependencies using [Justfile](https://github.com/casey/just), use the following command, this will create a virtual environment in `.venv`:

```bash
just install
```

To install dependencies without Justfile, use the following commands:

```bash
pip install -e .
pip install -r requirements/prod.txt
```

To install development dependencies, replace `prod` by `dev`.
You can also run `just install dev`.

# Configuration

## Domains

A **domain** contains a set of **problems** and each problem has a set of **versions**.
The different versions are used to make a same problem compatible for different planners.

To add a new domain to the analysis process, create a class inheriting from `tyr.AbstractDomain` and with a name finishing by *Domain*.
The class must be defined inside the `tyr.problem` module.
For example, you can create the domain *Rovers* with:

```python
# file: src/tyr/problem/rovers.py
from tyr import AbstractDomain

class RoversDomain(AbstractDomain):
  pass
```

For each version of the domain, a method `build_problem_<version>` must be added to that class.
This method takes a problem instance and must returns the unified planning problem associated with this version.
It can also return `None` if no problem can be created.

For example, to create the *base* version of the domain, you can do:

```python
# file: src/tyr/problem/rovers.py
from typing import Optional
from unified_planning.shortcuts import Problem as UProblem
from tyr import AbstractDomain, Problem


class RoversDomain(AbstractDomain):
  def build_problem_base(self, pb: Problem) -> Optional[UProblem]:
    return UProblem("base problem to create")
```

A full example can be found in [`tests/integration/problem/domain.py`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/tests/integration/problem/domain.py).

# Available Tools

## Domains

The following table lists the versions of the domains already present in the repo.

|            | Hierarchical | Hierarchical Numeric | Hierarchical Temporal Numeric | Numeric | Temporal Numeric  |
| ---------- | ------------ | -------------------- | ----------------------------- | ------- | ----------------- |
| **Depots** | `base`       | `base`               | `base`, `no_div`              | `base`  | `base`, `no_div ` |

# License

This project is privately licensed.
All rights reserved.
See [LICENSE.md](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/LICENSE.md) for more details.

# Contact

For inquiries or support, please contact [Roland Godet](mailto:rgodet@raida.fr).
