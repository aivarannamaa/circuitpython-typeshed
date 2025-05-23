# circuitpython-typeshed

This package contains a custom [typeshed](https://github.com/python/typeshed) suitable for type-checking or completing 
CircuitPython code.

The goal has been to provide CircuitPython specific stubs also for modules present in CPython's stdlib, which 
some type-checkers (e.g. MyPy) may consider special.
For this reason, the stubs are arranged into typeshed layout (i.e. under `stdlib` and `stubs` folders). 
This means, it doesn't suffice to install this package into a venv -- you also
need to set your type-checker's typeshed path to the installation directory of this package.

The stubs and typeshed helpers are compiled from the following sources.

* Most stubs come from [circuitpython-stubs](https://pypi.org/project/circuitpython-stubs/), including the stubs present in the sdist of said package
  but omitted from the wheel (`math`, `os`, `random`, `struct`, `ssl`, `time`).
* Typeshed helpers and some stdlib stubs come from [micropython-stdlib-stubs](https://pypi.org/project/micropython-stdlib-stubs/).
* Remaining stdlib stubs come from [micropython-rp2-stubs](https://pypi.org/project/micropython-rp2-stubs/).  

## Installation

You can install this package into a venv (e.g. `pip install circuitython-typeshed`) or into a plain directory
(e.g. `python3 -m pip install circuitpython-typeshed --target typeshed --no-user`).

## Using with Pyright and basedpyright

You need to indicate the installed location via the `-t` (or `--typeshedpath`) option (e.g.
 `pyright -t .venv/lib/python3.10/site-packages my-code.py` or `pyright -t typeshed my-code.py`).

## Using with MyPy

You need to indicate the installed location via the `--custom-typeshed-dir` option (e.g. `mypy --custom-typeshed-dir typeshed my-code.py`).
  