import json
from changelog_getter import get_root_file_names,get_urls
from unittest import mock


def test_print_urls():
    with open('mock_github_response.json') as f:
        mock_github_response = f
        with mock.patch('changelog_getter.urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = mock_github_response
            assert next(get_urls(["https://github.com/celery/celery"], token="secret!")) == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"
