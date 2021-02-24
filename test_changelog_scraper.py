import json
from changelog_getter import get_root_file_names,get_urls
from unittest import mock


def test_print_urls():
    assert next(get_urls(["https://github.com/celery/celery"], token="secret!")) == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"

# def test_print_urls():
#     with open('mock_github_response.json') as f:
#         mock_github_response = f
#     with mock.patch('urllib.request.urlopen') as mock_urlopen:
#         mock_urlopen.return_value = mock_github_response
#         assert next(get_urls(["foo"])) == "https://github.com/15five/rocket_releaser"

#         del mock_github_response['info']['home_page']
#         mock_urlopen.return_value = mock_github_response
#         assert next(get_urls(["foo"])) == "https://github.com/15five/rocket_releaser"

#         mock_github_response['info']['project_urls']['home_page'] = "non_repo_website"
#         mock_github_response['info']['project_urls']['source'] = "https://github.com/15five/foo"
#         mock_urlopen.return_value = mock_github_response
#         assert next(get_urls(["foo"])) == "https://github.com/15five/foo"