#!/usr/bin/env python
import argparse
import json
import urllib.parse
import urllib.request
from os.path import join
from pathlib import Path
from sys import stdin
from time import sleep
from typing import Iterable, List, Optional

verbosity = 0
target_files = [
    "CHANGELOG",
    "CHANGES",
    "HISTORY",
    "RELEASES",
    "NEWS",
]  # default, todo allow override
graphql_root_files_query = """
query GetFilesQuery($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo,) {
      object(expression: "HEAD:") {
        ... on Tree {
          entries {
            name
            type
          }
        }
      }
    }
  }
"""
# want to play around with above? Try https://docs.github.com/en/graphql/overview/explorer


def get_root_file_names(org_or_user: str, repo: str, token: str) -> List[str]:
    variables = {"owner": org_or_user, "repo": repo}
    payload = {"query": graphql_root_files_query, "variables": variables}
    headers = {"Authorization": "Bearer " + token}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        method="POST",
        headers=headers,
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(req) as u:
        response = json.load(u)
        if "errors" in response:
            if response["errors"][0].get("type", "") == "NOT_FOUND":
                return []
            else:
                raise Exception(response["errors"][0]["message"])
        entries = response["data"]["repository"]["object"]["entries"]
        # "blobs" are files and we only want files
        return [entry["name"] for entry in entries if entry["type"] == "blob"]


def get_urls(urls: Iterable[str], token: str, output_dir: Optional[str] = None):
    """yields a changelog link for each repo link in urls

    Args:
        urls: any iterable yielding repo links. Ex: ['https://github.com/15five/changelog-scraper']
        token: github token
        output_dir: dir to write changelog files to. Defaults to None.

    Yields:
        str: changelog url
    """
    for url in urls:
        # url ex:  https://github.com/boto/boto3/
        # clean url
        url = url.strip().rstrip("/")
        if len(url) == 0:
            continue
        if url.rfind(" unknown") > -1:
            # package requirement parser was unable to find vcs link
            # so we pass unknown through verbatim
            yield url
            continue
        parsed_url = urllib.parse.urlparse(url)
        # we don't care about anything after repo name
        # ex: "/boto/boto3/blob/main/readme.md" -> ["","boto","boto3"]
        seperated_path = parsed_url.path.split("/")[:3]
        new_path = "/".join(seperated_path)
        url = urllib.parse.urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment,
            )
        )

        changelog_found = False

        # for getting file contents if changelog found
        raw_url = url.replace("github.com", "raw.githubusercontent.com")
        org_or_user = seperated_path[1]  # ex: boto
        repo = seperated_path[2]  # ex: boto3
        root_file_names = get_root_file_names(
            org_or_user=org_or_user,
            repo=repo,
            token=token,
        )
        if verbosity > 0:
            print("searching through files: " + str(root_file_names))
        for file_name in root_file_names:
            upper_case_name = file_name.upper()
            for target_file in target_files:
                if upper_case_name.startswith(target_file):
                    changelog_found = True
                    raw_url_full = f"{raw_url}/HEAD/{file_name}"
                    if output_dir:
                        out_dir_full = join(output_dir, org_or_user, repo)
                        # urlretrieve requires path to already exist
                        Path(out_dir_full).mkdir(parents=True, exist_ok=True)
                        sleep(1)  # be nice to API
                        urllib.request.urlretrieve(
                            raw_url_full, join(out_dir_full, "CHANGELOG.md")
                        )
                    yield raw_url_full
                    break
            if changelog_found:
                break
        if not changelog_found:
            yield f"no changelog found for {url}"
        sleep(1)  # be nice to API


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "Prints link to changelog given a github repo link, or optionally downloads the changelog for you"
    parser.add_argument(
        "filepath",
        nargs="?",
        type=argparse.FileType("r"),
        default=stdin,
        help="Path to a file with a newline-seperated list of github repo url's. Defaults to stdin.",
    )
    parser.add_argument("-t", "--token", help="GitHub API Token", type=str)
    parser.add_argument(
        "-o",
        "--outputdirectory",
        help="If specified downloads changelogs to this dir in the form dir/owner/repo/CHANGELOG.md",
        type=str,
    )
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    parsed_args = parser.parse_args()
    f = parsed_args.filepath  # argparse actually turns filepath into a file for us :D
    verbosity = parsed_args.verbosity
    [
        print(url)
        for url in get_urls(
            token=parsed_args.token, output_dir=parsed_args.outputdirectory
        )
    ]
