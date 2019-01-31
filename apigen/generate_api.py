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
"""Main file for Meraki-APIgen. Should only import from project files."""

import apigen._cli as cli
import apigen._web as web
import apigen.generate_method as make_method

import apigen.make_bash_script as mbs
import apigen.make_python_script as mps
import apigen.make_ruby_script as mrs


def main():
    """Main func.
    Should take care of all functions that are shared across languages."""
    api_key, language, options = cli.show_cli()
    api_json = web.fetch_apidocs_json()

    api_calls = make_method.modify_api_calls(api_json, options)
    http_stats = make_method.get_http_stats(api_calls)
    preamble = make_method.get_preamble(len(api_calls), http_stats, language)

    print('Generating a {' + language + '} script')
    if language == 'python':
        mps.make_python_script(api_key, api_calls, preamble, options)
    elif language == 'ruby':
        mrs.make_ruby_script(api_key, api_calls, preamble, options)
    elif language == 'bash':
        mbs.make_bash_script(api_key, api_calls, preamble)


if __name__ == '__main__':
    main()
