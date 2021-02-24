#!/usr/bin/env python
import json
import re
from sys import argv, stdin
from time import sleep
from urllib.request import urlopen


def mock_get_pypi_json():
    """ for testing """
    with open('mock_pypi_response.json') as f:
        return json.loads(f.read())


def get_pypi_json(package_name):
    with urlopen(f'https://pypi.org/pypi/{package_name}/json') as u:
        return json.loads(u.read().decode())


def clean_package_name(package_name: str):
    """
    Simplistic cleaning of a line from a requirement file into a plain package name
    Does not handle all cases!
    """
    # I should probably replace this w/ https://github.com/davidfischer/requirements-parser
    clean_name = ''
    for character in package_name:
        # get rid of extra packages, we just want base
        # ex: main_package[extra] -> main_package
        # get rid of version, changelog will have version history anyways
        # get rid of comments or egg, either way useless
        if character in '[=<>#!':
            break
        clean_name += character
    # get rid of user typos or newlines at end
    return clean_name.strip()


possible_url_names = ['home_page', 'Source', 'Code', 'Homepage']


def get_repo_link(f):
    """yields a repo link for each package in f

    Args:
        f (TextIO): text stream
    """
    for package in f:
        package = clean_package_name(package)
        if package == '': continue
        link = None
        response = get_pypi_json(package)
        project_urls = response['info'].get('project_urls', {})
        if project_urls is None: project_urls = {}
        if 'home_page' in response['info']:
            project_urls['home_page'] = response['info']['home_page']

        for url_name in possible_url_names:
            if url_name in project_urls and 'github.com' in project_urls[url_name]:
                link = project_urls[url_name]
                break
        if link:
            yield link
        else:
            yield package + ' unknown'
        sleep(1)  # be nice to API

if __name__ == "__main__":
    # We want to be a well-behaved linux utility
    # so we read from either stdin or first arg as file
    f = stdin
    if len(argv) > 1:
        f = open(argv[1])
    [print(package) for package in get_repo_link(f)]