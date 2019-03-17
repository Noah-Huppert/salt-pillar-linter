# Salt Pillar Linter
Lints Salt states and their use of pillars. Only Jinja supported.

# Table Of Contents
- [Overview](#overview)
- [Install](#install)

# Overview
Lints Salt states to ensure they are using Pillar keys which exist.  

This project exists because at times it can be challenging to debug Jinja 
render errors.

Only works with fairly standard Salt state setups which use Jinja and plain 
text pillars in SLS files.

Usage:

```
usage: salt-pillar-linter [-h] -p PILLARS_ROOT -s STATES_ROOT
                             [-f TMPL_FILE] [-d]

Lints Salt states to ensure pillars are used correctly

optional arguments:
  -h, --help       show this help message and exit
  -p PILLARS_ROOT  Directories where pillars are present, can be specified
                   multiple times
  -s STATES_ROOT   Directories where states are located, can be specified
                   multiple times
  -f TMPL_FILE     Non state files which uses Jinja templating to check, can
                   be specified multiple times
  -d               Print additional debug information
```

Sample output:

```
% salt-pillar-linter -p pillar -s salt
salt/foo/init.sls uses pillar keys which do not exist
    Line 151:
        foo.bar.config_file
```

See `salt-pillar-linter -h` for more details usage information.

# Install
1. Clone down the repository
2. Install dependencies
	- [Pipenv](https://pipenv.readthedocs.io/en/latest/) is used to manage 
	a virtual environment used by Salt Pillar Linter.
	- Install dependencies by running `pipenv install`
3. Add repository directory to `PATH`
4. Invoke `salt-pillar-linter`
