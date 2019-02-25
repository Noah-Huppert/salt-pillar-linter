#!/usr/bin/env python3

import argparse
import os
import sys
import re

import yaml
import jinja2

# {{{1 Parse arguments
parser = argparse.ArgumentParser(description="Lints Salt states to ensure" +
                                 "pillars are used correctly")
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
args = parser.parse_args()

# {{{1 Locate all state and pillar files
def gather_sls_files(dirs):
    """ Walks directories to find locations of all sls files
    """

    sls_files = []

    while dirs:
        root = dirs.pop()

        for top_dir, sub_dirs, files in os.walk(root):
            sls_files.extend([os.path.join(top_dir, f) for f in files
                                if f != 'top.sls' and
                                   os.path.splitext(f)[1] == '.sls'])
            dirs.extend([os.path.join(top_dir, sub_dir)
                                           for sub_dir in sub_dirs])

    return sls_files

pillar_files = gather_sls_files(args.pillar_roots)
state_files = gather_sls_files(args.state_roots)

# {{{1 Get all pillar keys
def flatten_dict(d, parent_key=''):
    """ Return array of flattened dict keys
    """

    keys = []

    for k in d:
        if type(d[k]) == dict:
            call_parent_key = k

            if parent_key:
                call_parent_key = "{}.{}".format(parent_key, k)

            keys.extend(flatten_dict(d[k], parent_key=call_parent_key))
        else:
            keys.append("{}.{}".format(parent_key, k))

    return keys

pillar_keys = {}

loader = jinja2.FileSystemLoader(searchpath=os.getcwd())
env = jinja2.Environment(loader=loader)

for pillar_file in pillar_files:
    template = env.get_template(pillar_file)
    template_str = template.render()

    value = yaml.load(template_str)

    for k in flatten_dict(value):
        pillar_keys[k] = True

# {{{1 Lint states
jinja_pattern = re.compile(r"{{\s*pillar\.([a-zA-Z\._]*)\s*}}")

for state_file in state_files:
    with open(state_file, 'r') as f:
        line_num = 1
        not_keys = {}

        for line in f:

            for match in re.finditer(jinja_pattern, line):
                for pillar_str in match.groups():
                    if pillar_str not in pillar_keys:
                        if line_num not in not_keys:
                            not_keys[line_num] = []

                        not_keys[line_num].append(pillar_str)

            line_num += 1

        if not_keys:
            common_prefix = os.path.commonprefix([os.getcwd(), state_file])
            pretty_file_name = os.path.relpath(state_file, common_prefix)

            print("{} uses pillar keys which do not exist".format(pretty_file_name))

            for line_num in not_keys:
                print("    Line {}:".format(line_num))

                for k in not_keys[line_num]:
                    print ("        {}".format(k))

                print()
