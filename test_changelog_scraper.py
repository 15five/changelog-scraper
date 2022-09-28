import json
from unittest import mock

from changelog_getter import get_root_file_names, get_urls


def test_passes_unknown_through_verbatim():
    assert next(get_urls(["django unknown"], token="secret!")) == "django unknown"


def test_print_urls():
    with open("mock_github_response.json") as mock_github_response:
        with mock.patch("changelog_getter.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_github_response
            assert (
                next(
                    get_urls(
                        ["https://github.com/celery/celery/blob/master/README.rst"],
                        token="secret!",
                    )
                )
                == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"
            )


def test_print_multiple_urls():
    with mock.patch("changelog_getter.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = [
            open("mock_github_response.json"),
            open("mock_github_response.json"),
        ]
        urls = list(
            get_urls(
                [
                    "https://github.com/celery/celery/blob/master/README.rst",
                    "https://github.com/celery/celery",
                ],
                token="secret!",
            )
        )
        assert (
            urls[0]
            == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"
        )
        assert (
            urls[1]
            == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"
        )


@mock.patch("changelog_getter.Path")
@mock.patch("changelog_getter.urllib.request.urlretrieve")
def test_downloads_changelogs(mock1, mock2):
    with open("mock_github_response.json") as f:
        mock_github_response = f
        with mock.patch("changelog_getter.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_github_response
            assert (
                next(
                    get_urls(
                        ["https://github.com/celery/celery/blob/master/README.rst"],
                        token="secret!",
                        output_dir="foo",
                    )
                )
                == "https://raw.githubusercontent.com/celery/celery/HEAD/Changelog.rst"
            )
            mock1.assert_called_once()
            mock2.assert_called_once()
