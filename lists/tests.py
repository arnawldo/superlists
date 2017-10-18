from django.urls import resolve
from django.http import HttpRequest

from lists.models import Item, List

import pytest

@pytest.mark.django_db
def test__uses_home_template(client):
    response = client.get('/')
    # check what template was used to render a response
    assert 'home.html' in [t.name for t in response.templates]

# ITEMS AND LIST MODELS
@pytest.mark.django_db
def test__saving_and_retrieving_items():
    list_ = List()
    list_.save()

    first_item = Item()
    first_item.text = 'The first (ever) list item'
    first_item.list = list_
    first_item.save()

    second_item = Item()
    second_item.text = 'Item the second'
    second_item.list = list_
    second_item.save()

    saved_list = List.objects.first()
    assert saved_list == list_
    saved_items = Item.objects.all()
    assert saved_items.count() == 2

    first_saved_item = saved_items[0]
    second_saved_item = saved_items[1]
    assert first_saved_item.text == 'The first (ever) list item'
    assert first_saved_item.list == list_
    assert second_saved_item.text == 'Item the second'
    assert second_saved_item.list == list_

@pytest.mark.django_db
def test__only_saves_items_when_necessary(client):
    client.get('/')
    assert Item.objects.count() == 0

# LIST VIEW
@pytest.mark.django_db
def test__uses_list_template(client):
    list_ = List.objects.create()
    response = client.get(f'/lists/{list_.id}/')
    assert 'list.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test__displays_only_items_for_that_list(client):
    correct_list = List.objects.create()
    Item.objects.create(text='itemey 1', list=correct_list)
    Item.objects.create(text='itemey 2', list=correct_list)
    other_list = List.objects.create()
    Item.objects.create(text='other list item 1', list=other_list)
    Item.objects.create(text='other list item 1', list=other_list)

    response = client.get(f'/lists/{correct_list.id}/')

    assert 'itemey 1' in response.content.decode()
    assert 'itemey 2' in response.content.decode()
    assert 'other list item 1' not in response.content.decode()
    assert 'other list item 2' not in response.content.decode()

# NEW LIST
@pytest.mark.django_db
def test__can_save_a_POST_request(client):
    response = client.post('/lists/new', data={'item_text': 'A new list item'})

    assert Item.objects.count() == 1
    new_item = Item.objects.first()
    assert new_item.text == 'A new list item'

@pytest.mark.django_db
def test__redirects_after_POST(client):
    response = client.post('/lists/new', data={'item_text': 'A new list item'})
    new_list = List.objects.first()
    assert response.status_code == 302
    assert response['location'] == f'/lists/{new_list.id}/'

@pytest.mark.django_db
def test__passes_correct_list_to_template(client):
    other_list = List.objects.create()
    correct_list = List.objects.create()
    response = client.get(f'/lists/{correct_list.id}/')
    assert response.context['list'] == correct_list

# NEW ITEM
@pytest.mark.django_db
def test__can_save_a_POST_request_to_an_existing_list(client):
    other_list = List.objects.create()
    correct_list = List.objects.create()

    response = client.post(f'/lists/{correct_list.id}/add_item', 
        data={'item_text': 'A new item for an existing list'}
        )
    assert response.status_code == 302
    assert response['location'] == f'/lists/{correct_list.id}/'
