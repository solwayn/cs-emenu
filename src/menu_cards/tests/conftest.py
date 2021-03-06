import uuid

import pytest
from django.contrib.auth.models import User
from django.test import Client
from faker import Faker
from model_bakery import baker
from PIL import Image
from rest_framework.authtoken.models import Token
from six import BytesIO

from menu_cards.models import FOOD_TYPE_CHOICES, Dish, MenuCard
from seeder.management.commands.seed_db import (EXAMPLE_MEAT_DISHES,
                                                EXAMPLE_VEGAN_DISHES,
                                                EXAMPLE_VEGETARIAN_DISHES)

faker = Faker()
TEST_USERS_NUM = 5


@pytest.fixture
def meat_dish():
    return baker.make(Dish, food_type=FOOD_TYPE_CHOICES.meat)


@pytest.fixture
def vegetarian_dish():
    return baker.make(Dish, food_type=FOOD_TYPE_CHOICES.vegetarian)


@pytest.fixture
def meat_menu():
    return create_menu_card(
        dict(name="Protein", description="meat and more meat"),
        dict(food_type=FOOD_TYPE_CHOICES.meat),
        EXAMPLE_MEAT_DISHES,
    )


@pytest.fixture
def vegan_menu():
    return create_menu_card(
        dict(name="Vegan card", description="for carrots lovers"),
        dict(food_type=FOOD_TYPE_CHOICES.vegan),
        EXAMPLE_VEGAN_DISHES,
    )


@pytest.fixture
def vegetarian_menu():
    return create_menu_card(
        dict(name="Cheese card", description="!MEAT"),
        dict(food_type=FOOD_TYPE_CHOICES.vegetarian),
        EXAMPLE_VEGETARIAN_DISHES,
    )


def create_menu_card(menu_attr=None, dish_attrs=None, dishes_names=None):
    menu_attr = menu_attr or {}
    dish_attrs = dish_attrs or {}
    dishes_names = dishes_names or []
    menu_card = baker.make(MenuCard, **menu_attr)
    for dish in dishes_names:
        baker.make(Dish, name=dish, menu_card=menu_card, **dish_attrs)
    return menu_card


@pytest.fixture
def valid_data_for_dish_creation():
    return {
        "name": "Good Food",
        "description": "100% beef",
        "price": "100.12",
        "prep_time": "00:15:12",
        "food_type": "10",
        "menu_card": "1",
    }


@pytest.fixture
def invalid_data_for_dish_creation():
    return {
        "name": "Good Food",
        "description": "100% beef",
        "food_type": "10",
    }


@pytest.fixture
def valid_data_for_menu_creation():
    return {
        "name": "Best Menu!",
        "description": "Funny description goes here",
        "dishes": [
            {
                "name": "Good Food",
                "description": "100% beef",
                "price": "100.12",
                "prep_time": "00:15:12",
                "food_type": "10",
            },
        ],
    }


@pytest.fixture
def invalid_data_for_menu_creation():
    return {
        "bad_field": "sad menu",
        "description": "It ain't gonna work",
    }


@pytest.fixture
def valid_data_to_update_menu():
    return {
        "name": "New name!",
        "description": "new description",
    }


@pytest.fixture
def valid_data_to_update_dish():
    return {
        "name": "New name!",
        "price": 20.12,
    }


def client():
    return Client()


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs["password"] = test_password
        if "username" not in kwargs:
            kwargs["username"] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def make_superuser(db, django_user_model, test_password):
    user_kwargs = dict(password=test_password, username=str(uuid.uuid4()))
    return django_user_model.objects.create_superuser(**user_kwargs)


@pytest.fixture
def test_password():
    return "strong_password"


@pytest.fixture
def get_token(db, create_user):
    user = create_user()
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def get_superadmin_token(db, make_superuser):
    token, _ = Token.objects.get_or_create(user=make_superuser)
    return token


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def token_client(api_client, get_token):
    token = get_token
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return api_client


@pytest.fixture
def superadmin_client(api_client, get_superadmin_token):
    token = get_superadmin_token
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return api_client


@pytest.fixture
def test_users():
    return [
        baker.make(User, is_superuser=False, **_generate_user_data())
        for _ in range(TEST_USERS_NUM)
    ]


def _generate_user_data():
    return {
        "username": faker.name(),
        "email": faker.email(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
    }


@pytest.fixture
def photo():
    data = BytesIO()
    Image.new("RGB", (100, 100), (255, 255, 255)).save(data, "png")
    data.name = "test.png"
    data.seek(0)
    return data
