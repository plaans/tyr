# Tyr: Task Planner Comparison Tool

## Overview

**Tyr** is a Python-based tool designed for comparing a set of task planners over a variety of problems using the [unified-planning](https://unified-planning.readthedocs.io) library.
This project aims to provide a understanding analysis of task planners' performance on different problem sets, offering valuable insights into their efficiency and effectiveness.

## Table of Contents

- [Installation](#installation)
    - [Cloning the Repository](#cloning-the-repository)
    - [Installing the Dependencies](#installing-the-dependencies)
- [Configuration](#configuration)
  - [Domains](#domains)
  - [Variants](#variants)
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

A **domain**, e.g., *Rovers*, is made of **variants**, e.g., *hierarchical* and *temporal*.
Each variant contains a set of **problems** and each problem has a set of **versions**.
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

For each variant supported by this domain, a method `build_<variant>_problem_<version>` must be added to that class.
This method takes a problem instance and must returns the unified planning problem associated with this variant and this version.
It can also return `None` if no problem can be created.

For example, to create the *base* version of the *hierarchical* variant, you can do:

```python
# file: src/tyr/problem/rovers.py
from typing import Optional
from unified_planning.shortcuts import Problem as UProblem
from tyr import AbstractDomain, Problem


class RoversDomain(AbstractDomain):
  def build_hierarchical_problem_base(self, pb: Problem) -> Optional[UProblem]:
    return UProblem("base problem to create")
```

A full example can be found in [`tests/integration/problem/domain.py`](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/tests/integration/problem/domain.py).

## Variants

A new variant can be defined by adding a class inheriting from `tyr.AbstractVariant` and with a name finishing by *Variant*.
The class must be defined inside the `tyr.problem` module.
For example, you can create the variant *hierarchical* with:

```python
# file: src/tyr/problem/variants.py
from tyr import AbstractVariant

class HierarchicalVariant(AbstractVariant):
  pass
```

There is nothing more to do.
The variant is defined by a class in order to be able to add features in the future, as getters defining characteristics of the variant in order for the planners to know if they can support it.

# License

This project is privately licensed.
All rights reserved.
See [LICENSE.md](https://gitlab.laas.fr/rgodet1/tyr/-/blob/master/LICENSE.md) for more details.

# Contact

For inquiries or support, please contact [Roland Godet](mailto:rgodet@raida.fr).
