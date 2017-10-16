from django.urls import resolve
from django.http import HttpRequest



def test__uses_home_template(client):
    response = client.get('/')
    # check what template was used to render a response
    assert 'home.html' in [t.name for t in response.templates]

def test__can_save_a_POST_request(client):
    response = client.post('/', data={'item_text': 'A new list item'})
    assert 'A new list item' in response.content.decode()
