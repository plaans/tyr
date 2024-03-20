# Use with https://github.com/casey/just

@_default:
    just --list --unsorted

# ================================= Variables ================================ #

aries_dir := "libs/aries"
coverage_dir := "coverage"
logs_dir := "logs"
python_dir := ".venv"
python := python_dir + "/bin/python"

# ================================== Install ================================= #

@_venv python_version="3.11":
    if test ! -e {{ python_dir }}; then python{{ python_version }} -m venv .venv; fi

# Remove the virtual environment and all temporary files.
clear:
    rm -rf {{ python_dir }}
    rm -rf {{ coverage_dir }}
    rm -rf {{ logs_dir }}
    rm -rf **/*.egg-info

# Install dependencies in a virtual environment. Target should be in [prod, dev].
install target="prod" python_version="3.11": (_venv python_version) build_aries
    {{ python }} -m pip install -r requirements/{{ target }}.txt

# Clear then re-install the target.
reset target="prod" python_version="3.11": clear (install target python_version)

# Build the up-server binary of Aries.
build_aries:
    cargo build --release --bin up-server --manifest-path {{ aries_dir }}/Cargo.toml
    cp {{ aries_dir }}/target/release/up-server {{ aries_dir }}/planning/unified/plugin/up_aries/bin/up-aries_linux_amd64

# ================================== Linters ================================= #

# Format Justfile.
fmt-justfile:
    just --fmt --unstable

_lint linter folder *args:
    @echo "\033[1m\033[96m==> Linting {{ folder }} with {{ linter }}\033[0m"
    {{ python }} -m {{ linter }} {{ args }} {{ folder }}

# Run all python linters in the folder. By default, run in src/ and tests/.
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

# =================================== Tests ================================== #

# Run pytest.
test-all +args="tests/":
    {{ python }} -m pytest {{ args }}

# Run pytest without slow tests.
test +args="tests/": (test-all "-m 'not slow'" args)

# Run pytest for coverage.
cov: (test-all "tests --cov src --cov-report term:skip-covered --cov-report html:coverage")


# ==================================== CI ==================================== #

_cov-ci: (test-all "tests --cov src --cov-report term --cov-report xml --junitxml report.xml")

_ci-local:
    just reset "dev" "3.12" 
    just lint
    just test
    just reset "dev" "3.8"
    just test
    just reset "dev" "3.9"
    just test
    just reset "dev" "3.10"
    just test
    just reset "dev" "3.11"
    just test

# ==================================== CLI =================================== #

# Run the tyr module.
tyr *args:
    {{ python }} -m tyr {{ args }}

# Run the analyse command.
analyse *args: (tyr "analyse" args)

# Run the bench command.
bench *args: (tyr "bench" args)

# Run the solve command.
solve *args: (tyr "solve" args)
