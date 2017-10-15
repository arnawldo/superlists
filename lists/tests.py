from django.urls import resolve
from django.http import HttpRequest



def test__uses_home_template(client):
    response = client.get('/')
    # check what template was used to render a response
    assert 'home.html' in [t.name for t in response.templates]
