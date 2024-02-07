# Tyr: Task Planner Comparison Tool

[![pipeline](https://gitlab.laas.fr/rgodet1/tyr/badges/master/pipeline.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/pipelines)
[![coverage](https://gitlab.laas.fr/rgodet1/tyr/badges/master/coverage.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/graphs/master/charts)
[![Latest Release](https://gitlab.laas.fr/rgodet1/tyr/-/badges/release.svg)](https://gitlab.laas.fr/rgodet1/tyr/-/releases)
[![GitLab License](https://img.shields.io/gitlab/license/rgodet1%2Ftyr?gitlab_url=https%3A%2F%2Fgitlab.laas.fr%2F&label=License)](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/LICENSE.md)


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
- [Usage](#usage)
- [Configuration](#configuration)
  - [Domains](#domains)
  - [Planners](#planners)
- [Available Tools](#available-tools)
  - [Domains](#domains-1)
  - [Planners](#planners-1)
- [License](#license)
- [Contact](#contact)

# Installation

### Cloning the Repository

To clone this repository, use the following command:

```bash
git clone --recurse-submodules https://gitlab.laas.fr/rgodet1/tyr
```

### Installing the Dependencies

To install dependencies using [Justfile](https://github.com/casey/just), use the following command, this will create a virtual environment in `.venv`:

```bash
just install
```

To install dependencies without Justfile, use the following commands (think to create a virtual environment if you want to):

```bash
cargo build --release --bin up-server --manifest-path libs/aries/Cargo.toml
cp libs/aries/target/release/up-server libs/aries/planning/unified/plugin/up_aries/bin/up-aries_linux_amd64
pip install -r requirements/prod.txt
```

To install development dependencies, replace `prod` by `dev`.
You can also run `just install dev`.

# Usage

To get the help of the tyr module, run:

```bash
python -m tyr --help
```

The help should be sufficiently documented to guide you.

# Configuration

## Domains

A **domain** contains a set of **problems** and each problem has a set of **versions**.
The different versions are used to make a same problem compatible for different planners.

To add a new domain to the analysis process, create a class inheriting from `tyr.AbstractDomain` and with a name finishing by *Domain*.
The class must be defined inside the `tyr.problems` module and must override the `get_num_problems` method returning the number of instances.
For example, you can create the domain *Rovers* with:

```python
# file: src/tyr/problems/rovers.py
from tyr import AbstractDomain

class RoversDomain(AbstractDomain):
  def get_num_problems(self) -> int:
    """Returns the number of instances in the domain."""
    return 10
```

For each version of the domain, a method `build_problem_<version>` must be added to that class.
This method takes a problem instance and must returns the unified planning problem associated with this version.
It can also return `None` if no problem can be created.

For example, to create the *base* version of the domain, you can do:

```python
# file: src/tyr/problems/rovers.py
from typing import Optional
from unified_planning.shortcuts import Problem as UProblem
from tyr import AbstractDomain, Problem


class RoversDomain(AbstractDomain):
  def get_num_problems(self) -> int:
    return 10

  def build_problem_base(self, pb: Problem) -> Optional[UProblem]:
    """Builds the instance for the given problem."""
    return UProblem("base problem to create")
```

A full example can be found in [`tests/integration/problems/domains.py`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/tests/integration/problems/domains.py).

## Planners

The planners are configured in [`src/tyr/configuration/planners.yaml`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/src/tyr/configuration/planners.yaml).

Each entry contains:

- the name of the planner used by the unified-planning factory
- the version to use for each supported domain
- an optional list of environment variables

It is possible to add a planner which is not supported by the unified-planning library.
To do so, create a class inheriting from `tyr.TyrPDDLPlanner` and with a name finishing by *Planner*.
The class must be defined inside the `tyr.planners` module.
The created planner will be automatically registered in the unified-planning factory.

A full example can be found in [`src/tyr/planners/optic/__init__.py`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/src/tyr/planners/optic/__init__.py) to add the **Optic** planner.

# Available Tools

## Domains

The following table lists the versions of the domains already present in the repo.

|               | Scheduling | Hierarchical | Hierarchical Numeric | Hierarchical Temporal Numeric             | Numeric      | Temporal Numeric                          |
| ------------- | ---------- | ------------ | -------------------- | ----------------------------------------- | ------------ | ----------------------------------------- |
| **Depots**    |            | `base`       | `base`, `red`        | `base`, `red`,`no_div`,`red_no_div`       | `base`,`red` | `base`, `red`, `no_div`, `red_no_div`     |
| **Jobshop**   | `base`     |              |                      |                                           |              | `base`, `no_neg_cond`                     |
| **RCPSP**     | `base`     |              |                      |                                           |              | `base`, `no_neg_cond`                     |
| **Rovers**    |            | `base`       | `base`, `red`        | `base`, `red`, `no_div`, `red_no_div`     | `base`,`red` | `base`, `red`, `no_div`, `red_no_div`     |
| **Satellite** |            | `base`       | `base`, `red`        | `base`, `red`, `no_float`, `red_no_float` | `base`,`red` | `base`, `red`, `no_float`, `red_no_float` |

## Planners

List of the planners already present in the repo.
Please take a look at [`src/tyr/configuration/planners.yaml`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/src/tyr/configuration/planners.yaml) for the supported domains.

- Aries
- LPG
- Optic

# License

This project licensed under MIT license.
See [LICENSE.md](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/LICENSE.md) for more details.

# Contact

For inquiries or support, please contact [Roland Godet](mailto:rgodet@raida.fr).
