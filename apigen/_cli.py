# -*- coding: utf-8 -*-
# Copyright 2019 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Meraki-APIgen:
    Code generator for the Meraki API

USAGE:
    meraki-apigen (--key <apikey>) [--language <name>]
                  [--classy] [--lint] [--no-wrap] [--add-sample-resp]
                  [-h | --help] [-v | --version]

DESCRIPTION:
    Convert all of the recently released Meraki v0 API calls into
    Python or Ruby. As new API calls are released all the time, rerun
    this occasionally.

OPTIONS:
  --key <apikey>        Your API key. You can find it by going to your profile.
  --language <name>     Create a script in language. Valid options are
                        python, ruby, and bash. Python is the default.
                        For ruby linting, ruby/gem will need to be installed.
  -c, --classy          Use classes instead of a function list.
  -l, --lint            Call Pylint. If not 10.00/10, print error text.
  -r, --add-sample-resp
                        Add the sample response to function documentation.
  -n, --no-wrap         Do not wrap text to 79 width with yapf.
                        Default is to wrap.
  -h, --help            Print this help message.
  -v, --version         Print version and exit.

SEE ALSO:
    Contact: Ross Jacobs (rosjacob [AT] cisco.com)
    Github: https://github.com/pocc/meraki-apigen
"""
import sys
import subprocess as sp
import re

import docopt

from requests import __version__ as requests_version
from yapf import __version__ as yapf_version
from apigen import __version__ as apigen_version


def get_bash_version():
    """Get the bash version if it exists and a message if it does not.

    Should return a string like '3.2.57(1)-release (x86_64-apple-darwin18)'
    """
    try:
        cmd_list = ['bash', '--version']
        sp_pipe = sp.Popen(cmd_list, stdout=sp.PIPE)
        sp_stdout = sp_pipe.communicate()[0].decode('utf-8')
        version_info = sp_stdout.split('version ')[1].split('\n')[0]
        return version_info
    except FileNotFoundError:
        msg = 'not found (required for bash testing)'
        return msg


def get_ruby_versions():
    """Check whether ruby/gem is installed. If so, then rubocop can be used."""
    try:
        sp_ruby_ver = sp.Popen(['ruby', '-v'], stdout=sp.PIPE)
        sp_gem_ver = sp.Popen(['gem', '-v'], stdout=sp.PIPE)
        ruby_ver = sp_ruby_ver.communicate()[0].decode('utf-8')
        gem_ver = sp_gem_ver.communicate()[0].decode('utf-8')
        return re.sub(r'\n|ruby ', '', ruby_ver), re.sub(r'\n', '', gem_ver)
    # If not installed, catch the error and return not found.
    except FileNotFoundError:
        msg = 'not found (required for ruby linting and testing)'
        return msg, msg


def show_cli():
    """Show the docopt cli"""
    args = docopt.docopt(__doc__)
    if args['--version']:
        python_ver = sys.version.replace('\n', '')
        print('Meraki-APIgen', apigen_version, '\n\nPython', python_ver)
        print('\trequests', requests_version, '\n\tyapf', yapf_version)
        print('Testing/linting')
        ruby_ver, gem_ver = get_ruby_versions()
        print('\truby', ruby_ver, '\n\tgem', gem_ver)
        print('\tbash', get_bash_version())
        sys.exit()
    # Python is default
    if not args['--language']:
        args['--language'] = 'python'
    if args['--language'] not in ['bash', 'python', 'ruby']:
        raise ValueError(
            "Only valid languages are python and ruby.\n" + __doc__)

    # Reformatting args so that other modules can use options like a dict
    args['textwrap'] = not args['--no-wrap']
    # These are all of the user-selected options.
    options = [arg.replace('--', '') for arg in args if args[arg]]
    return args['--key'], args['--language'], options
