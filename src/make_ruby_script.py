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
"""Generate ruby script."""
import re


def make_ruby_function(func_name, func_desc, func_args,
                       req_http_type, req_path):
    """Generate a ruby function given the paramaters."""
    ruby_indented_func_desc = func_desc.replace('  ', ' ')

    params_should_be_in_url = req_http_type in ['GET', 'DELETE']
    if func_args:  # If there is more than the function description, +newline
        func_desc += '\n    '
    if 'params' in func_args:
        func_args = func_args.replace('params', 'params=nil')
        if params_should_be_in_url:
            func_urlencoded_query = """
    url_query = URI::encode(params)
    url_query = '?' + url_query.gsub('&', '?')"""
            # Add additional format variable for params arg to be sent in
            req_data = '[]'
        else:  # req_http_type in ['PUT', 'POST'], data in requests body
            func_urlencoded_query = ''
            req_data = 'params.to_json'
    else:
        func_urlencoded_query = ''
        req_data = '[]'
    for arg in func_args.split(', '):
        infix_arg = '#{' + arg + '}'
        req_path = re.sub(r'\[[a-zA-z-_]*?\]', infix_arg, req_path, count=1)
    if func_args:  # Don't add parentheses if no args (ruby syntactic sugar)
        func_args = '(' + func_args + ')'  # get_orgs() => get_orgs
    function_text = """\ndef {0}{1}
  <<-HEREDOC
  {2}HEREDOC{3}
  api_call('{4}', "#{{$base_url}}{5}", {6})
end""".format(
        func_name,
        func_args,
        ruby_indented_func_desc,
        func_urlencoded_query,
        req_http_type.upper(),
        req_path,
        req_data
    )
    return function_text


def make_ruby_script(api_key, api_calls, preamble, options):
    """Make ruby script."""
    # Indent preamble heredoc exactly 2 spaces
    preamble = ('  ' + re.sub(r'\n[ ]*', '\n  ', preamble))[:-2]
    output_file = 'meraki_api.rb'
    generated_text = """\
<<-HEREDOC
{}HEREDOC

require 'net/http'
require 'uri'
require 'json'

$base_url = 'https://api.meraki.com/api/v0'

# From Ruby docs. One redirect is expected: a second is not.
def api_call(http_method, url, options, limit = 2)
  raise ArgumentError, 'too many HTTP redirects' if limit.zero?

  uri = URI.parse(url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  case http_method
  when 'GET' then
    request = Net::HTTP::Get.new(uri.request_uri)
  when 'POST' then
    request = Net::HTTP::Post.new(uri.request_uri)
    request.body = options.to_json
  when 'PUT' then
    request = Net::HTTP::Put.new(uri.request_uri)
    request.body = options.to_json
  when 'DELETE' then
    request = Net::HTTP::Delete.new(uri.request_uri)
  else
    raise ArgumentError, 'Invalid HTTP method'
  end
  request['Content-Type'] = 'application/json'
  request['X-Cisco-Meraki-Api-Key'] = {}
  request['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36  (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'
  response = http.request(request)

  case response
  when Net::HTTPSuccess then
    response.body
  when Net::HTTPRedirection then
    api_call(http_method, response['location'], options, limit - 1)
  else
    response.value
  end
end

""".format(preamble, api_key)
    if options:
        print("WARNING: Ruby options currently won't do anything.")
    whitespace_between_functions = '\n\n'
    for api_call in api_calls:
        generated_text += make_ruby_function(
            func_name=api_call['gen_api_name'],
            func_desc=api_call['gen_func_desc'],
            func_args=api_call['gen_func_args'],
            req_http_type=api_call['http_method'],
            req_path=api_call['path']) \
            + whitespace_between_functions
    with open(output_file, 'w') as myfile:
        print('\t- saving ' + output_file + '...')
        myfile.write(generated_text)

    print("\nRuby module generated!")