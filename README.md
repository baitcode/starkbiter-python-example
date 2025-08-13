# About

This is a repo showcasing usage of starkbitier python bindings to simulate behaviors over the Starknet blockchain.

This project PDM for dependency management.

To create env do:

```bash
pdm venv create
```

To activate it:
```bash
eval $(pdm venv activate)
```

To install dependencies when env activated:
```bash
pdm install
```

To run the example:
```bash
python src/main.py
```

# Structure

`starkbiter` package has wrappers around starkbiter_bindings.
    `known_calls` - collection of factories for Call objects for known contracts (ekubo core, swapper, UDC)
    `accounts` - contains Account class that exposes `call` and `execute` methods
    `middleware` - is a class to interact with environment, is not supposed to be shared among several threads. Consider it a connection. Every thread (or coroutine) should have it's own.
    `environement` - is blockchain instance. One per label. Also has Token classifier.

`main.py` is the example on how to spin the environment, fork it, and run agents that interact with it

Please, check main.py for more examples.

Library relies heavily on nethermind.starknet-abi lib.

# Compatibility

Currently starkbiter only has wheel for python 3.12.x version MAC OS (darwin) version. 
