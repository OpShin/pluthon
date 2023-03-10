Pluthon
=======
[![Build Status](https://app.travis-ci.com/OpShin/pluthon.svg?branch=master)](https://app.travis-ci.com/OpShin/pluthon)
 [![PyPI version](https://badge.fury.io/py/pluthon.svg)](https://pypi.org/project/pluthon/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pluthon.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/pluthon.svg)](https://pypi.org/project/pluthon/)


Pluto-like programming language for Cardano Smart Contracts in Python

## What is this?

This is an programming language that compiles down to Untyped Plutus Language Core, inspired by MLabs [pluto](https://github.com/Plutonomicon/pluto)
programming language.
It is used as an intermediate step when compiling a pythonic smart contract language down to UPLC.


## Contributing

Contributions are very welcome.

## Notes

- Some higher level functions defined in pluthon use UPLC builtin variables. In order to avoid naming conflicts, all variables assigned start with "0" and end with "_".
