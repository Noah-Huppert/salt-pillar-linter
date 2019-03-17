#!/usr/bin/env python3

import argparse
import os
import sys
import re

import yaml
import jinja2

# {{{1 Parse arguments
parser = argparse.ArgumentParser(description="Lints Salt states to ensure " +
                                 "pillars are used correctly")
parser.prog = 'salt-pillar-linter'
parser.add_argument('-p',
                    action='append',
                    metavar='PILLARS_ROOT',
                    required=True,
                    dest='pillar_roots',
                    help="Directories where pillars are present, can be " +
                        "specified multiple times")
parser.add_argument('-s',
                    action='append',
                    metavar='STATES_ROOT',
                    required=True,
                    dest='state_roots',
                    help="Directories where states are located, can be " +
                        "specified multiple times")
parser.add_argument('-f',
                    action='append',
                    metavar='TMPL_FILE',
                    dest='template_files',
                    help="Non state files which uses Jinja templating to " +
                        "check, can be specified multiple times")
parser.add_argument('-d',
                    action='store_true',
                    default=False,
                    dest='debug',
                    help="Print additional debug information")
args = parser.parse_args()

# {{{1 Locate all state and pillar files
def gather_sls_files(initial_dirs):
    """ Walks directories to find locations of all sls files
    """
    dirs = set()
    dirs.update(initial_dirs)

    sls_files = set()

    while dirs:
        root = dirs.pop()

        for top_dir, sub_dirs, files in os.walk(root):
            sls_files.update([os.path.join(top_dir, f) for f in files
                                if f != 'top.sls' and
                                   os.path.splitext(f)[1] == '.sls'])
            dirs.update([os.path.join(top_dir, sub_dir)
                                           for sub_dir in sub_dirs])

    return sls_files

pillar_files = gather_sls_files(args.pillar_roots)

state_files = gather_sls_files(args.state_roots)

if args.template_files:
    state_files.update(args.template_files)

# {{{1 Get all pillar keys
def flatten_dict(d, parent_key=''):
    """ Return array of flattened dict keys
    """

    keys = []

    for k in d:
        combined_key = k

        if parent_key:
            combined_key = "{}.{}".format(parent_key, k)

        if type(d[k]) == dict:


            keys.extend(flatten_dict(d[k], parent_key=combined_key))
        else:
            keys.append(combined_key)

    return keys

pillar_keys = {}

loader = jinja2.FileSystemLoader(searchpath=os.getcwd())
env = jinja2.Environment(loader=loader)

if args.debug:
    print("###################")
    print("# PARSING PILLARS #")
    print("###################")

for pillar_file in pillar_files:
    template = env.get_template(pillar_file)
    template_str = template.render()

    value = yaml.load(template_str)

    flat_keys = flatten_dict(value)

    if args.debug:
        print()
        print ("{} keys:".format(pillar_file))
        print()

        for k in flat_keys:
            print("    {}".format(k))

    for k in flat_keys:
        pillar_keys[k] = True

if args.debug:
    print()

# {{{1 Lint states
if args.debug:
    print("##################")
    print("# LINTING STATES #")
    print("##################")

jinja_pattern = re.compile(r"{{\s*pillar\.([0-9a-zA-Z\._]*)\s*}}")

for state_file in state_files:
    with open(state_file, 'r') as f:
        line_num = 1
        not_keys = {}

        if args.debug:
            print("{} keys used by state:".format(state_file))
            print()

        # For each line in a state
        for line in f:
            # For each Jinja pillar usage in state
            for match in re.finditer(jinja_pattern, line):
                # Get groups from match
                for pillar_str in match.groups():
                    if args.debug:
                        print("    {}".format(pillar_str))

                    # Check if pillar key used exists
                    if pillar_str not in pillar_keys:
                        # Create entry in not_keys dict for line if this is the 
                        # first item on this line
                        if line_num not in not_keys:
                            not_keys[line_num] = []

                        # Add pillar key to dict so we can tell user about
                        # improper usage later
                        not_keys[line_num].append(pillar_str)

            # Increment line number so we can keep track of where errors are
            line_num += 1

        if args.debug:
            print()

        # If any errors
        if not_keys:
            common_prefix = os.path.commonprefix([os.getcwd(), state_file])
            pretty_file_name = os.path.relpath(state_file, common_prefix)

            print("{} uses pillar keys which do not exist".format(pretty_file_name))

            for line_num in not_keys:
                print("    Line {}:".format(line_num))

                for k in not_keys[line_num]:
                    print ("        {}".format(k))

                print()
