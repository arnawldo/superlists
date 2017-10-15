from django.urls import resolve
from lists.views import home_page

def test__root_url_resolves_to_home_page_view():
    found = resolve('/')
    assert found.func is home_page
