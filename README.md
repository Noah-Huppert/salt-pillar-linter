# Salt Pillar Linter
Lints Salt states and their use of pillars. Only Jinja supported.

# Table Of Contents
- [Overview](#overview)
- [Setup](#setup)

# Overview
Lints Salt states to ensure they are using Pillar value which exist.  

This project exists because the Salt tool does not provide the best output 
when you use a Pillar in a state which does not exist.  

Only works with fairly standard Salt state setups which use Jinja and plain 
text pillars in SLS files.

Usage:

```
salt-pillar-linter.py -p PILLARS_ROOT -s STATES_ROOT
```

See `salt-pillar-linter -h` for more details usage information.

# Setup
[Pipenv](https://pipenv.readthedocs.io/en/latest/) is used to manage a virtual 
environment used by Salt Pillar Linter.

Setup:

1. Install dependencies:
   ```
   pipenv install
   ```
2. Run:
   ```
   pipenv run salt-pillar-linter.py OPTIONS...
   ```
