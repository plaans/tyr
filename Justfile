# Use with https://github.com/casey/just

@_default:
    just --list --unsorted
    just _default-args


# ============================================================================ #
#                                   Arguments                                  #
# ============================================================================ #


PY_V := "3.$(python3 -V | cut -d\" \" -f2 | cut -d\".\" -f2)"
PY_T := "prod"
PY_D := ".venv"

_default-args:
    #!/bin/bash
    echo
    echo "Default arguments:"

    labels=("PY_V: {{PY_V}}" "PY_T: {{PY_T}}" "PY_D: {{PY_D}}")
    comments=("Version of Python" "Python target (prod/dev)" "Python virtual environment folder")

    max_length=27
    for label in "${labels[@]}"; do
        length=${#label}
        if ((length > max_length)); then
            max_length=$length
        fi
    done

    for i in "${!labels[@]}"; do
        printf "    %-${max_length}s %b\n" "${labels[i]}" "\033[34m# ${comments[i]}\033[0m"
    done

    echo
    echo "Update an argument:"
    echo "    just --set <ARG_NAME> <ARG_VAL> <RECIPE>"


# ============================================================================ #
#                                   Constants                                  #
# ============================================================================ #


logs_dir := "logs"
domains_dir := "src/tyr/problems/domains"
planners_dir := "src/tyr/planners/planners"
python := PY_D + "/bin/python"


# ============================================================================ #
#                                     Clear                                    #
# ============================================================================ #


# Clear everything
clear-full: clear-venv clear-cov clear-logs
alias clear := clear-full

# Clear virtual environment
clear-venv:
    rm -rf {{ PY_D }}
    rm -rf **/*.egg-info

# Clear coverage
clear-cov:
    rm -rf coverage

# Clear logs
clear-logs:
    rm -rf {{ logs_dir }}


# ============================================================================ #
#                                    Install                                   #
# ============================================================================ #


# Install Python virtual environment
install-venv:
    if test ! -e {{ PY_D }}; then python{{ PY_V }} -m venv {{ PY_D }}; fi

# Install Python dependencies
install-pip: install-venv
    {{ python }} -m pip install -r requirements/{{ PY_T }}.txt
alias install := install-pip

# Install Python dependencies, planners, and domains
install-full: install-pip install-all-planners install-all-domains

# ================================== Domains ================================= #

# Install all integrated domains
install-all-domains: install-ipc-domains install-scheduling-domains install-custom-domains

_install-domain-submodule name:
    git submodule update --init --recursive {{ domains_dir }}/{{ name }}

# Install the IPC domains
install-ipc-domains:
    @just _install-domain-submodule ipc

# Install the Scheduling domains
install-scheduling-domains:
    @just _install-domain-submodule scheduling

# Install the Custom domains
install-custom-domains:
    @just _install-domain-submodule custom

# ================================= Planners ================================= #

# Install all integrated planners
install-all-planners: install-aries  install-enhsp install-linear-complex install-lpg install-optic install-panda-pi install-popf

_install-planner-submodule name:
    git submodule update --init --recursive {{ planners_dir }}/{{ name }}

_register-planner name:
    #!/bin/bash
    file="shortcuts/configuration/planners.yaml"
    line="name: {{ name }}"
    if ! grep -Fq "$line" "$file"
    then
        echo "- $line" >> "$file"
        echo "{{ name }} planner registered."
    else
        echo "{{ name }} planner already registered."
    fi

_register-planner-aries:
    #!/bin/bash
    file="shortcuts/configuration/planners.yaml"
    line="name: aries"
    if ! grep -Fq "$line" "$file"
    then
        echo "- $line" >> "$file"
        echo "  env:" >> "$file"
        echo "    ARIES_UP_ASSUME_REALS_ARE_INTS: \"true\"" >> "$file"
        echo "  upf_engine: tyr.planners.planners.aries.planning.unified.plugin.up_aries.Aries" >> "$file"
        echo "aries planner registered."
    else
        echo "aries planner already registered."
    fi

# Install the Aries planner
install-aries: install-venv
    @just _install-planner-submodule aries
    cargo build --release --bin up-server --manifest-path {{ planners_dir }}/aries/Cargo.toml
    cp {{ planners_dir }}/aries/target/release/up-server {{ planners_dir }}/aries/planning/unified/plugin/up_aries/bin/up-aries_linux_amd64
    {{ python }} -m pip install -r {{ planners_dir }}/aries/planning/unified/requirements.txt
    @just _register-planner-aries

# Install the ENHSP planner
install-enhsp: install-venv
    {{ python }} -m pip install up-enhsp
    @just _register-planner enhsp

# Install the LinearComplex planner
install-linear-complex:
    @just _install-planner-submodule linear-complex
    ./{{ planners_dir }}/linear-complex/install.sh
    @just _register-planner linear-complex

# Install the LPG planner
install-lpg:
    @just _install-planner-submodule lpg
    {{ python }} -m pip install -e {{ planners_dir }}/lpg
    @just _register-planner lpg

# Install the Optic planner
install-optic:
    @just _install-planner-submodule optic
    @just _register-planner optic

# Install the PandaPi planner
install-panda-pi:
    @just _install-planner-submodule pandapi
    ./{{ planners_dir }}/pandapi/install.sh
    @just _register-planner panda-pi

# Install the Popf planner
install-popf:
    @just _install-planner-submodule popf
    @just _register-planner popf


# ============================================================================ #
#                                     Reset                                    #
# ============================================================================ #


# Reset the python environment
reset-venv: clear-venv install-pip
alias reset := reset-venv

# Reset the python environment, planners, and domains
reset-full: clear-full install-full


# ============================================================================ #
#                                   Container                                  #
# ============================================================================ #


# Build the Apptainer image.
build-apptainer:
    apptainer build --fakeroot --writable-tmpfs container/tyr.sif container/tyr.def


# ============================================================================ #
#                                    Linters                                   #
# ============================================================================ #


# Format Justfile.
fmt-justfile:
    just --fmt --unstable

_lint linter folder *args:
    @echo "\033[1m\033[96m==> Linting {{ folder }} with {{ linter }}\033[0m"
    {{ python }} -m {{ linter }} {{ args }} {{ folder }}

# Run all python linters in the folder.
@lint +folders="src/ tests/":
    #!/usr/bin/env sh
    set -e;
    for folder in {{ folders }}; do
        just _lint "bandit" $folder "-r -c pyproject.toml";
        just _lint "black" $folder;
        just _lint "flake8" $folder;
        just _lint "isort" $folder;
        just _lint "mypy" $folder;
        just _lint "pylint" $folder;
    done


# ============================================================================ #
#                                     Tests                                    #
# ============================================================================ #


# Run pytest.
test-all +args="tests/":
    {{ python }} -m pytest {{ args }}

# Run pytest without slow tests.
test +args="tests/": (test-all "-m 'not slow'" args)

# Run pytest for coverage.
cov: (test-all "tests --cov src --cov-report term:skip-covered --cov-report html:coverage")


# ============================================================================ #
#                                      CI                                      #
# ============================================================================ #


_erase-planners-config-ci:
    rm -f shortcuts/configuration/planners.yaml
_install-planners-ci: _erase-planners-config-ci install-aries
_install-domains-ci: install-all-domains
_install-ci: install-pip _install-planners-ci _install-domains-ci
_reset-ci: reset-venv _install-planners-ci _install-domains-ci
_cov-ci: (test-all "tests --cov src --cov-report term --cov-report xml --junitxml report.xml")


# ============================================================================ #
#                                      CLI                                     #
# ============================================================================ #


# Run the tyr module.
tyr *args:
    {{ python }} -m tyr {{ args }}

# Run the bench command.
bench *args: (tyr "bench" args)

# Run the plot command.
plot *args: (tyr "plot" args)

# Run the slurm command.
slurm *args: (tyr "slurm" args)

# Run the solve command.
solve *args: (tyr "solve" args)

# Run the table command.
table *args: (tyr "table" args)
