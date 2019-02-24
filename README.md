# Salt Pillar Linter
Lints Salt states and their use of pillars. Only Jinja supported.

# Table Of Contents
- [Overview](#overview)
- [Setup](#setup)

# Overview
Lints Salt states to ensure they are using Pillar keys which exist.  

This project exists because at times it can be challenging to debug Jinja 
render errors.

Only works with fairly standard Salt state setups which use Jinja and plain 
text pillars in SLS files.

Usage:

```
salt-pillar-linter.py -p PILLARS_ROOT -s STATES_ROOT
```

Sample output:

```
% salt-pillar-linter.py -p pillar -s salt
salt/foo/init.sls uses pillar keys which do not exist
    Line 151:

        foo.bar.config_file
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
