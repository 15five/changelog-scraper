from python_get_repo_link import clean_package_name

def test_clean_package_name():
    assert clean_package_name("a==3") == 'a'
    assert clean_package_name("a>=3") == 'a'
    assert clean_package_name("a<=3") == 'a'
    assert clean_package_name("a>3") == 'a'
    assert clean_package_name("a<3") == 'a'
    assert clean_package_name("a==3 #comment") == 'a'
    assert clean_package_name(" a ") == 'a'