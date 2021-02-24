import json
from python_get_repo_link import clean_package_name,get_repo_link
from unittest import mock

def test_clean_package_name():
    assert clean_package_name("a==3") == 'a'
    assert clean_package_name("a>=3") == 'a'
    assert clean_package_name("a<=3") == 'a'
    assert clean_package_name("a>3") == 'a'
    assert clean_package_name("a<3") == 'a'
    assert clean_package_name("a==3 #comment") == 'a'
    assert clean_package_name(" a ") == 'a'


def test_get_repo_link():
    with open('mock_pypi_response.json') as f:
        mock_pypi_json = json.loads(f.read())
    with mock.patch('python_get_repo_link.get_pypi_json') as mock_get_pypi_json:
        mock_get_pypi_json.return_value = mock_pypi_json
        assert next(get_repo_link(["foo"])) == "https://github.com/15five/rocket_releaser"

        del mock_pypi_json['info']['home_page']
        mock_get_pypi_json.return_value = mock_pypi_json
        assert next(get_repo_link(["foo"])) == "https://github.com/15five/rocket_releaser"

        mock_pypi_json['info']['project_urls']['home_page'] = "non_repo_website"
        mock_pypi_json['info']['project_urls']['source'] = "https://github.com/15five/foo"
        mock_get_pypi_json.return_value = mock_pypi_json
        assert next(get_repo_link(["foo"])) == "https://github.com/15five/foo"