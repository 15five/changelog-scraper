#!/usr/bin/env python
import json
from sys import argv, stderr, stdin
from time import sleep
from typing import Dict, Iterable
from urllib.request import urlopen


def get_pypi_json(package_name: str) -> Dict:
    with urlopen(f"https://pypi.org/pypi/{package_name}/json") as u:
        return json.loads(u.read().decode())


def clean_package_name(package_name: str):
    """
    Simplistic cleaning of a line from a requirement file into a plain package name.
    Does not handle all cases!
    """
    # I should probably replace this w/ https://github.com/davidfischer/requirements-parser
    clean_name = ""
    for character in package_name:
        # get rid of extra packages, we just want base
        # ex: main_package[extra] -> main_package
        # get rid of version, changelog will have version history anyways
        # get rid of comments or egg, either way useless
        if character in "[=<>#!":
            break
        clean_name += character
    # get rid of user typos or newlines at end
    return clean_name.strip()


POSSIBLE_URL_NAMES = ["home_page", "source", "code", "homepage", "source code"]
# KEEP ABOVE LOWERCASE


def get_repo_link(f: Iterable[str]):
    """yields a repo link for each package in f

    Args:
        f: any iterable yielding package names. Ex: ['django']
    """
    for package in f:
        try:
            package = clean_package_name(package)
            if package == "":
                continue
            link = None
            response = get_pypi_json(package)
            project_urls = response["info"].get("project_urls", {})
            if project_urls is None:
                project_urls = {}
            if "home_page" in response["info"]:
                project_urls["home_page"] = response["info"]["home_page"]

            # make sure we are in lowercase for case-insensitive comparison
            # Also remove useless None urls to avoid TypeError later on
            project_urls: Dict[str, str] = {
                k.lower(): v for k, v in project_urls.items() if v is not None
            }

            for url_name in POSSIBLE_URL_NAMES:
                if url_name in project_urls and "github.com" in project_urls[url_name]:
                    link = project_urls[url_name]
                    break
            if link:
                yield link
            else:
                yield package + " unknown"
        except Exception:
            stderr.write(f"package {package} ran into an error:\n")
            raise
        sleep(1)  # be nice to API


if __name__ == "__main__":
    # We want to be a well-behaved linux utility
    # so we read from either stdin or first arg as file
    f = stdin
    if len(argv) > 1:
        f = open(argv[1])
    [print(package) for package in get_repo_link(f)]
