# Use with https://github.com/casey/just

@_default:
    just --list --unsorted

# ================================= Variables ================================ #

coverage_dir := "coverage"
linters := "black flake8 isort mypy pylint"
python_dir := ".venv"
python_bin := "python3"
python := python_dir + "/bin/" + python_bin

# ================================== Install ================================= #

@_venv:
    if test ! -e {{ python_dir }}; then {{ python_bin }} -m venv .venv; fi

# Remove the virtual environment and all temporary files.
clear:
    rm -rf {{ python_dir }}
    rm -rf {{ coverage_dir }}
    rm -rf **/*.egg-info

# Install dependencies in a virtual environment. Target should be in [prod, dev].
install target="prod": _venv
    {{ python }} -m pip install -r requirements/{{ target }}.txt

# Clear then install the target.
reset target="prod": clear (install target)

# ================================== Linters ================================= #

_lint linter folder *args: _venv
    @echo "\033[1m\033[96m==> Linting {{ folder }} with {{ linter }}\033[0m"
    {{ python }} -m {{ linter }} {{args}}{{ folder }}

# Run all python linters in the folder. By default, run in src/ and tests/.
@lint +folders="src/ tests/":
    for folder in {{ folders }}; do \
        just _lint "bandit" $folder "-r -c pyproject.toml "; \
        for linter in {{ linters }}; do \
            just _lint $linter $folder; \
        done; \
    done;

# =================================== Tests ================================== #

# Run pytest.
test-all +args="tests/":
    {{ python }} -m pytest {{ args }}

# Run pytest without slow tests.
test +args="tests/": (test-all "-m 'not slow'" args)

# Run pytest for coverage.
cov: (test-all "tests --cov src --cov-report term:skip-covered --cov-report html:coverage")
