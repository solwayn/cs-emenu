import freezegun
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from menu_cards.models import Dish, FOOD_TYPE_CHOICES
from model_bakery import baker
from menu_cards.tests.test_menu_endpoint_api import TIMESTAMP
from seeder.management.commands.seed_db import (
    EXAMPLE_VEGAN_DISHES,
    EXAMPLE_VEGETARIAN_DISHES,
)

DISHES_LIST_URL = 'dishes-list'
DISHES_DETAIL_URL = 'dishes-detail'

pytestmark = pytest.mark.django_db


def test_dishes__list_all_dishes(superadmin_client, vegan_menu):
    url = reverse(DISHES_LIST_URL)
    response = superadmin_client.get(url)
    db_names = vegan_menu.dishes.only('name').values_list('name', flat=True)
    for item in response.data:
        assert item.get('name') in db_names
    assert response.status_code == status.HTTP_200_OK


def test_dishes__get_shows_name_of_menu_card(
    superadmin_client, vegetarian_menu
):
    url = reverse(DISHES_LIST_URL)
    response = superadmin_client.get(url)

    assert all([item.get('menu_card') for item in response.data])
    assert response.status_code == status.HTTP_200_OK


def test_dishes__retrieve_single_dish(superadmin_client, vegetarian_dish):
    dish_from_db = Dish.objects.only('id').first()
    url = reverse(DISHES_DETAIL_URL, args=(dish_from_db.id,))
    response = superadmin_client.get(url)
    assert dish_from_db.id == response.data.get('id')
    assert response.status_code == status.HTTP_200_OK


def test_dishes__single_dish_creation(
    superadmin_client, valid_data_for_dish_creation
):
    url = reverse(DISHES_LIST_URL)
    response = superadmin_client.post(
        url, data=valid_data_for_dish_creation, format='json'
    )
    created_dish = response.data
    dish_exists = Dish.objects.filter(id=created_dish.get('id')).exists()
    assert dish_exists
    assert response.status_code == status.HTTP_201_CREATED


def test_dishes__dish_creation_error_on_wrong_data(
    superadmin_client, invalid_data_for_dish_creation
):
    url = reverse(DISHES_LIST_URL)
    response = superadmin_client.post(
        url, data=invalid_data_for_dish_creation, format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


class DishesEndpointTest(TestCase):
    def setUp(superadmin_client):
        """Setup for tests to seed db with a test data"""

        vegan_card = create_menu_card(
            dict(name='Vegan card', description='for carrots lovers'),
            dict(food_type=FOOD_TYPE_CHOICES.vegan),
            EXAMPLE_VEGAN_DISHES,
        )
        vegetarian_card = create_menu_card(
            dict(name='Vegetarian card', description='Non meat eaters'),
            dict(food_type=FOOD_TYPE_CHOICES.vegetarian),
            EXAMPLE_VEGETARIAN_DISHES,
        )

    # def test_dishes__list_all_dishes(superadmin_client):
    #     url = reverse(LIST_URL)
    #     response = superadmin_client.get(url)
    #     for item in response.data:
    #         self.assertIn(
    #             item.get('name'),
    #             EXAMPLE_VEGETARIAN_DISHES + EXAMPLE_VEGAN_DISHES,
    #         )
    #
    #     assert response.status_code == status.HTTP_200_OK
    #
    # def test_dishes__get_shows_name_of_menu_card(superadmin_client):
    #     url = reverse(LIST_URL)
    #     response = superadmin_client.get(url)
    #
    #     assert all([item.get('menu_card') for item in response.data])
    #     assert response.status_code == status.HTTP_200_OK
    #
    # def test_dishes__retrieve_single_dish(superadmin_client):
    #     dish_from_db = Dish.objects.only('id').first()
    #     url = reverse('dishes-detail', args=(dish_from_db.id,))
    #     response = superadmin_client.get(url)
    #     assert dish_from_db.id == response.data.get('id')
    #     assert response.status_code == status.HTTP_200_OK
    #
    # def test_dishes__single_dish_creation(superadmin_client):
    #     url = reverse(LIST_URL)
    #     response = superadmin_client.post(
    #         url, data=valid_data_for_dish_creation(), format='json'
    #     )
    #     created_dish = response.data
    #     dish_exists = Dish.objects.filter(id=created_dish.get('id')).exists()
    #
    #     assert dish_exists
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_dishes__dish_creation_error_on_wrong_data(superadmin_client):
    #     url = reverse(LIST_URL)
    #     response = superadmin_client.post(
    #         url, data=invalid_data_for_dish_creation(), format='json'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@pytest.mark.parametrize(
    'field, values, ordered, reverse_ordered',
    [
        (
            'price',
            [1.01, 5.01, 2.01],
            [1.01, 2.01, 5.01],
            [5.01, 2.01, 1.01],
        ),
        (
            'food_type',
            [
                FOOD_TYPE_CHOICES.meat,
                FOOD_TYPE_CHOICES.vegan,
                FOOD_TYPE_CHOICES.meat,
            ],
            [
                FOOD_TYPE_CHOICES.meat,
                FOOD_TYPE_CHOICES.meat,
                FOOD_TYPE_CHOICES.vegan,
            ],
            [
                FOOD_TYPE_CHOICES.vegan,
                FOOD_TYPE_CHOICES.meat,
                FOOD_TYPE_CHOICES.meat,
            ],
        ),
    ],
)
def test_dishes__are_ordered_by_field(
    superadmin_client, field, values, ordered, reverse_ordered
):
    for value in values:
        baker.make(Dish, **{field: value})

    url = reverse(DISHES_LIST_URL)
    response = superadmin_client.get(url, {'ordering': field})
    assert all(
        [
            str(item[field]) == str(expected)
            for item, expected in zip(response.json(), ordered)
        ]
    )
    response = superadmin_client.get(url, {'ordering': f"-{field}"})
    assert all(
        [
            str(item[field]) == str(expected)
            for item, expected in zip(response.json(), reverse_ordered)
        ]
    )


@freezegun.freeze_time(TIMESTAMP)
def test_dishes__patch_updates_timestamps(
    superadmin_client, meat_dish, valid_data_to_update_menu
):

    url = reverse(DISHES_DETAIL_URL, args=(meat_dish.id,))
    response = superadmin_client.patch(
        url,
        data=json.dumps(valid_data_to_update_menu),
        content_type='application/json',
    )

    assert Dish.objects.first().modified == TIMESTAMP
    assert response.status_code == status.HTTP_200_OK
