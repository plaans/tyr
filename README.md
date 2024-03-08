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
    - [Installing the Module](#installing-the-module)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Configuration](#configuration)
  - [Domains](#domains)
  - [Planners](#planners)
- [License](#license)
- [Contact](#contact)

# Installation

### Cloning the Repository

To clone this repository, use the following command:

```bash
git clone --recurse-submodules https://gitlab.laas.fr/rgodet1/tyr
```

### Installing the Dependencies

Before running the installation script you need to install some dependencies:

```bash
# Python 3.8+
sudo apt install python3 python3-venv
# Curl, needed to install cargo
sudo apt install curl
# Cargo
curl https://sh.rustup.rs -sSf | sh
```

If you want to use the PandaPi planner, you also have to [install Singularity](https://docs.sylabs.io/guides/latest/admin-guide/installation.html).

### Installing the Module

Once the dependencies are installed, just run the install script:

```bash
./install.sh
```

# Usage

To get the help of the tyr module, run:

```bash
python -m tyr --help
```

The help should be sufficiently documented to guide you.

# Available Tools

The following table lists the domains (with the number of instances) and planners available, as well as the version used by the planners to solve the domain.

|                                      |     **Aries**     |    **LPG**     |   **Optic**    |    **PandaPi**    |
| ------------------------------------ | :---------------: | :------------: | :------------: | :---------------: |
| **Depots**                           |                   |                |                |                   |
| *Hierarchical (30)*                  |      `base`       |       ❌       |       ❌       |      `base`       |
| *Hierarchical Numeric (22)*          |       `red`       |       ❌       |       ❌       |        ❌         |
| *Hierarchical Temporal Numeric (22)* |   `red_no_div`    |       ❌       |       ❌       |        ❌         |
| *Numeric (22)*                       |       `red`       |     `red`      |     `red`      |        ❌         |
| *Temporal Numeric (22)*              |   `red_no_div`    |  `red_no_div`  |  `red_no_div`  |        ❌         |
| **Rovers**                           |                   |                |                |                   |
| *Hierarchical (20)*                  |      `base`       |       ❌       |       ❌       |      `base`       |
| *Hierarchical Numeric (20)*          |       `red`       |       ❌       |       ❌       |        ❌         |
| *Hierarchical Temporal Numeric (20)* |   `red_no_div`    |       ❌       |       ❌       |        ❌         |
| *Numeric (20)*                       |       `red`       |     `red`      |     `red`      |        ❌         |
| *Temporal Numeric (20)*              |   `red_no_div`    |  `red_no_div`  |  `red_no_div`  |        ❌         |
| **Satellite**                        |                   |                |                |                   |
| *Hierarchical (22)*                  |      `base`       |       ❌       |       ❌       |      `base`       |
| *Hierarchical Numeric (16)*          |       `red`       |       ❌       |       ❌       |        ❌         |
| *Hierarchical Temporal Numeric (16)* |  `red_no_float`   |       ❌       |       ❌       |        ❌         |
| *Numeric (16)*                       |       `red`       |     `red`      |     `red`      |        ❌         |
| *Temporal Numeric (16)*              |  `red_no_float`   | `red_no_float` | `red_no_float` |        ❌         |
| **JobShop**                          |                   |                |                |                   |
| *Sheduling (40)*                     |      `base`       |       ❌       |       ❌       |        ❌         |
| *Temporal Numeric (40)*              |      `base`       |     `base`     | `no_neg_cond`  |        ❌         |
| **RCPSP**                            |                   |                |                |                   |
| *Sheduling (30)*                     |      `base`       |       ❌       |       ❌       |        ❌         |
| *Temporal Numeric (30)*              |      `base`       |     `base`     | `no_neg_cond`  |        ❌         |
| **Simple Goto**                      |                   |                |                |                   |
| *Hierarchical(10)*                   | `base` & `linear` |       ❌       |       ❌       | `base` & `linear` |

# Configuration

## Domains

A **domain** contains a set of **problems** and each problem has a set of **versions**.
The different versions are used to make a same problem compatible for different planners.

To add a new domain to the analysis process, create a class inheriting from `tyr.AbstractDomain` and with a name finishing by *Domain*.
The class must be defined inside the `tyr.problems.domains` module and must override the `get_num_problems` method returning the number of instances.
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
The class must be defined inside the `tyr.planners.planners` module.
The created planner will be automatically registered in the unified-planning factory.

A full example can be found in [`src/tyr/planners/optic/__init__.py`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/src/tyr/planners/optic/__init__.py) to add the **Optic** planner.

# License

This project licensed under MIT license.
See [LICENSE.md](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/LICENSE.md) for more details.

# Contact

For inquiries or support, please contact [Roland Godet](mailto:rgodet@raida.fr).
